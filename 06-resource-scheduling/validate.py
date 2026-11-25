#!/usr/bin/env python3
"""Verify representative resource and scheduling edges against the source."""
from catalogue import cached_source, connect, lookup
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABILITIES = 'Config/ConfigAbility/Avatar/Avatar_'
CHARACTERS = 'Config/ConfigCharacter/Avatar/Avatar_'
EXCEL = 'ExcelOutput/'

def value(path, pointer):
    return lookup(cached_source(path), pointer)

def ability(role, pointer):
    return value(ABILITIES + role + '_00_Ability.json', pointer)

def character(role, pointer):
    return value(CHARACTERS + role + '_00_Config.json', pointer)

def excel(table, pointer):
    return value(EXCEL + table + '.json', pointer)

def kind(node):
    return node['$type'].removeprefix('RPG.GameCore.')

def cost_chain():
    archer = excel('AvatarConfigLD', '/1')
    archer_skill = excel('AvatarSkillConfigLD', '/76')
    archer_entry = character('Archer', '/SkillList/1')
    archer_call = ability('Archer', '/AbilityList/2/OnStart/7')
    assert archer['AvatarID'] == 1015 and archer_skill['SkillID'] in archer['SkillList']
    assert archer_entry['Name'] == archer_skill['SkillTriggerKey'] == 'Skill02'
    assert archer_skill['BPNeed']['Value'] == 2
    assert archer_entry['EntryAbility'] == ability('Archer', '/AbilityList/2/Name')
    assert archer_call['AbilityName']['Value'] == ability('Archer', '/AbilityList/3/Name')
    rank = ability('Archer', '/AbilityList/3/OnStart/10/Predicate/TriggerKey/Hash')
    assert rank == excel('AvatarRankConfigLD', '/6/Trigger/Hash')
    bump = ability('Archer', '/AbilityList/3/OnStart/10/SuccessTaskList/0/SuccessTaskList/0')
    assert kind(bump) == 'ModifyTeamBoostPoint' and bump['ModifyFunction'] == 'Add'
    trigger = '/GlobalModifiers/MAvatar_Archer_00_BonusTrigger/_CallbackList/1'
    request = ability('Archer', trigger + '/CallbackConfig/1/SuccessTaskList/1/SuccessTaskList/0')
    assert ability('Archer', trigger + '/Event') == 'OnListenAfterAction'
    assert kind(request) == 'TurnInsertAction' and request['CanInsertUltraSkill'] is True
    assert request['OnInsertAbort'][0]['DynamicKey']['Value'] == 'MDF_InBonus'
    assert [excel('AvatarSkillConfig', f'/{i}/BPNeed/Value') for i in (1333,1342,1351)] == [1,2,3]
    instance = '/AbilityList/9/Modifiers/MAvatar_DanHengIL_00_BPCost_1/_CallbackList'
    assert ability('DanHengIL', instance + '/1/CallbackConfig/3/Properties/0/Value/FixedValue/Value') == 1
    assert ability('DanHengIL', instance + '/0/CallbackConfig/1/Properties/0/OperatorType') == 'Unset'
    assert character('Phainon', '/SkillList/2/UsableConditions/0/UsableCondition/Predicate/Flag') == 'SpecialBattleArea'
    print('Passed Archer master/entry/rank/insert links, DanHengIL tier costs and override, Phainon eligibility.')

