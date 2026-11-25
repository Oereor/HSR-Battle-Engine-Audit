#!/usr/bin/env python3
"""Re-read source joins for the four support case studies."""
from functools import lru_cache
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from query import lookup, source

read_file = lru_cache(maxsize=16)(source)
AVATARS = 'ExcelOutput/AvatarConfig.json'
SKILLS = 'ExcelOutput/AvatarSkillConfig.json'
RANKS = 'ExcelOutput/AvatarRankConfig.json'
TARGETS = 'Config/GlobalConfig/TargetAliasConfig.json'

def read(file, pointer=''):
    return lookup(read_file(file), pointer)

def avatar_files(name):
    return (f'Config/ConfigCharacter/Avatar/Avatar_{name}_Config.json',
            f'Config/ConfigAbility/Avatar/Avatar_{name}_Ability.json')

def input_params(character, row, trigger, bindings):
    skill = read(SKILLS, f'/{row}')
    assert skill['Level'] == 1 and skill['SkillTriggerKey'] == trigger
    for hash_value, index, expected in bindings:
        declaration = read(character, f'/DynamicValues/Floats/{hash_value}/ReadInfo')
        assert declaration == {'Type': 'SkillParam', 'TriggerKey': trigger, 'Index': index}
        assert skill['ParamList'][index]['Value'] == expected

def expression(node, code, hashes):
    assert node['IsDynamic'] and node['PostfixExpr'] == {
        'OpCodes': code, 'FixedValues': [], 'DynamicHashes': hashes,
    }

def entry(character, abilities, avatar_row, skill_row, skill_index, ability_index):
    avatar = read(AVATARS, f'/{avatar_row}')
    skill = read(SKILLS, f'/{skill_row}')
    config = read(character, f'/SkillList/{skill_index}')
    assert avatar['JsonPath'] == character and skill['SkillID'] in avatar['SkillList']
    assert skill['SkillTriggerKey'] == config['Name']
    assert config['EntryAbility'] == read(abilities, f'/AbilityList/{ability_index}/Name')

def request(abilities, pointer, destination):
    assert read(abilities, pointer + '/AbilityName/Value') == read(abilities, f'/AbilityList/{destination}/Name')

def fixed(node):
    assert node['IsDynamic'] is False
    return node['FixedValue']['Value']

def asta():
    char, ability = avatar_files('Asta_00')
    entry(char, ability, 7, 215, 2, 5)
    entry(char, ability, 7, 230, 3, 7)
    request(ability, '/AbilityList/5/OnStart/3', 6)
    input_params(char, 215, 'Skill03', [(812362065, 0, 36), (242053466, 1, 2)])
    input_params(char, 230, 'SkillP01', [(122195315, 0, 0.07), (-954590882, 1, 5), (-1917709945, 2, 3)])
    apply = read(ability, '/AbilityList/6/OnStart/2')
    assert apply['TargetType']['Alias'] == 'AllTeamMember'
    expression(apply['LifeTime'], 'AQAR', [242053466])
    expression(apply['DynamicValues']['MDF_PropertyValue'], 'AQAR', [812362065])
    mod = read(ability, f'/AbilityList/6/Modifiers/{apply["ModifierName"]["Value"]}/_CallbackList/0')
    assert mod['Event'] == 'OnStack' and mod['CallbackConfig'][0]['Property'] == 'SpeedDelta'
    charge = read(ability, '/GlobalModifiers/MAvatar_Asta_00_Passive_Charge')
    assert charge['Count'] == 5 and charge['LifeStepMoment'] == 'ModifierPhase1End'
    set_team = charge['_CallbackList'][1]['CallbackConfig'][3]
    drop_team = charge['_CallbackList'][0]['CallbackConfig'][2]
    assert set_team['ModifierName'] == drop_team['ModifierName'] == {'Value': 'MAvatar_Asta_00_TeamAttackUP'}

