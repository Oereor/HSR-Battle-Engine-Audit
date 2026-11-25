#!/usr/bin/env python3
"""Extract the exact source slices cited by the Modifier report."""
import json
from functools import lru_cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from query import lookup, source

A = 'Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json'
AC = 'Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json'
P = '/GlobalModifiers/MAvatar_Asta_00_Passive_Charge'
R = 'Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json'
RS = '/GlobalModifiers/MAvatar_Robin_00_Skill03Area_sub'
RM = 'Config/ConfigAbility/Avatar/Avatar_RuanMei_00_Ability.json'
RM_PATH = '/GlobalModifiers/MAvatar_RuanMei_PassiveArea_Enemy'
G = 'Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json'
G_PATH = '/ModifierMap/StanceBreakState'
PH = 'Config/ConfigAbility/Avatar/Avatar_Phainon_00_Ability.json'
J = 'Config/ConfigAbility/Avatar/Avatar_JingYuan_00_Ability.json'
SAMPLES = [
    ('M01', 'ExcelOutput/AvatarConfig.json', '/7', 'AvatarID JsonPath SkillList'),
    ('M02', 'ExcelOutput/AvatarSkillConfig.json', '/215', 'SkillID Level SkillTriggerKey ParamList'),
    ('M03', AC, '/SkillList/2', 'Name EntryAbility'),
    ('M04', AC, '/DynamicValues/Floats/812362065', ''),
    ('M05', AC, '/DynamicValues/Floats/242053466', ''),
    ('M06', A, '/AbilityList/5/OnStart/3', ''),
    ('M07', A, '/AbilityList/6/OnStart/2', ''),
    ('M08', A, '/AbilityList/6/Modifiers/MAvatar_Asta_00_Ultra_SpeedUP/_CallbackList/0', ''),
    ('M09', A, '/AbilityList/7/OnStart/0', ''),
    ('M10', A, '/AbilityList/7/Modifiers/M_Asta_Passive/_CallbackList/0/CallbackConfig/0/FailedTaskList/1/SuccessTaskList/1', ''),
    ('M11', A, P, 'LifeStepMoment Stacking Count UIConfig'),
    ('M12', A, P + '/_CallbackList/1/CallbackConfig/3', ''),
    ('M13', A, '/GlobalModifiers/MAvatar_Asta_00_TeamAttackUP/_CallbackList/0/CallbackConfig/1', ''),
    ('M14', A, P + '/_CallbackList/0/CallbackConfig/2', ''),
    ('M15', 'ExcelOutput/AvatarStatusConfig.json', '/41', 'StatusID ModifierName StatusName'),
    ('M16', R, RS + '/_CallbackList/1/CallbackConfig/0', ''),
    ('M17', R, RS + '/_CallbackList/1/CallbackConfig/4', ''),
    ('M18', R, RS + '_disableAction', ''),
    ('M19', R, RS + '/_CallbackList/0/CallbackConfig/3', ''),
    ('M20', G, G_PATH, 'LifeStepMoment PerformTime BehaviorFlagList'),
    ('M21', G, G_PATH + '/_CallbackList/0/CallbackConfig/0', ''),
    ('M22', G, G_PATH + '/_CallbackList/0/CallbackConfig/1', ''),
    ('M23', G, G_PATH + '/_CallbackList/3', ''),
    ('M24', RM, RM_PATH + '/_CallbackList/6', ''),
    ('M25', RM, RM_PATH + '/BehaviorFlagList', ''),
    ('M26', 'Config/ConfigAbility/Avatar/Avatar_Castorice_00_Ability.json', '/AbilityList/8/OnStart/6', ''),
    ('M27', 'Config/ConfigAbility/Monster/Monster_W1_CocoliaP2_00_Ability.json', '/AbilityList/21/Modifiers/EnterBattleRage/_CallbackList/0/CallbackConfig/4', ''),
    ('M28', 'Config/ConfigAbility/Monster/Monster_XP_Elite02_01_Ability.json', '/AbilityList/0/Modifiers/EnterBattleRage/_CallbackList/0', ''),
    ('M29', 'ExcelOutput/EquipmentSkillConfig.json', '/0', 'SkillID Level AbilityName ParamList'),
    ('M30', 'Config/ConfigAbility/EquipmemtAbility.json', '/AbilityList/1/OnStart/0', ''),
    ('M31', 'Config/ConfigAbility/EquipmemtAbility.json', '/AbilityList/1/Modifiers/MEquip_20000_Main/_CallbackList/0/CallbackConfig/0', ''),
    ('M32', 'Config/ConfigAbility/RelicAbility.json', '/AbilityList/7/Modifiers/MRelic_106_Main/_CallbackList/0', ''),
    ('M33', 'Config/ConfigAbility/Servant/Servant_AglaeaServant_00_Ability.json', '/AbilityList/4/Modifiers/MServant_AglaeaServantPassive_DamageAddedRatio/_CallbackList/0/CallbackConfig/0', ''),
    ('M34', 'Config/ConfigCharacter/Avatar/Avatar_Phainon_00_Config.json', '/SkillList/4/UsableConditions/0/UsableCondition', ''),
    ('M35', PH, '/GlobalModifiers/MAvatar_Phainon_00_Ultra/_CallbackList/2/CallbackConfig/1/SuccessTaskList/0/TaskList/0', ''),
    ('M36', J, '/AbilityList/3/OnStart/1', ''),
    ('M37', J, '/GlobalModifiers/MAvatar_JingYuan_00_BattleEvent/_CallbackList/0', ''),
    ('M38', 'Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json', '/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra/_CallbackList/1/CallbackConfig/0/SuccessTaskList/0', ''),
    ('M39', 'Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_Aventurine_00_Ability.json', '/AbilityList/3/OnAdd/1', ''),
    ('M40', 'Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_Aventurine_00_Ability.json', '/AbilityList/3/Modifiers/RTMAvatar_Aventurine_00_StatTracker/_CallbackList/0/Event', ''),
    ('M41', 'Config/ConfigAbility/Avatar/Avatar_Common_Ability.json', '/GlobalModifiers/MAvatar_Common_Departed/_CallbackList/0/CallbackConfig/0', ''),
    ('M42', 'Config/ConfigAbility/Avatar/Avatar_PlayerGirl_00_Ability.json', '/GlobalModifiers/MAvatar_PlayerGirl_00_Ultra_Transform', 'LifeStepMoment LifeTime BehaviorFlagList'),
    ('M43', RM, '/AbilityList/8/OnStart/5/ModifierName', ''),
    ('M44', 'Config/ConfigAbility/Avatar/Avatar_Fugue_00_Ability.json', '/AbilityList/5/Modifiers/MAvatar_Fugue_00_BPSkill/LifeStepMoment', ''),
    ('M45', 'Config/ConfigAbility/BattleEventAbility_2.json', '/AbilityList/0/Modifiers/Modifier_BattleEventAbility_Challenge_Month_16_SuperIce/_CallbackList/3/CallbackConfig/0', ''),
    ('M46', RM, RM_PATH + '/OnDynamicValueChange/0', 'Key ContextScope Ranges'),
    ('M47', 'Config/Gameplays/LittleGame/DiceCombat/DiceCombatSkill_1004.json', '/Modifiers/0', 'ModifierID Flags'),
    ('M48', 'Config/ConfigAbility/Avatar/Avatar_AetherDivide_Perk_Ability.json', '/AbilityList/3/Modifiers/MAvatar_AetherDivide_Add_Perk_0003/_CallbackList/1/CallbackConfig/0/SuccessTaskList/1', ''),
    ('M49', A, P + '/DynamicValues/Floats/-1826473127', ''),
    ('M50', A, '/GlobalModifiers/MAvatar_Asta_00_TeamAttackUP/DynamicValues/Floats/-1826473127', ''),
    ('M51', R, '/GlobalModifiers/MAvatar_Robin_00_Skill03Area/AdditionConfig/SubModifierList/3', ''),
    ('M52', R, '/GlobalModifiers/MAvatar_Robin_00_SkillTree02_InsertDmgUp/_CallbackList/0/Event', ''),
    ('M53', 'Config/ConfigAbility/Activity/Activity_StarFightActivity.json', '/AbilityList/26/Modifiers/Activity_StarFightActivity_09_Taunt', 'TargetSelectRestrict TargetSelectRestrictType BehaviorFlagList UIConfig'),
    ('M54', 'Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_Aventurine_00_Ability.json', '/AbilityList/3/Modifiers/RTMAvatar_Aventurine_00_StatTracker/TickInterval', ''),
]
load = lru_cache(maxsize=5)(source)

def main():
    with (HERE / 'evidence.jsonl').open('w', encoding='utf-8') as output:
        for identifier, path, pointer, fields in SAMPLES:
            node = lookup(load(path), pointer)
            if fields:
                node = {key: node[key] for key in fields.split()}
            record = dict(id=identifier, path=path, pointer=pointer, snippet=node)
            output.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f'validated {len(SAMPLES)} exact source fragments')

if __name__ == '__main__':
    main()
