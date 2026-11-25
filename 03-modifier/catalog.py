#!/usr/bin/env python3
"""Regenerate stage 03 evidence tables from the shared v1 index and relevant JSON."""
from collections import Counter, defaultdict
import csv
from itertools import groupby
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from query import connect, lookup, source

CORE = "path LIKE 'Config/ConfigAbility/%' OR path LIKE 'Config/ConfigGlobalModifier/%'"
MODE = "path LIKE 'Config/Activity/RtBattle/%' OR path LIKE 'Config/Activity/RtDefence/%'"
STATUS_FIELDS = {'Stacking', 'LifeStepMoment', 'BehaviorFlagList', 'UseSnapshotEntity',
                 'LifeTime', 'Count', 'WorkingTurn', 'MaxLayer', 'LayerAddWhenStack',
                 'Priority', 'TargetSelectRestrictType', 'UIConfig'}
EXPLICIT = {
    'AddModifier': 'named-add', 'RemoveModifier': 'named-remove',
    'RemoveSelfModifier': 'context-remove', 'RemoveModifierByBehaviorFlag': 'flag-remove',
    'DispelStatus': 'dispel', 'InfectModifier': 'transfer', 'Remodifier': 'context-selection',
    'SetModifierValue': 'value-write', 'SetModifierDynamicValue': 'dynamic-value-write',
    'SetDynamicValueByModifierValue': 'value-read', 'ByIsContainModifier': 'presence-test',
    'ByCompareModifierValue': 'value-test', 'StackProperty': 'property-write',
    'TriggerModifierCustomEvent': 'event-request', 'AbortModifierPhasePerform': 'phase-control',
    'TriggerModifierEnterBattle': 'event-request', 'TriggerModifierLeaveBattle': 'event-request',
    'RtStackProperty': 'rt-property-write', 'StackStatusDesc': 'status-description',
    'StackStatusResistance': 'status-resistance', 'StackStatusProbability': 'status-probability',
    'AGPMEJILJBO': 'rt-named-add-candidate',
}

