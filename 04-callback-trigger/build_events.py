#!/usr/bin/env python3
"""Build event inventories from index v2 and indexed source nodes."""
from collections import Counter, defaultdict
import csv
import functools
from itertools import groupby
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / 'tools'))
os.environ['AUDIT_INDEX_VERSION'] = '2'
from query import connect, lookup, source

CORE = ('Config/ConfigAbility/', 'Config/ConfigGlobalModifier/', 'Config/ConfigGlobalTaskListTemplate/')
RT_MODE = ('Config/Activity/RtBattle/', 'Config/Activity/RtDefence/')
ANIM = 'Config/ConfigAnimEvents/'
GLOBAL_RULES = 'Config/GlobalConfig/GameCoreConstValue.json'
EXACT_TYPES = set("""
AddModifier RemoveModifier RemoveSelfModifier DispelStatus FireProjectile FireWaveProjectile
DamageByAttackProperty DamagePerformFinish ModifyDamageData HealHP InitShield ModifyShield ModifySP
ModifySpecialSP ModifyTeamBoostPoint TurnInsertAbility TurnInsertAction TurnInsertAbilityCondition
AbortInsertAbility PerformDelayExecute WaitSecond WaitAnimState IncludeTaskListTemplate
SetDynamicValueByDamageDataProperty SetDynamicValueByAttackDamageData ByContainsParamFlag
ByCompareNextUnusedInsertAction ByCompareUnusedInsertAbilityCount ByHasInsertAbilityPending
ModifyEnergyPoint RemoveParamFlag AddParamFlag StopBattleEvent SetCurrentSkillResult
""".split())
FILTER_FIELDS = {'Condition', 'Predicate', 'PredicateList', 'PreCheck', 'ActivePredicate', 'CasterFilter',
                 'ParamEntityFilter', 'TargetPredicate', 'TargetFilterList', 'Filter', 'IgnoreIf'}
COUNT_FIELDS = {'MaxNumber', 'Times', 'TriggerCount', 'MaxTriggerCount', 'CountLimit',
                'MaxCount', 'MaxLoopCount', 'Once', 'OnlyOnce', 'CanTriggerOnce', 'LifeTime', 'WorkingTurn'}
CONTROL_FIELDS = COUNT_FIELDS | {'Priority', 'Order', 'Delay', 'DelayTime', 'TickInterval'}
PAYLOAD_FIELDS = {'Alias', 'DamageDataProperty', 'AttackDataProperty', 'ContextScope', 'Flag',
                  'ReadTargetType', 'HealerTargetType', 'TargetType', 'CasterFilter', 'OverrideParamEntity',
                  'AttackerTargetType', 'DefenderTargetType', 'SourceType', 'AbilityTarget', 'TargetAlias',
                  'ReadScope', 'TargetContextScope', 'OwnerTargetType'}
EVENT_ROLES = {'TriggerModifierCustomEvent':'modifier-custom-send', 
               'TriggerParamModifierCustomEvent':'parameter-modifier-custom-send',
               'ByCompareModifierCustomEvent':'modifier-custom-filter',
               'TriggerAnimStateOnModifierCustomEvent':'modifier-custom-animation',
               'TriggerBattleStatisticEvent':'battle-statistic-send',
               'TriggerLittleGameCustomEvent':'little-game-send',
               'WaitLittleGameCustomEvent':'little-game-wait',
               'WaitAnimEvent':'animation-wait', 'ManualTriggerAnimEvent':'animation-explicit-trigger',
               'TriggerModifierEnterBattle':'modifier-enter-battle-request'}
source = functools.lru_cache(maxsize=8)(source)

