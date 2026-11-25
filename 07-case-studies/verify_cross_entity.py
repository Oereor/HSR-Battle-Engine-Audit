#!/usr/bin/env python3
"""Static source checks for cases 09–12."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from probe_named_values import alternating_djb2
from query import lookup, source


def avatar(name, family='ConfigAbility', group='Avatar', suffix='Ability'):
    return source(f'Config/{family}/{group}/{name}_{suffix}.json')


def fix(value):
    assert value['IsDynamic'] is False
    return value['FixedValue']['Value']


def check_cerydra():
    char = avatar('Avatar_Cerydra_00', 'ConfigCharacter', suffix='Config')
    ability = avatar('Avatar_Cerydra_00')
    skill = source('ExcelOutput/AvatarSkillConfig.json')[4524]
    assert skill['SkillID'] in source('ExcelOutput/AvatarConfig.json')[70]['SkillList']
    assert lookup(char, '/SkillList/1/Name') == skill['SkillTriggerKey']
    assert lookup(char, '/SkillList/1/EntryAbility') == lookup(ability, '/AbilityList/2/Name')
    assert lookup(char, '/DynamicValues/Floats/208472327/ReadInfo/Index') == 3
    assert lookup(skill, '/ParamList/3/Value') == 6
    assert lookup(ability, '/AbilityList/2/OnStart/1/SuccessTaskList/23/AbilityName/Value') == lookup(
        ability, '/AbilityList/3/Name'
    )
    promotion = lookup(ability, '/GlobalTemplates/0')
    assert lookup(ability, '/AbilityList/8/OnStart/16/Name') == promotion['Name']
    assert lookup(promotion, '/TaskList/2/ModifierName/Value') == 'MCommon_Windfury'
    assert fix(lookup(promotion, '/TaskList/2/DynamicValues/_ReplaySkill')) == 1
    common = source('Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json')
    callback = lookup(common, '/ModifierMap/MCommon_Windfury/_CallbackList/5')
    assert callback['Event'] == 'OnAfterSkillUse'
    request = lookup(callback, '/CallbackConfig/0/SuccessTaskList/3/SuccessTaskList/0/FailedTaskList/3')
    assert request['$type'] == 'RPG.GameCore.TurnInsertAction' and request['OnInsertAbort']
    assert request['TargetType']['Alias'] == 'ModifierOwnerEntity'
    assert request['AutoCastTargetType']['Alias'] == 'ModifierOwnerSkillTargetEntityList'
    assert request['InsertActionPriority'] == 'Windfury'


def check_summons():
    event = source('ExcelOutput/BattleEventConfig.json')
    event_data = source('ExcelOutput/BattleEventData.json')
    jing = avatar('Avatar_JingYuan_00')
    assert fix(lookup(jing, '/AbilityList/7/OnStart/4/EventID')) == event[42]['BattleEventID'] == 11203
    assert event[42]['AbilityList'] == [jing['AbilityList'][i]['Name'] for i in (9, 12)]
    call = lookup(jing, '/GlobalModifiers/MAvatar_JingYuan_00_BattleEvent/_CallbackList/0/CallbackConfig/0')
    assert call['AbilityName']['Value'] == jing['AbilityList'][10]['Name']
    assert call['TargetType']['Alias'] == 'BattleEventCaster'

    topaz = avatar('Avatar_Topaz_00')
    assert fix(lookup(topaz, '/AbilityList/8/OnStart/7/EventID')) == event[44]['BattleEventID'] == 11216
    assert event[44]['AbilityList'] == [] and event_data[107]['BattleEventID'] == 11216
    event_skill = source('ExcelOutput/BattleEventSkillConfig.json')[7]
    assert event_skill['SkillID'] in event_data[107]['SkillIDList']
    event_char = source(event_data[107]['Config'])
    assert event_char['SkillList'][0]['Name'] == event_skill['SkillTriggerKey']
    assert event_char['SkillList'][0]['EntryAbility'] == topaz['AbilityList'][10]['Name']
    request = lookup(topaz, '/AbilityList/10/Modifiers/Topaz_BETag/_CallbackList/1/CallbackConfig/2/SuccessTaskList/0')
    assert request['AbilityName']['Value'] == topaz['AbilityList'][15]['Name']

    aglaea = avatar('Avatar_Aglaea_00')
    servant = source('ExcelOutput/AvatarServantConfig.json')[0]
    assert fix(lookup(aglaea, '/AbilityList/3/OnStart/1/SuccessTaskList/0/ServantID')) == servant['ServantID'] == 11402
    assert fix(lookup(aglaea, '/AbilityList/12/OnStart/9/EventID')) == event[48]['BattleEventID'] == 11402
    assert event[48]['AbilityList'] == [aglaea['AbilityList'][13]['Name']]


def check_cyrene():
    owner = avatar('Avatar_Cyrene_00')
    servant = source('ExcelOutput/AvatarServantConfig.json')[4]
    assert fix(lookup(owner, '/AbilityList/8/OnStart/7/ServantID')) == servant['ServantID'] == 11415
    assert 1141523 in servant['SkillIDList']
    skill = source('ExcelOutput/AvatarServantSkillConfig.json')[400]
    assert skill['SkillID'] == 1141523
    char = source(servant['Config'])
    ability = avatar('Servant_CyreneServant_00', group='Servant')
    rule = lookup(ability, '/AbilityList/5/OnStart/21')
    assert fix(lookup(rule, '/Predicate/TargetCharacterID')) == 1412
    values = lookup(rule, '/SuccessTaskList/0/DynamicValues')
    for key, expected in [('MDF_DamageIncrease', 0.15), ('MDF_ExtraPoint', 1)]:
        hash_value, = lookup(values, f'/{key}/PostfixExpr/DynamicHashes')
        bind = lookup(char, f'/DynamicValues/Floats/{hash_value}/ReadInfo')
        assert bind['TriggerKey'] == skill['SkillTriggerKey']
        assert skill['ParamList'][bind['Index']]['Value'] == expected
    cost_key = lookup(
        ability, '/GlobalModifiers/MServant_CyreneServant_00_AmazingBuff_Cerydra/_CallbackList/1/CallbackConfig/0/Key/Value'
    )
    receiver = lookup(
        avatar('Avatar_Cerydra_00'),
        '/GlobalModifiers/MAvatar_Cerydra_00_Skill02_Target_Lv2/_CallbackList/4/CallbackConfig/0/SuccessTaskList/0/Value/PostfixExpr/DynamicHashes',
    )
    assert alternating_djb2(cost_key) == 840429360 and 840429360 in receiver


def check_elation():
    stage = source('Config/Level/StageCommonTemplate.json')
    ability = source('Config/ConfigAbility/BattleEvent/StageAbility_Elation.json')
    assert lookup(stage, '/OnStartSequece/1/TaskList/6/SuccessTaskList/0/StageAbilityName/Value') == ability['AbilityList'][0]['Name']
    event_data = source('ExcelOutput/BattleEventData.json')
    assert lookup(ability, '/AbilityList/0/OnStart/0/BattleEventID') == [event_data[i]['BattleEventID'] for i in (371, 456)]
    elation_char = source(event_data[371]['Config'])
    skill41 = source('ExcelOutput/BattleEventSkillConfig.json')[167]
    assert skill41['SkillID'] in event_data[371]['SkillIDList']
    assert skill41['SkillTriggerKey'] == lookup(elation_char, '/SkillList/2/Name')
    assert lookup(elation_char, '/SkillList/2/EntryAbility') == ability['AbilityList'][4]['Name']
    assert lookup(ability, '/AbilityList/4/OnStart/5/AbilityName/Value') == ability['AbilityList'][5]['Name']
    random = lookup(ability, '/AbilityList/5/OnStart/1/TaskList/0')
    for i, value in enumerate((0.5, 0.5)):
        token, = lookup(random, f'/OddsList/{i}/PostfixExpr/DynamicHashes')
        index = lookup(elation_char, f'/DynamicValues/Floats/{token}/ReadInfo/Index')
        assert skill41['ParamList'][index]['Value'] == value
    yao = avatar('Avatar_YaoGuang_00')
    request = lookup(yao, '/AbilityList/6/OnStart/4/FailedTaskList/0')
    template = lookup(source('Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json'), '/TaskListTemplate/50')
    assert request['Name'] == template['Name'] == 'Elation_StartElationTime'
    assert fix(lookup(request, '/DynamicValues/TryStartElationTime_ElationTimeIsNoConsume')) == 1
    assert fix(lookup(template, '/TaskList/0/TaskList/0/SkillIndex')) == 0


if __name__ == '__main__':
    for check in (check_cerydra, check_summons, check_cyrene, check_elation):
        check()
        print('verified', check.__name__)