def compact(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def write(name, headers, rows):
    with (HERE / (name + '.tsv')).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(headers)
        writer.writerows(rows)

def child(ptr, key):
    return ptr + '/' + str(key).replace('~', '~0').replace('/', '~1')

def mode_definitions(root):
    if not isinstance(root, dict):
        return
    groups = [('GlobalModifiers', '/GlobalModifiers', '', root.get('GlobalModifiers')),
              ('ModifierMap', '/ModifierMap', '', root.get('ModifierMap'))]
    for i, ability in enumerate(root.get('AbilityList', [])):
        if isinstance(ability, dict):
            groups.append(('ability-local', f'/AbilityList/{i}/Modifiers',
                           ability.get('Name', ''), ability.get('Modifiers')))
    for scope, prefix, owner, members in groups:
        if isinstance(members, dict):
            for name, node in members.items():
                if isinstance(node, dict):
                    yield child(prefix, name), scope, owner, name, node

def tree(obj, ptr=''):
    yield ptr, obj
    if isinstance(obj, dict):
        members = obj.items()
    elif isinstance(obj, list):
        members = enumerate(obj)
    else:
        return
    for key, val in members:
        if isinstance(val, (dict, list)):
            yield from tree(val, child(ptr, key))

def collect(db):
    definitions = []
    counts = Counter()
    shapes = Counter()
    locations = {}
    values = Counter()
    callbacks = Counter()
    callback_locations = {}
    mode_refs = []
    mode_defs = defaultdict(list)
    mode_positions = {}
    mode_types = defaultdict(list)
    addition_refs = []
    core_defs = defaultdict(list)

    def consume(domain, path, ptr, scope, owner, name, node):
        counts[(domain, scope)] += 1
        if domain == 'core':
            core_defs[name].append((path, ptr, scope))
        addition = node.get('AdditionConfig', {})
        if isinstance(addition, dict):
            for index, child_modifier in enumerate(addition.get('SubModifierList', [])):
                if not isinstance(child_modifier, dict) or not isinstance(child_modifier.get('Name'), str):
                    continue
                loc = f'{ptr}/AdditionConfig/SubModifierList/{index}/Name'
                addition_refs.append((domain, path, loc, ptr, child_modifier))
        declared_callbacks = []
        for index, event in enumerate(node.get('_CallbackList', [])):
            if isinstance(event, dict) and isinstance(event.get('Event'), (str, int)):
                label = event['Event']
                declared_callbacks.append(label)
                key = (domain, type(label).__name__, str(label))
                callbacks[key] += 1
                callback_locations.setdefault(key, (path, f'{ptr}/_CallbackList/{index}/Event'))
        definitions.append((domain, scope, path, ptr, owner, name,
                            compact(sorted(node)), compact(declared_callbacks)))
        for field, value in node.items():
            shape_key = (domain, field, type(value).__name__)
            shapes[shape_key] += 1
            locations.setdefault(shape_key, (path, child(ptr, field)))
            if field in STATUS_FIELDS:
                options = value if field == 'BehaviorFlagList' and isinstance(value, list) else [value]
                for option in options:
                    values[domain, field, compact(option)] += 1

    indexed = db.execute(f"""SELECT path,pointer,scope,name,keys_json FROM definition_locations
                        WHERE kind='modifier' AND ({CORE}) ORDER BY path,pointer""")
    for path, rows in groupby(indexed, key=lambda row: row[0]):
        data = source(path)
        for _, ptr, scope, name, keys in rows:
            node = lookup(data, ptr)
            assert sorted(node) == json.loads(keys), (path, ptr)
            owner = lookup(data, scope)['Name'] if scope.startswith('/') else ''
            consume('core', path, ptr, 'ability-local' if scope.startswith('/') else scope, owner, name, node)
    for path, in db.execute(f"SELECT path FROM files WHERE status='parsed' AND ({MODE}) ORDER BY path"):
        data = source(path)
        for ptr, scope, owner, name, node in mode_definitions(data):
            mode_defs[name].append((path, ptr, scope))
            mode_positions[path, ptr] = name
            consume('rt-mode', path, ptr, scope, owner, name, node)
        if not isinstance(data, dict) or not {'AbilityList', 'ModifierMap', 'GlobalModifiers'}.intersection(data):
            continue
        for ptr, node in tree(data):
            if not isinstance(node, dict):
                continue
            kind = node.get('$type')
            if not isinstance(kind, str) or 'IFNAGLOMHBK' not in node:
                continue
            mode_types[kind].append((path, ptr))
            raw = node['IFNAGLOMHBK']
            if isinstance(raw, dict):
                name, loc = raw.get('Value'), ptr + '/IFNAGLOMHBK/Value'
            else:
                name, loc = raw, ptr + '/IFNAGLOMHBK'
            if isinstance(name, str) and name:
                mode_refs.append((path, loc, name, 'IFNAGLOMHBK', kind, ptr))
    write('definitions', ('domain','scope','path','pointer','owner_ability','name','fields','callback_events'), definitions)
    write('definition-fields', ('domain','field','value_shape','definitions','example_path','example_pointer'),
          ((*key, count, *locations[key]) for key, count in sorted(shapes.items())))
    write('policy-values', ('domain','field','serialized_value','occurrences'),
          ((*key, count) for key, count in sorted(values.items())))
    write('callback-selectors', ('domain','value_shape','event','occurrences','example_path','example_pointer'),
          ((*key, count, *callback_locations[key]) for key, count in sorted(callbacks.items())))
    relinked = []
    for path, loc, name, field, kind, task in mode_refs:
        candidates = mode_defs.get(name, [])
        local = [x for x in candidates if x[0] == path and x[2] == 'ability-local'
                 and task.startswith(x[1].split('/Modifiers/', 1)[0] + '/')]
        same = [x for x in candidates if x[0] == path and x[2] != 'ability-local']
        selected = local or same
        if len(selected) == 1:
            status, target = 'scoped', selected[0]
        elif len(candidates) == 1:
            status, target = 'candidate', candidates[0]
        elif candidates:
            status, target = 'ambiguous', ('', '', '')
        else:
            status, target = 'unresolved', ('', '', '')
        ancestors = task.split('/')
        anchor = ''
        for i in range(len(ancestors), 0, -1):
            test = '/'.join(ancestors[:i])
            if (path, test) in mode_positions:
                anchor = test
                break
        relinked.append((path,loc,name,field,kind,anchor,status,len(candidates),target[0],target[1]))
    write('rt-symbol-candidates', ('path','pointer','name','field','type','modifier_anchor','status','candidates','def_path','def_pointer'), relinked)
    submodifier_links = []
    for domain, path, loc, anchor, node in addition_refs:
        name = node['Name']
        candidate_map = core_defs if domain == 'core' else mode_defs
        candidates = candidate_map.get(name, [])
        local = [x for x in candidates if x[0] == path and x[2] == 'ability-local'
                 and anchor.startswith(x[1].split('/Modifiers/', 1)[0] + '/')]
        same = [x for x in candidates if x[0] == path and x[2] != 'ability-local']
        selected = local or same
        if len(selected) == 1:
            status, dest = 'scoped', selected[0]
        elif len(candidates) == 1:
            status, dest = 'candidate', candidates[0]
        elif candidates:
            status, dest = 'ambiguous', ('', '', '')
        else:
            status, dest = 'unresolved', ('', '', '')
        submodifier_links.append((domain, path, loc, anchor, name, status, len(candidates),
                                  dest[0], dest[1], compact(node)))
    write('addition-candidates', ('domain','path','pointer','modifier_anchor','name','status',
                                  'candidates','def_path','def_pointer','entry'), submodifier_links)
    core = sum(count for (key, _), count in counts.items() if key == 'core')
    public_core, = db.execute(f"SELECT count(*) FROM definition_locations WHERE kind='modifier' AND ({CORE})").fetchone()
    assert core == public_core
    print('definitions:', dict(sorted(counts.items())))
    print('direct field identities:', {d: len({field for dom,field,_ in shapes if dom==d}) for d in {'core','rt-mode'}})
    print('UIConfig:', {d: sum(n for (dom,f,_),n in shapes.items() if dom==d and f=='UIConfig') for d in {'core','rt-mode'}})
    print('empty UIConfig:', {d: values[d,'UIConfig','{}'] for d in {'core','rt-mode'}})
    print('callback selectors:', {d: (sum(n for (dom,_,_),n in callbacks.items() if dom==d),sum(dom==d for dom,_,_ in callbacks)) for d in {'core','rt-mode'}})
    print('rt-symbols:', len(relinked), dict(Counter(row[6] for row in relinked)))
    print('declarative submodifiers:', len(submodifier_links),
          dict(Counter((row[0], row[5]) for row in submodifier_links)))
    return mode_types

def refs(db, mode_types):
    schema = ('path','pointer','kind','name','field','parent_type','anchor','anchor_kind',
              'status','candidate_count','def_path','def_pointer')
    base = 'SELECT ' + ','.join(schema) + ' FROM reference_locations'
    all_refs = base + " WHERE kind='modifier' ORDER BY path,pointer"
    write('references', schema, db.execute(all_refs))
    write('unresolved-or-ambiguous', schema,
          db.execute(base + " WHERE kind='modifier' AND status IN ('unresolved','ambiguous') ORDER BY path,pointer"))
    graph = list(db.execute(base + """ WHERE (anchor_kind IN ('ability','modifier') AND kind='modifier')
                             OR (anchor_kind='modifier' AND kind='ability') ORDER BY path,pointer"""))
    write('graph', schema, graph)
    src = Counter((row[7], row[2], row[8]) for row in graph)
    assert sum(src.values()) == len(graph)
    lifecycle_edges = {(row[0], row[6], row[11], row[5].split('.')[-1]) for row in graph
                       if row[7]=='modifier' and row[2]=='modifier' and row[8]=='scoped'
                       and row[5].split('.')[-1] in ('AddModifier','RemoveModifier') and row[0]==row[10]}
    self_edges = sorted(row for row in lifecycle_edges if row[1]==row[2])
    mutual = sorted(row for row in lifecycle_edges if row[1]<row[2] and
                    any((row[0],row[2],row[1],step) in lifecycle_edges for step in ('AddModifier','RemoveModifier')))
    write('feedback-examples', ('path','source','target','operation'),
          self_edges + mutual)
    print('graph edges:', len(graph), dict(sorted(src.items())))
    print('unique self / reciprocal static lifecycle links:', len(self_edges), len(mutual))
    print('public modifier reference statuses:',
          db.execute("SELECT status,count(*) FROM reference_locations WHERE kind='modifier' GROUP BY status ORDER BY status").fetchall())

    pattern = re.compile(r'Modifier|DispelStatus')
    found = []
    all_fields = []
    for typ, n, file_count in db.execute("SELECT type,occurrences,files FROM type_counts ORDER BY type"):
        short = typ.rsplit('.',1)[-1]
        if not (short in EXPLICIT or pattern.search(short) or typ in mode_types):
            continue
        role = EXPLICIT.get(short, 'rt-symbol-field' if typ in mode_types else 'name-matched-candidate')
        locations = db.execute('SELECT path,pointer FROM occurrences WHERE type=? ORDER BY path,pointer LIMIT 2',
                               (typ,)).fetchall()
        found.append((typ, role, n, file_count, compact(locations), len(mode_types.get(typ, []))))
        all_fields.extend(db.execute('SELECT type,field,shape,count FROM fields WHERE type=? ORDER BY field,shape', (typ,)))
    write('entry-types', ('type','role','full_corpus_nodes','files','first_locations','rt_symbol_nodes'), found)
    write('entry-fields', ('type','field','shape','occurrences'), all_fields)
    print('candidate / explicit types in entry inventory:', len(found))

if __name__ == '__main__':
    with connect() as db:
        refs(db, collect(db))
