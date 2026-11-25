#!/usr/bin/env python3
"""Build the task-role catalogue from the shared index and selected JSON nodes."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from query import connect, lookup, source

ARRAY_SLOTS = set("""
OnStart OnAdd OnRemove OnInsertAbort CallbackConfig TaskList SuccessTaskList
FailedTaskList OnChange OnEnterRange OnBattleEventCreate OnProjectileHit
PerformTaskList OnBeforeCreateCallback OnExitRange OnMonsterCreate
DefaultTaskList OnSelect OnDynamicEquipmentTrigger OnSuccess OnNoNewWeak
FailTaskList OnTopDamagerRoleChanged OnServantCreate OnNewAvatarRefresh
OnNewAvatarCreate OnInit OnTick OnBattleProgressChanged OnProjectileHitClientOnly
OnSucceed OnUIClick ResistedTaskList OnUICustomEvent OnReplace OnBeginPlay
PerformSequence OnCreate OnDestroy OnShow OnHide OnBeReplaced OnAcceptMoney
OnGroundInvalid OnSummonerGroundMove OnEvent OnPerformFinish OnBeforeBattle
OnAttack OnHit OnAbort OnFail OnFinish OnHitWall OnBeAttack OnSucc
OnBattle OnProjectileLifetimeFinish EventList OnEnter OnExit OnActive OnDeactive
OnBeforeEnterBattle OnAfterEnterBattle CameraFocusChangeAction UltraBeginAction UltraEndAction
""".split())
SINGLE_SLOTS = {'Task', 'DefaultTask', 'RootTask', 'PerProjectileDamage', 'OnDisable'}
ALIASED_SLOTS = set('OMFLDIGGPHC CABHEAGLNDD NKCKAJPAJCJ DNCFBGANPCD BKNDLCGHANK ELGMGKGMCCM MAONBNHOPBJ KBCHNLAAKLL CEIJOJNNGGL'.split())
CORE = (
    'Config/ConfigAbility/', 'Config/ConfigGlobalModifier/', 'Config/ConfigGlobalTaskListTemplate/',
    'Config/Activity/RtBattle/', 'Config/Activity/RtDefence/',
)
ADJACENT = (
    'Config/ConfigAI/', 'Config/ConfigAnimEvents/', 'Config/ConfigSummonUnit/',
    'Config/ConfigBattlePerform/', 'Config/ConfigCharacter/', 'Config/BattleMode/',
    'Story/BattlePerformance/',
)
SPECIAL = (
    ('Config/Gameplays/LittleGame/DiceCombat/', ('DiceCombatTaskConfig_',)),
    ('Config/Gameplays/ChenLingBattle/', ('ChenLingBattleEffect_', 'ChenLingBattleAbility')),
    ('Config/Gameplays/PixAir/', ('LittleGameAbilityPixAirEffect', 'LittleGameAbilityEffect')),
    ('Config/ConfigChessAbility/', ('Chess',)),
)

FAMILIES = [
    ('目标查询候选', r'^(Target|RtTarget|FindTarget|GetTarget)'),
    ('判定／表达式候选', r'^(By[A-Z]|RtBy|VE_|VP_|Compare|Check|Calc|Is[A-Z])'),
    ('分支／遍历候选', r'(PredicateTask|SwitchCase|ForEach|^Retarget$|SequenceConfig|Repeat|Loop|ScopeTask|ParallelTask|^MakeSuccess$)'),
    ('资源与支付候选', r'(SkillPoint|Energy|ModifySP|ModifyBP|CostBP|CostSP|ConsumeSP|Refund|ElationPoint)'),
    ('变量与数据候选', r'(DynamicValue|DynamicString|CustomValue|CustomString|Snapshot|Blackboard|CustomData|CopyParam|DynamicEntity)'),
    ('能力请求／调度候选', r'(Ability|SkillMapping|InsertAction|ExtraTurn|ActionDelay|DelayAction|^Wait|ActImmediately|TurnState|Timeline|TurnControl)'),
    ('召唤／实体候选', r'(Summon|Servant|CreateBattleEvent|RemoveBattleEvent|CreateEntity|DeleteEntity|ForceKill|Revive|Unstage|Limbo|StageEntity)'),
    ('生命／伤害／护盾候选', r'(Damage|Shield|Heal|LoseHP|SetHP|ModifyHP|^Attack|^Hit|^FireProjectile)'),
    ('韧性／弱点候选', r'(Stance|Weakness|StackWeak|BreakState|^TriggerBreak)'),
    ('Modifier／事件候选', r'(Modifier|Status|BehaviorFlag|Event|Callback|Buff|Debuff)'),
    ('属性修正候选', r'(Property|Aggro|Resistance|PropertyOverride)'),
    ('动画／表现／UI 候选', r'(Camera|Anim|Effect|Sound|Audio|Perform|Cutin|CutIn|BGM|Model|FloatMessage|^UI|^Show|^Hide|Visibility|Visual|^Debug|^Play|^Screen|^Move|^LookAt)'),
]

def short(typ):
    return typ.rsplit('.', 1)[-1]

def load_notes():
    with (HERE / 'semantic-notes.tsv').open(encoding='utf-8') as handle:
        return {row['type']: row for row in csv.DictReader(handle, delimiter='\t')}

def label(typ, notes):
    if typ in notes:
        return notes[typ]['category'], notes[typ]['grade'], notes[typ]['configured_role']
    if re.fullmatch(r'[A-Z]{11}', typ):
        return '不透明标识', 'Unknown', '见字段和任务槽证据'
    for label, pattern in FAMILIES:
        if re.search(pattern, short(typ)):
            return label, 'Unknown', '候选标签仅用于检索'
    return '其他或未分类', 'Unknown', '见字段和任务槽证据'

def role(path, typ, parent, in_array, anchor_kind):
    # Obfuscated and variant slots are explicitly evidenced in report.md.
    slot = (in_array and parent in ARRAY_SLOTS | ALIASED_SLOTS
            or not in_array and parent in SINGLE_SLOTS)
    if slot and (path.startswith(CORE) or anchor_kind in {'ability', 'modifier', 'template'}):
        return 'core'
    if slot and path.startswith(ADJACENT):
        return 'adjacent'
    if slot and re.search(r'(?i)/(?:StageBgTalk_|StageBattle|BattleStage|BattlePerform)', path):
        return 'adjacent'
    for prefix, prefixes in SPECIAL:
        if path.startswith(prefix) and (slot or any(short(typ).startswith(p) for p in prefixes)):
            return 'special'
    return 'review' if slot else ''

def write_tsv(name, headings, rows):
    with (HERE / name).open('w', encoding='utf-8', newline='') as handle:
        out = csv.writer(handle, delimiter='\t', lineterminator='\n')
        out.writerow(headings)
        out.writerows(rows)

def fmt(counter):
    return json.dumps(dict(sorted(counter.items())), ensure_ascii=False, separators=(',', ':'))

def shape(value):
    return 'null' if value is None else type(value).__name__

def value_form(v):
    if isinstance(v, dict):
        if isinstance(v.get('Alias'), str):
            return '@' + v['Alias']
        if isinstance(v.get('$type'), str):
            return v['$type']
        return '{' + ','.join(sorted(v)) + '}'
    if isinstance(v, list):
        return '[' + ','.join(sorted({value_form(i) for i in v})) + ']'
    return str(v)

def observed_fields(node, counters):
    for field, value in node.items():
        counters['fields'][field + ':' + shape(value)] += 1
        if field != '$type':
            counters['inputs'][field] += 1
        if re.search(r'(?:Target|Owner|Caster|Summoner|Source|Receiver)', field):
            counters['targets'][field + '=' + value_form(value)] += 1
        if field in {'ContextScope', 'DamageDataProperty', 'ActorRole', 'ContextType', 'ReadScope', 'WriteScope'}:
            counters['contexts'][field + '=' + value_form(value)] += 1
        if re.search(r'(?:(?:Ability|Modifier)(?:Name|NameList|Names)?$|TaskListTemplate|Event(?:Name|Type)$|Callback)', field):
            counters['link_fields'][field] += 1

def sample_families(path):
    if path.startswith('Config/ConfigAbility/'):
        return '/'.join(path.split('/')[:3])
    return '/'.join(path.split('/')[:2])

def dump_evidence(node, keys):
    fragment = {k: node[k] for k in ['$type', *keys] if k in node}
    for key, value in list(fragment.items()):
        if isinstance(value, list) and all(isinstance(member, dict) for member in value):
            fragment[key] = [{'$type': member['$type']} if '$type' in member else
                             {subkey: member[subkey] for subkey in list(member)[:3]}
                             for member in value[:3]]
        elif isinstance(value, dict) and len(value) > 8:
            fragment[key] = {subkey: value[subkey] for subkey in list(value)[:8]}
    return json.dumps(fragment, ensure_ascii=False, separators=(',', ':'))

def template_link(path, loc, name, definitions):
    found = definitions.get(name, [])
    local = []
    for target_path, target_pointer in found:
        container = re.split('/(?:TaskListTemplate|GlobalTemplates)/', target_pointer, maxsplit=1)[0]
        if path == target_path and (not container or loc.startswith(container + '/')):
            local.append((len(container), target_path, target_pointer))
    if local:
        nearest = max(row[0] for row in local)
        visible = [row[1:] for row in local if row[0] == nearest]
        if len(visible) == 1:
            return 'scoped', len(found), *visible[0]
    if len(found) == 1:
        return 'candidate', 1, *found[0]
    return ('ambiguous' if found else 'unresolved'), len(found), '', ''

def catalogue():
    notes = load_notes()
    selected = defaultdict(list)
    counts = defaultdict(Counter)
    review = {}
    placeholders = ','.join('?' for _ in ARRAY_SLOTS | ALIASED_SLOTS | SINGLE_SLOTS)
    with connect() as db:
        totals = dict(db.execute('SELECT type,occurrences FROM type_counts'))
        template_defs = defaultdict(list)
        for name, path, loc in db.execute(
            "SELECT name,path,pointer FROM definition_locations WHERE kind='template'"
        ):
            template_defs[name].append((path, loc))
        statement = f"""SELECT path,pointer,type,parent_field,parent_type,in_array,anchor,anchor_kind
            FROM occurrences
            WHERE parent_field IN ({placeholders})
               OR path LIKE 'Config/Gameplays/LittleGame/DiceCombat/%'
               OR path LIKE 'Config/Gameplays/ChenLingBattle/%'
               OR path LIKE 'Config/Gameplays/PixAir/%'
               OR path LIKE 'Config/ConfigChessAbility/%'
            ORDER BY path,pointer"""
        for path, loc, typ, parent, parent_type, array, anchor, ak in db.execute(
            statement, sorted(ARRAY_SLOTS | ALIASED_SLOTS | SINGLE_SLOTS)
        ):
            status = role(path, typ, parent, array, ak)
            if status == 'review':
                key = typ, parent, sample_families(path)
                counts['review', key]['n'] += 1
                if key not in review:
                    review[key] = path, loc
            elif status:
                selected[path].append((loc, typ, status, parent, parent_type, anchor, ak))

        refs = Counter()
        selected_types = {path: {row[0]: row[1] for row in entries} for path, entries in selected.items()}
        for path, loc, kind, field, status in db.execute(
            "SELECT path,pointer,kind,field,status FROM reference_locations WHERE kind IN ('ability','modifier','template')"
        ):
            if path not in selected_types:
                continue
            parts = loc.split('/')
            for i in range(len(parts) - 1, 0, -1):
                op = selected_types[path].get('/'.join(parts[:i]))
                if op:
                    refs[op, kind, field, status] += 1
                    break
        write_tsv('symbol-links.tsv', ['type', 'kind', 'field', 'static_status', 'count'],
                  ((*key, count) for key, count in sorted(refs.items())))
        data_roles = """WITH selected AS (
                SELECT type,
                       CASE WHEN parent_field IN ('TargetType','ReadTargetType','AbilityTarget','Sequence','SortSequence','Targets')
                                AND (type LIKE '%.Target%' OR type LIKE '%.RtTarget%' OR parent_type LIKE '%.Target%')
                              THEN 'target'
                            WHEN parent_field IN ('Predicate','PredicateList') THEN 'predicate'
                            WHEN type LIKE '%.VE_%' OR type LIKE '%.VP_%' THEN 'expression'
                            ELSE '' END role,
                       path,pointer
                FROM occurrences
                WHERE anchor_kind IN ('ability','modifier','template','alias')
                   OR path LIKE 'Config/Activity/RtBattle/%'
                   OR path LIKE 'Config/Activity/RtDefence/%'
            )
            SELECT role,type,count(*),min(path || char(9) || pointer) example
            FROM selected WHERE role<>'' GROUP BY 1,2 ORDER BY 1,2"""
        write_tsv('supporting-types.tsv', ['role', 'type', 'count', 'example_path', 'example_pointer'],
                  ((*row[:3], *row[3].split('\t', 1)) for row in db.execute(data_roles)))

    detail = defaultdict(lambda: defaultdict(Counter))
    examples = defaultdict(list)
    template_refs = []
    for path, entries in selected.items():
        obj = source(path)
        index_by_path = {row[0]: row for row in entries}
        children = defaultdict(list)
        for row in entries:
            loc, typ, *_ = row
            candidates = loc.split('/')
            for i in range(len(candidates) - 1, 0, -1):
                ancestor = '/'.join(candidates[:i])
                if ancestor in index_by_path:
                    children[ancestor].append((candidates[i], typ))
                    break
        for loc, typ, status, parent, parent_type, anchor, ak in entries:
            node = lookup(obj, loc)
            assert node['$type'] == typ, (path, loc, typ)
            result = detail[typ]
            result['level'][status] += 1
            result['slots'][parent] += 1
            result['placement'][status + '|' + parent + '|' + (parent_type or '<struct>') + '|' + (ak or '<root/supplement>')] += 1
            result['families'][sample_families(path)] += 1
            observed_fields(node, result)
            if typ == 'RPG.GameCore.IncludeTaskListTemplate' and isinstance(node.get('Name'), str):
                name = node['Name']
                template_refs.append((path, loc + '/Name', name, *template_link(path, loc, name, template_defs)))
            signature = '|'.join(sorted(node))
            result['signature'][signature] += 1
            for slot_name, child_type in set(children[loc]):
                result['children'][slot_name + '=' + child_type] += 1
            examples[typ].append((path, loc, status, parent, signature, anchor))

    write_tsv('template-links.tsv', ['path', 'pointer', 'name', 'static_status', 'name_candidates',
                                     'def_path', 'def_pointer'], template_refs)

    def sample(typ):
        stats = detail[typ]
        nodes = examples[typ]
        typical = min(nodes, key=lambda row: (row[2] != 'core', -stats['families'][sample_families(row[0])],
                                             -stats['signature'][row[4]], row[0], row[1]))
        rare = min(nodes, key=lambda row: (row == typical, row[0] == typical[0], row[3] == typical[3],
                                          stats['signature'][row[4]], stats['slots'][row[3]], row[0], row[1]))
        return typical, rare

    column_keys = ['slots', 'placement', 'families', 'fields', 'targets', 'inputs', 'children', 'link_fields', 'contexts']
    rows = []
    for typ, stats in sorted(detail.items()):
        common, rare = sample(typ)
        level = stats['level']
        rows.append([typ, *label(typ, notes), totals[typ], level['core'], level['adjacent'], level['special'],
                     *(fmt(stats[key]) for key in column_keys),
                     common[0], common[1], common[5], rare[0] if rare != common else '',
                     rare[1] if rare != common else '', rare[5] if rare != common else ''])
    evidence = []
    source_cache = {}
    for typ in sorted(notes):
        if typ not in detail:
            continue
        for row in dict.fromkeys(sample(typ)):
            path, loc, status, parent, _, anchor = row
            if path not in source_cache:
                source_cache[path] = source(path)
            node = lookup(source_cache[path], loc)
            keys = notes[typ]['focus_fields'].split(',')
            fragment = dump_evidence(node, keys)
            evidence.append((typ, path, loc, anchor, parent, status, fragment))
    write_tsv('semantic-evidence.tsv', ['type', 'path', 'pointer', 'anchor', 'slot', 'scope', 'observed_fragment'],
              evidence)
    assert set(notes) <= detail.keys(), sorted(set(notes) - detail.keys())
    write_tsv('operations.tsv',
              ['type', 'category', 'semantic_grade', 'configured_role', 'all_indexed_occurrences', 'core', 'adjacent', 'special',
               *column_keys, 'usual_path', 'usual_pointer', 'usual_anchor', 'contrasting_path', 'contrasting_pointer',
               'contrasting_anchor'], rows)
    write_tsv('review-outside.tsv', ['type', 'parent_field', 'directory', 'count', 'example_path', 'example_pointer'],
              ((*key, counts['review', key]['n'], *value) for key, value in sorted(review.items())))

    counts_by_level = Counter()
    for typ, stats in detail.items():
        for level, value in stats['level'].items():
            counts_by_level[level] += value
    per_level_types = {level: sum(stats['level'][level] > 0 for stats in detail.values()) for level in counts_by_level}
    opaque = sum(1 for typ in detail if re.fullmatch(r'[A-Z]{11}', typ))
    singles = sum(1 for stat in detail.values() if stat['level'].total() == 1)
    print('task-set:', len(detail), counts_by_level.total(), dict(counts_by_level), per_level_types)
    print('opaque:', opaque, 'singletons:', singles, 'semantic notes:', len(notes), 'selected files:', len(selected))
    print('outside review:', len({key[0] for key in review}), sum(value['n'] for value in counts.values()))
    assert sum(stats['level'].total() for stats in detail.values()) == sum(map(len, selected.values()))

if __name__ == '__main__':
    catalogue()