def resource_edges():
    tingyun = ability('Tingyun', '/AbilityList/6/OnStart/7/FailedTaskList/0')
    huohuo = ability('Huohuo', '/AbilityList/6/OnStart/1')
    assert kind(tingyun) == kind(huohuo) == 'ModifySPNew' and 'FixedAddValue' in tingyun
    assert 'FixedAddMaxSPRatio' in huohuo
    a = ability('Acheron', '/GlobalModifiers/MAvatar_Acheron_00_BlockModifySp/_CallbackList/0/CallbackConfig/1')
    p = ability('Phainon', '/AbilityList/24/Modifiers/MAvatar_Phainon_00_PassiveSkill01/_CallbackList/0/CallbackConfig/1')
    assert kind(a) == kind(p) == 'ModifySP'
    assert a['ModifyValue']['FixedValue']['Value'] == p['ModifyValue']['FixedValue']['Value'] == 0
    assert ability('Acheron', '/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra/OnAbilityPropertyChange/0/Property') == 'CurrentSpecialSP'
    phainon = ability('Phainon', '/GlobalTemplates/1/TaskList/0/TaskList/0')
    assert kind(phainon['SuccessTaskList'][0]) == 'ModifySpecialSP'
    assert phainon['FailedTaskList'][0]['Key']['Value'] == 'CurOverflowSpecialSP'
    rank = ability('Phainon', '/AbilityList/28/Modifiers/M_Phainon_00_SkillTree02_SubListener/_CallbackList/1')
    assert rank['Event'] == 'OnSPChange'
    assert rank['CallbackConfig'][0]['SuccessTaskList'][1]['SuccessTaskList'][1]['Name'] == ability('Phainon', '/GlobalTemplates/1/Name')
    sources = [
        ('DanHengIL', '/AbilityList/15/Modifiers/MAvatar_DanHengIL_PassiveModifier/_CallbackList/3', 'BPExChange'),
        ('Sparxie', '/GlobalModifiers/MAvatar_Sparxie_00_Passive01/_CallbackList/0', 'Sparxie_EnergyPoint'),
    ]
    for role, pointer, key in sources:
        candidate = ability(role,pointer)
        assert candidate['Event'] == 'OnListenBpChange'
        assert candidate['CallbackConfig'][0]['ValueType'] == 'RawDelta'
        assert candidate['CallbackConfig'][1]['SuccessTaskList'][0]['FHLJGDGMMHK'] == key
    print('Passed standard/special SP distinction and resource event payload/overflow branches.')

def scheduling_edges():
    r = '/GlobalModifiers/MAvatar_Robin_00_Skill03Area_sub/_CallbackList/1/CallbackConfig/0'
    r_event = excel('BattleEventConfig', '/46')
    assert ability('Robin',r)['EventID']['FixedValue']['Value'] == r_event['BattleEventID'] == 11309
    assert r_event['AbilityList'][0] == ability('Robin','/AbilityList/8/Name')
    j_event = excel('BattleEventConfig','/42')
    j_req = ability('JingYuan','/AbilityList/7/OnStart/4')
    assert j_req['EventID']['FixedValue']['Value'] == j_event['BattleEventID'] == 11203
    assert (j_req['Team'],j_event['Team']) == ('TeamLight','TeamNeutral')
    aglaea_servant = ability('Aglaea','/AbilityList/12/OnStart/1/SuccessTaskList/0')
    aglaea_event = ability('Aglaea','/AbilityList/12/OnStart/9')
    assert (kind(aglaea_servant),kind(aglaea_event)) == ('CreateServant','CreateBattleEvent')
    assert aglaea_servant['ServantID']['FixedValue']['Value'] == excel('AvatarServantConfig','/0/ServantID') == 11402
    assert aglaea_event['EventID']['FixedValue']['Value'] == excel('BattleEventConfig','/48/BattleEventID') == 11402
    assert ability('Phainon','/AbilityList/18/OnStart/4/TaskList/0/EventID/FixedValue/Value') == excel('BattleEventConfig','/50/BattleEventID') == 11408
    pred = ability('RuanMei','/AbilityList/8/OnStart/0/Predicate')
    assert pred == {'$type':'RPG.GameCore.ByIsFirstInsertAbilityInQueue','Inverse':True}
    with connect() as db:
        assert db.execute("SELECT occurrences FROM type_counts WHERE type='RPG.GameCore.ByIsFirstInsertAbilityInQueue'").fetchone() == (1,)
    print('Passed ordered-request predicate and four entity-to-BattleEvent joins, including separate servant namespace.')

def check_catalogue():
    with connect() as db:
        totals = dict(db.execute('SELECT type,occurrences FROM type_counts'))
        selectors = dict(db.execute("SELECT name,count(*) FROM events WHERE form='callback-selector' GROUP BY name"))
    with (HERE / 'interfaces.tsv').open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    assert len({r['type'] for r in rows}) == len(rows)
    for row in rows:
        assert int(row['all_occurrences']) == totals[row['type']] == sum(json.loads(row['anchor_counts']).values())
    with (HERE / 'events.tsv').open(encoding='utf-8') as handle:
        events = list(csv.DictReader(handle, delimiter='\t'))
    assert all(selectors[r['name']] == int(r['count']) for r in events if r['form']=='callback-selector')
    assert {'OnSPChange','OnListenBpChange','OnBeforeSkillCost','OnListenTurnPhase1Begin'} <= {r['name'] for r in events}
    print(f'{len(rows)} indexed interface types and {len(events)} event-role rows verified.')

if __name__ == '__main__':
    cost_chain()
    resource_edges()
    scheduling_edges()
    check_catalogue()