def out(name, columns, rows):
    with (HERE / f'{name}.tsv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(columns.split())
        writer.writerows(rows)

def j(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True)

def domain(path):
    if path.startswith(CORE):
        return 'core'
    if path.startswith(RT_MODE):
        return 'rt-mode'
    if path.startswith(ANIM):
        return 'animation'
    if path.startswith(('Config/ConfigCharacter/', 'Config/ConfigAI/', 'Config/ConfigSummonUnit/',
                        'Config/ConfigBattlePerform/', 'Config/BattleMode/', 'Config/ConfigChessAbility/',
                        'Story/BattlePerformance/', 'Config/Transition/', 'Config/Level/StageCommon')):
        return 'battle-adjacent'
    return 'other'

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def node_role(typ):
    label = typ.rsplit('.', 1)[-1]
    if re.match(r'^([A-Z]{11}|[A-Z]{12})$', label):
        return 'opaque'
    if label.startswith(('By', 'RtBy', 'VE_', 'VP_')):
        return 'predicate-or-expression'
    if label.startswith(('Target', 'RtTarget')):
        return 'target-query'
    return 'typed-node'

def child_types(value):
    if isinstance(value, list):
        return [node.get('$type', '<untyped>') for node in value if isinstance(node, dict)]
    if isinstance(value, dict):
        return [value.get('$type', '<untyped>')]
    return []

def collect_details(value):
    payload, filters, controls, below = set(), set(), set(), set()
    for obj in walk(value):
        typ = obj.get('$type')
        if isinstance(typ, str):
            role = node_role(typ)
            if role == 'predicate-or-expression':
                filters.add(typ)
            elif role != 'target-query':
                below.add(typ)
        for key, field in obj.items():
            if key in FILTER_FIELDS:
                filters.update(child_types(field))
            if key in CONTROL_FIELDS:
                controls.add(key)
            if key in PAYLOAD_FIELDS:
                snippet = field
                if isinstance(field, dict):
                    snippet = field.get('Alias', field.get('$type', field.get('Value', '<dict>')))
                if isinstance(snippet, (int, str)):
                    payload.add(f'{key}={snippet}')
    return sorted(payload), sorted(filters), sorted(controls), sorted(below)

def selector_lists(db):
    stats = defaultdict(Counter)
    first = {}
    distinct_definitions = defaultdict(set)
    def iter_rows():
        query = """SELECT e.path,e.pointer,e.name,e.anchor,coalesce(d.name,''),d.scope
            FROM event_locations e LEFT JOIN definition_locations d
              ON e.path=d.path AND e.anchor=d.pointer AND d.kind='modifier'
            WHERE e.form='callback-selector' ORDER BY e.path,e.pointer"""
        for path,pointer,name,anchor,defname,scope in db.execute(query):
            root = source(path)
            event = lookup(root,pointer)
            assert str(event) == name
            obj = lookup(root,pointer.rsplit('/',1)[0])
            payload,filters,controls,below = collect_details(obj.get('CallbackConfig', []))
            key = domain(path), type(event).__name__, name
            stats[key]['nodes'] += 1
            if isinstance(obj.get('Priority'), (int,str)):
                stats[key]['priority:'+str(obj['Priority'])] += 1
            for k in obj.keys() - {'CallbackConfig','Event'}:
                stats[key]['field:'+k] += 1
            for p in payload:
                stats[key]['payload:'+p] += 1
            for f in filters:
                stats[key]['filter:'+f] += 1
            for c in controls:
                stats[key]['body_control:'+c] += 1
            for t in child_types(obj.get('CallbackConfig')):
                stats[key]['direct_task:'+t] += 1
            distinct_definitions[key].add((path,anchor))
            first.setdefault(key,(path,pointer))
            declaration = {k:v for k,v in obj.items() if k not in {'CallbackConfig','Event'}}
            namespace = 'modifier-selector' if scope is not None else 'other-selector'
            yield (*key,path,pointer,anchor,defname,namespace,scope,
                   j(declaration),j(payload),j(filters),j(controls),j(child_types(obj.get('CallbackConfig'))),j(below))
    out('callback-sites','domain event_value_shape event path pointer definition_pointer definition_name namespace definition_scope declaration_fields payload_evidence filters nested_control_fields direct_tasks nested_nonquery_types',iter_rows())
    out('callback-catalog','domain event_value_shape event sites definitions evidence_counts example_path example_pointer producer_evidence runtime_dispatch',
        ((*key, val.pop('nodes'), len(distinct_definitions[key]), j(val), *first[key],
         'bounded enter-battle requester candidate' if key[2]=='OnEnterBattle' else 
         'see custom-event-sites.tsv' if key[2]=='OnCustomEvent' else 'Unknown', 'Unknown')
         for key,val in sorted(stats.items())))
    names = defaultdict(set)
    for area,_,name in stats:
        names[area].add(name)
    by_area = Counter(domain(path) for path, in db.execute("SELECT path FROM event_locations WHERE form='callback-selector'"))
    print('callback domains:',dict(by_area), {area:len(n) for area,n in names.items()})
    assert by_area['core'] == 35295 and by_area['rt-mode'] == 601

def hooks(db):
    stats,first = Counter(),{}
    where = " OR ".join("path LIKE '" + p + "%'" for p in CORE + RT_MODE +
                        (ANIM,'Story/BattlePerformance/','Config/Level/StageCommon',GLOBAL_RULES))
    key_types = defaultdict(Counter)
    def iter_rows():
        query = f"""SELECT path,pointer,anchor_kind,anchor,name,form,issuer_type
            FROM event_locations WHERE form IN ('hook','container') AND ({where})
            ORDER BY path,pointer,form"""
        for path,pointer,anchor_kind,anchor,name,form,issuer in db.execute(query):
            obj = lookup(source(path),pointer)
            assert isinstance(obj,(list,dict)), (path,pointer)
            key = domain(path),anchor_kind,form,name
            c_types = child_types(obj)
            stats[key] += 1
            first.setdefault(key,(path,pointer,issuer))
            key_types[key].update(c_types)
            pos = anchor and pointer[len(anchor):].count('/') if anchor else 0
            parent = lookup(source(path),pointer.rsplit('/',1)[0])
            options = {}
            if name == 'OnChange' and isinstance(parent,dict):
                options = {k:v for k,v in parent.items() if k != name and not isinstance(v,list)}
            yield (*key,path,pointer,anchor,issuer,type(obj).__name__,pos,j(c_types),j(options))
    out('hook-sites','domain anchor_kind form hook path pointer anchor_pointer issuer_type shape relative_depth direct_typed_members range_fields',iter_rows())
    out('hook-catalog','domain anchor_kind form hook sites direct_member_counts example_path example_pointer example_issuer',
        ((*key,n,j(key_types[key]),*first[key]) for key,n in sorted(stats.items())))
    print('hook/container roles:',sum(stats.values()),len(stats))

def typed_roles(db):
    values = db.execute("SELECT type, occurrences FROM type_counts ORDER BY type").fetchall()
    picked = [t for t,n in values if re.search(r'Trigger|CallBack|Callback|Event|Listen',t.rsplit('.',1)[-1])
              or t.rsplit('.',1)[-1] in EXACT_TYPES]
    counts,examples = defaultdict(Counter),{}
    names = sorted(set(picked))
    sql = f"""SELECT path,pointer,type,parent_field,parent_type,anchor_kind FROM occurrences
           WHERE type IN ({','.join('?' for t in names)}) GROUP BY path,pointer,type ORDER BY type,path,pointer"""
    for path,pointer,typ,parent,parent_type,anchor_kind in db.execute(sql,names):
        area = domain(path)
        counts[typ][area] += 1
        examples.setdefault((typ,area),(path,pointer,parent,parent_type,anchor_kind))
    count_map = dict(values)
    def rows():
        for typ in sorted(counts):
            areas = counts[typ]
            label = typ.rsplit('.',1)[-1]
            area = next((area for area in ('core','rt-mode','animation','battle-adjacent','other') if area in areas))
            inferred_label = EVENT_ROLES.get(label)
            assert sum(areas.values()) == count_map[typ], (typ, areas)
            yield typ,count_map[typ],j(areas),inferred_label or 'review-by-config-position',*examples[typ,area]
    out('trigger-type-candidates','type total domain_counts structural_label example_path example_pointer parent_field parent_type anchor_kind',rows())
    print('typed event/trigger review candidates:',len(counts))

def named_events(db):
    named_shapes = defaultdict(Counter)
    examples = {}
    def iter_rows():
        for path,pointer,name,form,anchor,kind,issuer in db.execute("""SELECT * FROM event_locations
                WHERE form IN ('animation-state','animation-group-record','animation-record','named-event-field','event-type-field')
                ORDER BY path,pointer,form"""):
            area = domain(path)
            if form == 'named-event-field' and area=='other':
                continue
            val = lookup(source(path),pointer)
            assert (val == name or form=='animation-group-record' or form=='event-type-field' and json.loads(name)==val)
            parent = lookup(source(path),pointer.rsplit('/',1)[0]) if form!='animation-group-record' else val
            controls = {k:v for k,v in parent.items() if k in
                        {'Time','NormalizedTime','AnimStateName','AnimatorStateName','DefaultTarget','EventType',
                         'Owner','Priority','DynamicKey','Value','TargetType','OverrideParamEntity','MaxNumber','PreCheck','AnimLogicState'}}
            options = {k:child_types(v) for k,v in parent.items() if k in {'EventList','OnEnter','OnExit','OnUpdate','OnStart'}}
            key = area,form,name,issuer
            named_shapes[key]['nodes'] += 1
            named_shapes[key].update(controls.keys())
            examples.setdefault(key,(path,pointer))
            yield (*key,path,pointer,anchor,kind,j(controls),j(options))
    out('named-event-sites','domain form value issuer_type path pointer anchor_pointer anchor_kind nearby_fields child_event_tasks',iter_rows())
    out('named-event-catalog','domain form value issuer_type sites nearby_field_counts example_path example_pointer',
        ((*key,val.pop('nodes'),j(val),*examples[key]) for key,val in sorted(named_shapes.items())))
    print('named/animation/token catalog entries:',len(named_shapes))

def cross_link(db):
    requests = defaultdict(list)
    listeners = defaultdict(list)
    types = ('TriggerModifierCustomEvent','TriggerParamModifierCustomEvent','ByCompareModifierCustomEvent','TriggerAnimStateOnModifierCustomEvent')
    for path,pointer,name,form,anchor,kind,issuer in db.execute("SELECT * FROM event_locations WHERE form='event-type-field' ORDER BY path,pointer"):
        label = issuer.rsplit('.',1)[-1]
        if label not in types:
            continue
        node = lookup(source(path),pointer.rsplit('/',1)[0])
        token = node['EventType']
        key = (token.get('EnumIndex',''), token.get('Value',''))
        selector = ''
        p = pointer.split('/CallbackConfig/',1)[0]
        if p != pointer:
            selector = lookup(source(path),p).get('Event','')
        row = (label,path,pointer,selector,anchor,j({k:v for k,v in node.items() if k not in {'$type','EventType'}}))
        (requests if label.startswith('Trigger') and label!='TriggerAnimStateOnModifierCustomEvent' else listeners)[key].append(row)
    rules = source(GLOBAL_RULES)
    declarations = {}
    for index, rule in enumerate(rules['ModifierCustomEvents']):
        key = (rule['EventType']['EnumIndex'], rule['EventType']['Value'])
        assert key not in declarations
        declarations[key] = f'/ModifierCustomEvents/{index}', rule
    all_keys = sorted(requests.keys() | listeners.keys() | declarations.keys())
    out('custom-event-sites','enum_index value role path pointer nearest_callback_selector anchor_pointer neighboring_fields',
        ((*key,*row) for key in all_keys for row in requests.get(key,[]) + listeners.get(key,[])))
    links = []
    for key in all_keys:
        sent = requests.get(key,[])
        observed = listeners.get(key,[])
        where, rule = declarations.get(key,('',{}))
        links.append((*key,len(sent),len(observed),len(sent)*len(observed),
            j(sent[0][:4] if sent else []),j(observed[0][:4] if observed else []),
            'equal-tuple-candidate' if sent and observed else 'producer-only' if sent else
            'consumer-only' if observed else 'declaration-only',where,
            j(rule.get('BehaviorFlags',[])),rule.get('SortBy','')))
    out('custom-event-links','enum_index value producer_sites consumer_candidate_sites candidate_equal_tuple_pairs first_producer first_consumer status global_declaration_pointer global_behavior_flags global_sortby',links)
    print('custom event tuples declared/sent/consumer/mixed:',len(declarations),len(requests),len(listeners),
          len(requests.keys() & listeners.keys()))

def global_policies():
    root = source(GLOBAL_RULES)
    for key in ['ForbidRecallModifierEventList', 'ServantModifierEventWhiteList']:
        assert isinstance(root[key],list)
    data = [(GLOBAL_RULES,'/'+key,j(root[key])) for key in (
        'ForbidRecallModifierEventList','ServantModifierEventWhiteList','ModifierBehaviorFlagEventMap')]
    out('global-event-policies','path pointer value',data)

def animation_links(db):
    events = defaultdict(list)
    for path,pointer,name,form,anchor,kind,issuer in db.execute("SELECT * FROM event_locations WHERE form='animation-record' ORDER BY path,pointer"):
        events[name].append((path,pointer))
    rows = []
    for path,pointer,anchor in db.execute("""SELECT path,pointer,anchor FROM occurrences 
          WHERE type='RPG.GameCore.WaitAnimEvent' ORDER BY path,pointer"""):
        node = lookup(source(path),pointer)
        ability = lookup(source(path),anchor)['Name']
        characters = [x[0] for x in db.execute("""SELECT DISTINCT path FROM reference_locations WHERE kind='ability'
           AND name=? AND path LIKE 'Config/ConfigCharacter/%' ORDER BY path""",(ability,))]
        linked=[]
        for character in characters:
            char = source(character)
            for asset,p in events[node.get('EventName')]:
                for i,item in enumerate(char.get('AnimEventConfigList',[])):
                    if item==asset:
                        linked.append([character,f'/AnimEventConfigList/{i}',asset,p])
        status='explicit-character-import' if linked else 'name-only' if events[node.get('EventName')] else 'unresolved'
        rows.append((path,pointer,ability,node.get('EventName'),status,j(linked),j(events[node.get('EventName')]),j(characters)))
    out('animation-wait-links','wait_path wait_pointer ability_name event_name status explicit_character_imports matching_named_records character_candidates',rows)
    print('animation waits:', dict(Counter(x[4] for x in rows)))

def main():
    with connect() as db:
        assert db.execute('PRAGMA user_version').fetchone() == (2,)
        selector_lists(db)
        hooks(db)
        typed_roles(db)
        named_events(db)
        cross_link(db)
        global_policies()
        animation_links(db)

if __name__ == '__main__':
    main()