def bronya_sunday():
    char, ability = avatar_files('Bronya_00')
    entry(char, ability, 9, 312, 1, 2)
    route = '/AbilityList/2/OnStart/0'
    assert read(ability, route + '/Predicate/$type').endswith('.ByIsTurnActionEntity')
    request(ability, route + '/SuccessTaskList/2', 4)
    request(ability, route + '/FailedTaskList/2', 3)
    assert fixed(read(ability, '/AbilityList/3/OnStart/6/Value')) == 0
    assert not any(t['$type'].endswith('.SetActionDelay') for t in read(ability, '/AbilityList/4/OnStart'))

    char, ability = avatar_files('Sunday_10')
    entry(char, ability, 55, 3714, 1, 2)
    entry(char, ability, 55, 3729, 2, 5)
    request(ability, '/AbilityList/2/OnStart/3', 3)
    request(ability, '/AbilityList/5/OnStart/2', 6)
    input_params(char, 3714, 'Skill02', [(936398762, 1, 0.15), (-1019408300, 2, 2), (-1204468266, 3, 0.25)])
    separate = read(ability, '/AbilityList/3/OnStart/10/SuccessTaskList/0/SuccessTaskList')
    assert all(t['$type'].endswith('.SetActionDelayNearTarget') and t['NearType'] == 'After' for t in separate)
    assert read(ability, '/AbilityList/6/OnStart/4/DynamicKey') == '_MAXSP'
    input_params(char, 3729, 'Skill03', [(172314977, 0, 0.2)])
    expression(read(ability, '/AbilityList/6/OnStart/5/Value'), 'AQABAQQR', [-1087634200, 172314977])
    trace = read('ExcelOutput/AvatarSkillTreeConfig.json', '/3087')
    assert trace['AvatarID'] == 1313 and trace['PointTriggerKey'] == 'PointB1'
    assert trace['ParamList'][0]['Value'] == 40
    expression(read(ability, '/AbilityList/6/OnStart/8/FixedAddValue'), 'AQAR', [-1835820702])

def tingyun_huohuo():
    char, ability = avatar_files('Tingyun_00')
    entry(char, ability, 22, 940, 2, 5)
    request(ability, '/AbilityList/5/OnStart/5', 6)
    input_params(char, 940, 'Skill03', [(-1349665456, 0, 50), (242053466, 1, 2), (1621744260, 2, 0.2)])
    rank, collision = (read(RANKS, f'/{i}') for i in (149, 143))
    assert rank['RankID'] == read(AVATARS, '/22/RankIDList/5') == 120206
    assert rank['Trigger'] == collision['Trigger'] and collision['RankID'] == 120106
    assert rank['Param'][0]['Value'] == 10
    expression(read(ability, '/AbilityList/6/OnStart/7/SuccessTaskList/0/FixedAddValue'),
               'AQABAQIR', [-1349665456, -1752447704])
    tingyun_tag = read(ability, '/AbilityList/6/OnStart/7/FailedTaskList/0/Tag')

    char, ability = avatar_files('Huohuo_00')
    entry(char, ability, 36, 2045, 2, 5)
    request(ability, '/AbilityList/5/OnStart/1', 6)
    input_params(char, 2045, 'Skill03', [(-668390952, 0, 0.15), (750216344, 1, 0.24), (238783065, 2, 2)])
    gain = read(ability, '/AbilityList/6/OnStart/1')
    assert gain['Tag'] == tingyun_tag == {'EnumIndex': 6, 'Value': 1}
    expression(gain['FixedAddMaxSPRatio'], 'AQAR', [-668390952])
    alias = gain['TargetType']['Alias']
    assert read(TARGETS, f'/AliasDict/{alias}/Alias') == 'AllTeammate - AllTeammate.GetServant'

def robin():
    char, ability = avatar_files('Robin_00')
    entry(char, ability, 52, 2980, 2, 6)
    request(ability, '/AbilityList/6/OnStart/5', 7)
    input_params(char, 2980, 'Skill03', [(1521926375, 1, 90), (1324426262, 3, 0.72)])
    area = read(ability, '/AbilityList/7/OnStart/1/ModifierName/Value')
    area_def = read(ability, f'/GlobalModifiers/{area}')
    start = area_def['_CallbackList'][3]
    assert start['Event'] == 'OnStack'
    sub = start['CallbackConfig'][1]['ModifierName']['Value']
    bonus = start['CallbackConfig'][2]['ModifierName']['Value']
    team = read(ability, f'/GlobalModifiers/{bonus}/_CallbackList/0')
    assert team['Event'] == 'OnStack' and fixed(team['CallbackConfig'][0]['Value']) == 0
    sub_def = read(ability, f'/GlobalModifiers/{sub}')
    create = sub_def['_CallbackList'][1]['CallbackConfig'][0]
    event = read('ExcelOutput/BattleEventConfig.json', '/46')
    assert fixed(create['EventID']) == event['BattleEventID'] == 11309
    assert event['AbilityList'] == [read(ability, '/AbilityList/8/Name')]
    callbacks = read(ability, '/GlobalModifiers/MAvatar_Robin_00_PassiveSkill01_BattleEvent/_CallbackList')
    assert callbacks[0]['Event'] == 'OnPhase1'
    back = callbacks[0]['CallbackConfig'][10]
    assert back['TargetType']['Alias'] == 'BattleEventCaster' and back['ModifierName']['Value'] == area
    assert sub_def['_CallbackList'][0]['CallbackConfig'][1]['PhaseName'] == 'Phase1'

if __name__ == '__main__':
    for case in (asta, bronya_sunday, tingyun_huohuo, robin):
        case()
        print('verified', case.__name__)
