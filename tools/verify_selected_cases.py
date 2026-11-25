#!/usr/bin/env python3
"""Verify specific source joins in the Himeko, equipment, and enemy case studies."""
from query import lookup, source

def selected(path, *pointers):
    root = source(path)
    return tuple(lookup(root, p) for p in pointers)

def fixed(node):
    assert node['IsDynamic'] is False
    return node['FixedValue']['Value']

def float_binding(char, hash_value, trigger, index):
    info = lookup(char, f'/DynamicValues/Floats/{hash_value}/ReadInfo')
    assert (info['Type'], info['TriggerKey'], info['Index']) == ('SkillParam', trigger, index)

def himeko():
    base, talent = selected('ExcelOutput/AvatarSkillConfig.json', '/43', '/82')
    char, = selected('Config/ConfigCharacter/Avatar/Avatar_Himeko_00_Config.json', '')
    assert (base['SkillID'], talent['SkillID']) == (100301, 100304)
    normal, follow_up = (lookup(char, f'/SkillList/{i}') for i in (0, 3))
    assert (normal['Name'], follow_up['Name']) == (base['SkillTriggerKey'], talent['SkillTriggerKey'])
    float_binding(char, -1126825319, normal['Name'], 0)
    float_binding(char, 1246667513, follow_up['Name'], 0)
    float_binding(char, -54401499, follow_up['Name'], 1)

    root = source('Config/ConfigAbility/Avatar/Avatar_Himeko_00_Ability.json')
    abilities = root['AbilityList']
    assert abilities[0]['Name'] == normal['EntryAbility']
    assert abilities[7]['Name'] == follow_up['EntryAbility']
    assert abilities[0]['OnStart'][1]['AbilityName']['Value'] == abilities[1]['Name']
    hits = [abilities[1]['OnStart'][i] for i in (5, 7)]
    props = [hit['AttackProperty'] for hit in hits]
    assert [fixed(prop['HitSplitRatio']) for prop in props] == [0.4, 0.6]
    assert all(prop['DamagePercentage']['PostfixExpr']['DynamicHashes'] == [-1126825319] for prop in props)
    modifier_name = abilities[7]['OnStart'][0]['ModifierName']['Value']
    callbacks = abilities[7]['Modifiers'][modifier_name]['_CallbackList']
    assert callbacks[0]['Event'] == 'OnListenAfterAttack'
    body = callbacks[0]['CallbackConfig'][0]['SuccessTaskList'][0]
    assert body['Predicate']['CompareValue']['PostfixExpr']['DynamicHashes'] == [-54401499]
    insertion = lookup(body, '/SuccessTaskList/0/SuccessTaskList/0')
    assert insertion['AbilityName']['Value'] == abilities[8]['Name']
    assert insertion['InsertAbilityPriority'] == 'AvatarInsertAttackSelf'
    assert lookup(abilities[8], '/OnStart/0/SuccessTaskList/7/AbilityName/Value') == abilities[9]['Name']
    assert lookup(abilities[9], '/OnStart/7/AttackProperty/DamagePercentage/PostfixExpr/DynamicHashes/0') == 1246667513

