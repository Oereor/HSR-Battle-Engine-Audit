#!/usr/bin/env python3
"""Inventory resource and scheduling configuration interfaces using the shared v2 index."""
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
os.environ['AUDIT_INDEX_VERSION'] = '2'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'tools'))
from query import connect, lookup, source

cached_source = lru_cache(maxsize=6)(source)

FAMILIES = {
    'SP 与 BP': r'(?:^|Modify|Compare|Change|Read|Consume|Cost|Gain|Current|Max|Input|Set|Extra|Lock|Ignore|Calc|Transfer|By)(?:SpecialSP|TeamBoostPoint|EntityBoostPoint|SP(?:Need|Ratio|Change|Cost|Bar|Limit|Overflow|$)|BP(?:Need|Change|Cost|Limit|$)|BoostPoint|SkillPoint)|EnergyBar|TeamPlayerSP',
    'HP 与护盾': r'(?:Heal(?:HP|By)|LoseHP|SetHP|LockTargetHP|HPOverflow|HPRatio|HPChange|HPShared|Shield|MaxHP|HPThreshold|HPPercent|PreCalcHPDamage|ForceKill|Revive)',
    '韧性与弱点': r'(?:Stance|Weakness|BreakState|TriggerBreak|RedStance|WeakBy)',
    '技能费用与资格': r'(?:SkillCost|SkillProperty|CurrentSkillType|ControlSkillType|ControlSkillMapping|UsedSkill|SkillTypeDisable|SkillCost|SPChangeTag|OverrideSkillReady|HasSpecialSkill)',
    '速度与行动值': r'(?:ActionDelay|SpeedDelta|SpeedAddedRatio|BaseSpeed|TurnBasedAdvance|SpeedRatio)',
    '行动与 Ability 请求': r'(?:TurnInsert|Insert(?:Ability|Action|Ultra|Skill)|Extra(?:Action|Turn)|Unused(?:Ultra|Insert)|WaitUltraCount|TurnSource|TriggerAbility|AutoUseUltra|ActionState|PendingInsert)',
    '阶段与调度控制': r'(?:PauseToTurnEnd|PauseGameMode|WaitForTurnEnd|WaitTurnCount|ActionCountDown|TurnLimit|BattleWave|WaveMonster|TaskScheduler|WaitFor$|^WaitSecond$|^WaitFrame|DelayExecute|Queue|SkillPerformFinish|DamagePerformFinish|ClearAction|ForbidAction|CancelAction|ResetAction)',
    '召唤与战斗实体': r'(?:Create(?:BattleEvent|Servant|Summon)|Summon(?:Partner|Monster|Unit|er)|BattleEvent(?:Config|Caster)|Servant(?:Config|Delay)|SetStageBattleEvents|ChildEntity|ForceRemoveEntity|DestroyServant)',
    '其他资源例证': r'(?:ElationPoint|ActivityElationPower|SpecialBattleArea|SwitchBattleArea)',
}
EVENT = re.compile(r'(?i)SPChange|BpChange|SkillCost|HPChange|HPOverflow|LoseHP|Stance|Break|Elation|Action|Turn|Insert|Wave|SwitchBattleArea|OnEnterBattle|OnBattleEventCreate|OnServantCreate|OnMonsterCreate|^OnPhase[12]$')
FIELD_KEYS = set("""
SPNeed BPNeed CurrentSP CurrentSpecialSP MaxSpecialSP SPHitRatio SPMultipleRatio
IgnoreSPDec IgnoreBPDec SkillIndex InsertAbilityPriority InsertConditionPriority
InsertActionPriority PendingInsertAbilityPriority CanInsertUltraSkill CancelPrepareAbilityIfDelayed
FollowSameTagNormalAction SkipTargetTurn WhitelistChangeReason
""".split())
TASK_EVIDENCE = {
    'LAJIKDENEOO': '丹恒与火花的 BP 改变分支，目标与私有键可见',
    'CNLIMBPHJNP': '火花战技同一类型有多处，原始字段未解',
    'JDOLDFECMPL': '火花奖池模板的队伍 BP 操作邻接节点，准确效应未知',
    'RPG.GameCore.SetDynamicValueByVariateType': 'Phainon OnSPChange 取得 ParamValue2',
    'RPG.GameCore.SetDynamicValueByChangeValue': 'Acheron CurrentSpecialSP 分支读取 ClampedAdd',
    'RPG.GameCore.SetDynamicValueByProperty': '可选属性来源，角色与环境均有样本',
    'RPG.GameCore.SetDynamicValueByAddValue': '显式变量加法，例如 Phainon 溢出',
    'RPG.GameCore.StackProperty': '属性修改可配置 SpeedDelta、BaseSpeed 等',
    'RPG.GameCore.ModifyProperty': '属性修改',
    'RPG.GameCore.AddModifier': '用于费用模式、溢出和队伍行动限制',
    'RPG.GameCore.RemoveModifier': '用于费用模式、溢出和队伍行动限制',
    'RPG.GameCore.RemoveSelfModifier': '溢出持有者清理及恢复路径',
    'RPG.GameCore.DamageByAttackProperty': '伤害及附带韧性配置',
    'RPG.GameCore.AttackData': 'StanceValue 和 SPHitRatio 与命中参数可并列',
    'RPG.GameCore.CharacterChangePhase': '战斗实体阶段切换',
    'RPG.GameCore.DefineDynamicValue': '角色私有键的初始化形态',
    'RPG.GameCore.SwitchByCommandType': '部分阻止普通 SP 路径的状态初始化任务',
}
MASTER = {
    'AvatarConfig': {'AvatarID', 'SPNeed', 'BPNeed', 'SkillList', 'JsonPath'},
    'AvatarConfigLD': {'AvatarID', 'SPNeed', 'BPNeed', 'SkillList', 'JsonPath'},
    'AvatarSkillConfig': {'SkillID', 'Level', 'SkillTriggerKey', 'SPNeed', 'BPNeed', 'SPMultipleRatio', 'DelayRatio', 'AttackType', 'InitCoolDown', 'CoolDown'},
    'AvatarSkillConfigLD': {'SkillID', 'Level', 'SkillTriggerKey', 'SPNeed', 'BPNeed', 'SPMultipleRatio', 'DelayRatio', 'AttackType', 'InitCoolDown', 'CoolDown'},
    'AvatarServantConfig': {'ServantID', 'Config', 'SpeedBase', 'SpeedInherit', 'SpeedSkill', 'HPBase', 'HPInherit', 'HPSkill'},
    'BattleEventConfig': {'BattleEventID', 'Team', 'EventSubType', 'Speed', 'AbilityList', 'BEActionBarType'},
    'MonsterConfig': {'MonsterID', 'HPModifyRatio', 'SpeedModifyRatio', 'StanceModifyRatio', 'StanceWeakList'},
    'MonsterTemplateConfig': {'MonsterTemplateID', 'BaseSpeed', 'BaseHP', 'BaseStance', 'Speed', 'HP', 'Stance', 'SkillList', 'Config'},
}