def equipment():
    item, = selected('ExcelOutput/EquipmentConfig.json', '/0')
    skill, = selected('ExcelOutput/EquipmentSkillConfig.json', '/0')
    modern, = selected('Config/ConfigAbility/Equip/EquipmemtAbility.json', '/AbilityList/1')
    other, = selected('Config/ConfigAbility/EquipmemtAbility.json', '/AbilityList/1')
    assert item['SkillID'] == skill['SkillID'] == 20000
    assert modern['Name'] == other['Name'] == skill['AbilityName'] == 'Ability20000'
    assert [x['Value'] for x in skill['ParamList']] == [0.12, 3]
    modifier = modern['OnStart'][0]['ModifierName']['Value']
    callback = modern['Modifiers'][modifier]['_CallbackList'][0]
    assert callback['Event'] == 'OnStack'
    assert callback['CallbackConfig'][0]['Property'] == 'CriticalChanceBase'
    for expr, index in [
        (modern['OnStart'][0]['LifeTime'], 1),
        (callback['CallbackConfig'][0]['PropertyValue'], 0),
    ]:
        hash_value, = expr['PostfixExpr']['DynamicHashes']
        info = lookup(modern, f'/DynamicValues/Floats/{hash_value}/ReadInfo')
        assert (info['Type'], info['Index']) == ('SkillEquip', index)
    assert set(other['DynamicValues']) == {'Values'}

    two, four = selected('ExcelOutput/RelicSetSkillConfig.json', '/0', '/1')
    assert two['SetID'] == four['SetID'] == 101
    assert (two['RequireNum'], four['RequireNum']) == (2, 4)
    assert two['PropertyList'] and not two['AbilityName']
    actual, = selected('Config/ConfigAbility/Equip/RelicAbility.json', '/AbilityList/1')
    assert four['AbilityName'] == actual['Name']
    callback = lookup(actual, '/Modifiers/MRelic_101_Main/_CallbackList/0')
    assert callback['Event'] == 'OnEnterBattle'
    branch, = callback['CallbackConfig']
    assert branch['Predicate']['$type'] == 'RPG.GameCore.ByCompareWaveCount'
    assert fixed(branch['Predicate']['CompareValue']) == 1
    task, = branch['SuccessTaskList']
    assert task['$type'] == 'RPG.GameCore.ModifyTeamBoostPoint'
    assert task['ModifyFunction'] == 'Add' and fixed(task['ModifyValue']) == 1

def enemy():
    stage, = selected('ExcelOutput/StageConfig.json', '/22705')
    monster, = selected('ExcelOutput/MonsterConfig.json', '/1640')
    template, = selected('ExcelOutput/MonsterTemplateConfig.json', '/356')
    skill, = selected('ExcelOutput/MonsterSkillConfig.json', '/2089')
    assert stage['MonsterList'][0]['Monster0'] == monster['MonsterID'] == 401501001
    assert monster['MonsterTemplateID'] == template['MonsterTemplateID'] == 4015010
    assert skill['SkillID'] in monster['SkillList']
    char = source(template['JsonConfig'])
    assert lookup(char, '/SkillList/10/Name') == skill['SkillTriggerKey']
    float_binding(char, 1405254526, skill['SkillTriggerKey'], 5)
    assert skill['ParamList'][5]['Value'] == 120
    root = source('Config/ConfigAbility/Monster/Monster_W4_DawnsEye_00_Ability.json')
    assert root['AbilityList'][0]['Name'] == char['SkillList'][10]['EntryAbility']
    assert root['AbilityList'][9]['Name'] in monster['AbilityNameList']
    stance = lookup(root, '/AbilityList/0/OnStart/17/DynamicValues/StanceDamage/PostfixExpr')
    assert stance['DynamicHashes'] == [1405254526]
    controller = root['GlobalModifiers']['MMonster_W4_DawnsEye_00_PhaseController']
    assert [r['Event'] for r in controller['_CallbackList']] == ['OnCreate', 'OnLimboWaitHeal']
    guard = lookup(controller, '/_CallbackList/1/CallbackConfig/3/SuccessTaskList/0/SuccessTaskList/5')
    for pointer, index in [('/SuccessTaskList/1', 13), ('/FailedTaskList/0', 14)]:
        insert = lookup(guard, pointer)
        assert insert['AbilityName']['Value'] == root['AbilityList'][index]['Name']
        assert insert['InsertAbilityPriority'] == 'MonsterChangePhase'
    first, second = (lookup(root, p) for p in ['/AbilityList/13/OnStart/1/Name', '/AbilityList/14/OnStart/9/Name'])
    common, = selected('Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json', '/TaskListTemplate/0')
    assert first == second == common['Name']
    assert [common['TaskList'][i]['EventType'] for i in (0, 9)] == [
        {'EnumIndex': 4, 'Value': 13}, {'EnumIndex': 4, 'Value': 8},
    ]

if __name__ == '__main__':
    for exercise in (himeko, equipment, enemy):
        exercise()
        print('verified', exercise.__name__)