def write(name, headers, rows):
    with (HERE / name).open('w', encoding='utf-8', newline='') as handle:
        out = csv.writer(handle, delimiter='\t', lineterminator='\n')
        out.writerow(headers)
        out.writerows(rows)

def pack(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

def relevant(short):
    return [cat for cat, rx in FAMILIES.items() if re.search(rx, short)]

def build(db):
    with (ROOT / '02-atomic-operations' / 'operations.tsv').open(encoding='utf-8') as handle:
        operation_roles = {r['type']: r for r in csv.DictReader(handle, delimiter='\t')}
    fields_by_type = defaultdict(dict)
    key_signals = defaultdict(set)
    for typ, field, shape, count in db.execute("SELECT type,field,shape,count FROM fields ORDER BY type,field,shape"):
        fields_by_type[typ][f'{field}:{shape}'] = count
        if field in FIELD_KEYS:
            key_signals[typ].add(field)

    rows = []
    for typ, count, nfiles in db.execute('SELECT type,occurrences,files FROM type_counts ORDER BY type'):
        matches = relevant(typ.rsplit('.', 1)[-1])
        if not (matches or key_signals[typ] or typ in TASK_EVIDENCE):
            continue
        scopes = dict(db.execute('SELECT COALESCE(NULLIF(anchor_kind,\'\'),\'<none>\'),count(*) FROM types WHERE type=? GROUP BY 1', (typ,)))
        roles = operation_roles.get(typ, {})
        examples = db.execute("""SELECT path,pointer,parent_field FROM occurrences WHERE type=?
                             ORDER BY anchor_kind NOT IN ('ability','modifier','template'),path,pointer LIMIT 1""", (typ,)).fetchone()
        assert lookup(cached_source(examples[0]), examples[1])['$type'] == typ
        rows.append((typ, '|'.join(matches), '|'.join(sorted(key_signals[typ])),
                     TASK_EVIDENCE.get(typ, ''), count, nfiles, pack(scopes),
                     *(roles.get(key, '') for key in ('core', 'adjacent', 'special')), pack(fields_by_type[typ]), *examples))
    write('interfaces.tsv',
          ['type', 'name_match_categories', 'explicit_fields', 'curated_link', 'all_occurrences', 'files', 'anchor_counts',
           'stage02_core', 'stage02_adjacent', 'stage02_special', 'fields', 'example_path', 'example_pointer', 'parent_field'],
          rows)

    events = defaultdict(list)
    for path, pointer, name, form, anchor, ak in db.execute("""
      SELECT path,pointer,name,form,anchor,anchor_kind
      FROM event_locations WHERE form IN ('callback-selector','hook') ORDER BY path,pointer
    """):
        if EVENT.search(name):
            events[form, name].append((path, pointer, anchor, ak))
    event_rows = []
    for (form, name), locations in sorted(events.items()):
        by_anchor = Counter(a[-1] or '<none>' for a in locations)
        candidate = next((r for r in locations if r[-1] in {'ability', 'modifier', 'template'}), locations[0])
        if form == 'callback-selector':
            assert lookup(cached_source(candidate[0]), candidate[1]) == name, (name, candidate)
        event_rows.append((form, name, len(locations), pack(dict(by_anchor)), *candidate))
    write('events.tsv', ['form','name','count','anchor_counts','path','pointer','anchor','anchor_kind'], event_rows)

    unresolved = list(db.execute("""
        SELECT parent_type,path,pointer,field,name,status,candidate_count
        FROM reference_locations
        WHERE kind='ability' AND status IN ('unresolved','ambiguous')
        AND parent_type IN ('RPG.GameCore.TurnInsertAction','RPG.GameCore.TurnInsertAbility',
                            'RPG.GameCore.TriggerAbility','RPG.GameCore.AbortInsertAbility',
                            'RPG.GameCore.TurnInsertAssistantAbility')
        ORDER BY parent_type,path,pointer
    """))
    write('unresolved-requests.tsv', ['type','path','pointer','field','name','status','candidate_count'], unresolved)

    master_rows = []
    for table, keys in MASTER.items():
        path = f'ExcelOutput/{table}.json'
        records = source(path)
        shapes = defaultdict(Counter)
        examples = {}
        for i, row in enumerate(records):
            for field in keys & row.keys():
                val = row[field]
                kind = 'null' if val is None else type(val).__name__
                shapes[field][kind] += 1
                examples.setdefault(field, (f'/{i}/{field}', pack(val)))
        for field, kind_counts in sorted(shapes.items()):
            master_rows.append((path, field, sum(kind_counts.values()), len(records), pack(kind_counts), *examples[field]))
    write('master-fields.tsv', ['path','field','present_rows','table_rows','shapes','first_pointer','first_value'], master_rows)

    print(f'{len(rows)} typed candidates, {sum(int(r[7] or 0) > 0 for r in rows)} intersect stage 02 core.')
    for form, count in sorted(Counter(r[0] for r in event_rows).items()):
        print(f'{count} distinct {form} names by query.')
    print(f'{len(master_rows)} Excel table/field combinations.')
    print(f'{len(unresolved)} ambiguous or unresolved Ability request literals under selected types.')

if __name__ == '__main__':
    with connect() as db:
        build(db)
