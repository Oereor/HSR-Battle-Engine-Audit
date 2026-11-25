#!/usr/bin/env python3
"""Verify specific resource case joins using the local, read-only data source."""

from functools import cache
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from probe_named_values import alternating_djb2
from query import lookup, source


@cache
def read(path):
    return source(path)


def avatar(name, pointer='', ability=True):
    directory, tail = ('ConfigAbility', 'Ability') if ability else ('ConfigCharacter', 'Config')
    return lookup(read(f'Config/{directory}/Avatar/Avatar_{name}_00_{tail}.json'), pointer)


def excel(table, pointer):
    return lookup(read(f'ExcelOutput/{table}.json'), pointer)


def read_info(name, key, source_type, trigger, index):
    assert avatar(name, f'/DynamicValues/Floats/{key}/ReadInfo', ability=False) == {
        'Type': source_type, 'TriggerKey': trigger, 'Index': index,
    }


def operation(node, suffix):
    assert node['$type'] == f'RPG.GameCore.{suffix}'


def call(name, pointer, target):
    node = avatar(name, pointer)
    operation(node, 'TriggerAbility')
    assert node['AbilityName']['Value'] == avatar(name, f'/AbilityList/{target}/Name')


def binding(name, row, data_key, key, trigger, index, expected, source_type='SkillParam',
            table='AvatarSkillConfig'):
    read_info(name, key, source_type, trigger, index)
    assert excel(table, f'/{row}/{data_key}/{index}/Value') == expected


def acheron():
    name = 'Acheron'
    assert excel('AvatarConfig', '/51/AvatarID') == 1308
    call(name, '/AbilityList/5/OnStart/8', 6)
    call(name, '/AbilityList/17/OnStart/0/SuccessTaskList/0', 18)
    call(name, '/AbilityList/18/OnStart/7', 19)
    binding(name, 2546, 'ParamList', 1525852618, 'Skill02', 2, 1)
    binding(name, 2576, 'ParamList', 1483210409, 'SkillP01', 0, 9)
    binding(name, 2887, 'ParamList', -590721991, 'PointB1', 1, 3, 'SkillTreeParam',
            'AvatarSkillTreeConfig')
    binding(name, 2, 'NNACKOBKFGE', 21888035, 'ExRank01', 1, 1, 'SkillRank',
            'AvatarExRankConfig')
    passive = '/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra'
    attach = avatar(name, passive + '/_CallbackList/7/CallbackConfig/0')
    assert (attach['TargetType']['Alias'], attach['ModifierName']['Value']) == (
        'AllEnemy', 'MAvatar_Acheron_00_OnListenDeBuffAdd',
    )
    listen = avatar(name, '/GlobalModifiers/MAvatar_Acheron_00_OnListenDeBuffAdd/_CallbackList/0')
    assert listen['Event'] == 'OnModifierOnStack'
    gate = listen['CallbackConfig'][0]
    assert gate['Predicate']['PredicateList'][0]['TargetStatusType'] == 'Debuff'
    add = lookup(gate, '/SuccessTaskList/0/SuccessTaskList/0')
    operation(add, 'ModifySpecialSP')
    assert add['FixedAddValue']['FixedValue']['Value'] == 1
    watcher = avatar(name, passive + '/OnAbilityPropertyChange/0')
    assert watcher['Property'] == 'CurrentSpecialSP' and lookup(watcher, '/Ranges/0/TriggerClampedChange')
    assert lookup(watcher, '/Ranges/0/OnChange/0/Name') == avatar(
        name, passive + '/TaskListTemplate/0/Name')
    full = lookup(watcher, '/Ranges/0/OnChange/1/SuccessTaskList/0/SuccessTaskList')
    add_layer = lookup(full, '/1/SuccessTaskList/0')
    assert lookup(add_layer, '/MaxLayer/PostfixExpr/DynamicHashes') == [-590721991]
    assert lookup(add_layer, '/LayerAddWhenStack/PostfixExpr/DynamicHashes') == [
        alternating_djb2(full[0]['DynamicKey']),
    ]


def archer_danhengil():
    name = 'Archer'
    assert excel('AvatarSkillConfigLD', '/76/BPNeed/Value') == 2
    assert excel('AvatarConfigLD', '/1/RankIDList/0') == excel('AvatarRankConfigLD', '/6/RankID') == 101501
    binding(name, 6, 'Param', 952868987, 'Rank01', 0, 3, 'SkillRank', 'AvatarRankConfigLD')
    binding(name, 6, 'Param', 1424168145, 'Rank01', 1, 2, 'SkillRank', 'AvatarRankConfigLD')
    call(name, '/AbilityList/2/OnStart/7', 3)
    call(name, '/AbilityList/4/OnStart/3', 5)
    by_need = avatar(name, '/AbilityList/3/OnStart/13')
    assert by_need['PropertyType'] == 'BPNeed' and by_need['SkillTriggerKey'] == 'Skill02'
    assert avatar(name, '/AbilityList/3/OnStart/14/Predicate/PredicateList/0/CompareValue/PostfixExpr/DynamicHashes') == [
        alternating_djb2(by_need['DynamicKey']),
    ]
    assert avatar(name, '/AbilityList/3/OnStart/10/Predicate/TriggerKey/Hash') == excel(
        'AvatarRankConfigLD', '/6/Trigger/Hash')
    bonus = avatar(name, '/GlobalModifiers/MAvatar_Archer_00_BonusTrigger/_CallbackList/1')
    assert bonus['Event'] == 'OnListenAfterAction'
    ins = lookup(bonus, '/CallbackConfig/1/SuccessTaskList/1/SuccessTaskList/0')
    operation(ins, 'TurnInsertAction')
    assert ins['SkillType'] == 'ControlSkill02' and ins['CustomTags'][0]['Value'] == 'Archer_Bonus'
    operation(ins['OnInsertAbort'][1], 'RemoveSelfModifier')

    name = 'DanHengIL'
    assert excel('AvatarConfig', '/33/AvatarID') == 1213
    call(name, '/AbilityList/8/OnStart/1', 9)
    for tier, row, effect in [(1, 1333, 3), (2, 1342, 5), (3, 1351, 7)]:
        trigger = f'Skill1{tier}'
        entry = avatar(name, f'/SkillList/{tier + 2}', ability=False)
        assert entry['EntryAbility'] == avatar(name, f'/AbilityList/{effect - 1}/Name')
        assert entry['Name'] == excel('AvatarSkillConfig', f'/{row}/SkillTriggerKey') == trigger
        assert excel('AvatarSkillConfig', f'/{row}/BPNeed/Value') == tier
        modifier = f'/AbilityList/9/Modifiers/MAvatar_DanHengIL_00_BPCost_{tier}/_CallbackList'
        stack = avatar(name, modifier + '/1')
        restore = avatar(name, modifier + '/0')
        assert stack['Event'] == 'OnStack' and restore['Event'] == 'OnDestroy'
        assert [t['SkillTriggerKey'] for t in stack['CallbackConfig']
                if t['$type'].endswith('.SetControlSkillMapping')][0] == trigger
        props = next(t['Properties'] for t in stack['CallbackConfig']
                     if t['$type'].endswith('.ModifySkillPropertyByName'))
        assert lookup(props, '/0/Value/FixedValue/Value') == tier
        assert lookup(restore, '/CallbackConfig/1/Properties/0/OperatorType') == 'Unset'


def sparkle_sparxie():
    name = 'Sparkle'
    assert excel('AvatarConfig', '/49/AvatarID') == 1306
    assert excel('AvatarConfig', '/49/RankIDList/3') == excel('AvatarRankConfig', '/321/RankID') == 130604
    binding(name, 3209, 'ParamList', -1284285354, 'SkillP01', 2, 2)
    binding(name, 3194, 'ParamList', 419301503, 'Skill03', 1, 4)
    call(name, '/AbilityList/6/OnStart/2', 7)
    stock = avatar(name, '/AbilityList/7/OnStart/2/FailedTaskList/0')
    operation(stock, 'ModifyTeamBoostPoint')
    assert lookup(stock, '/ModifyValue/PostfixExpr/DynamicHashes') == [419301503]
    listener = '/AbilityList/9/Modifiers/Avatar_Sparkle_00_PassiveSkill_Listen/_CallbackList'
    assert avatar(name, listener + '/0/Event') == 'OnCreate'
    cap = avatar(name, listener + '/0/CallbackConfig/0/FailedTaskList/0')
    operation(cap, 'ModifyTeamBoostPointMax')
    assert lookup(cap, '/ModifyValue/PostfixExpr/DynamicHashes') == [-1284285354]

    name = 'Sparxie'
    assert excel('AvatarConfig', '/74/AvatarID') == 1501
    assert excel('AvatarConfig', '/74/RankIDList/1') == excel('AvatarRankConfig', '/481/RankID') == 150102
    binding(name, 481, 'Param', -1937183604, 'Rank02', 0, 2, 'SkillRank', 'AvatarRankConfig')
    binding(name, 5485, 'ParamList', -851278791, 'Skill21', 0, 2)
    call(name, '/AbilityList/2/OnStart/7', 3)
    call(name, '/AbilityList/4/OnStart/1', 5)
    call(name, '/AbilityList/11/OnStart/2', 12)
    operation(avatar(name, '/AbilityList/12/OnStart/6'), 'ModifyEntityBoostPoint')
    prize = avatar(name, '/GlobalTemplates/3')
    assert prize['Name'] == avatar(name, '/AbilityList/5/OnStart/0/SuccessTaskList/0/Name')
    assert lookup(prize, '/TaskList/3/ModifyValue/PostfixExpr/DynamicHashes') == [-851278791]


def phainon():
    name = 'Phainon'
    assert excel('AvatarConfig', '/67/AvatarID') == 1408
    binding(name, 4221, 'ParamList', 766439870, 'Skill03', 3, 8)
    binding(name, 4349, 'ParamList', -911674397, 'SkillP02', 3, 0.4)
    binding(name, 4349, 'ParamList', -1930233400, 'SkillP02', 4, 1.35)
    call(name, '/AbilityList/17/OnStart/5', 18)
    call(name, '/AbilityList/21/OnStart/0/TaskList/0', 22)
    call(name, '/AbilityList/22/OnStart/6', 23)
    loop = avatar(name, '/AbilityList/18/OnStart/4')
    assert lookup(loop, '/MaxLoopCount/PostfixExpr/DynamicHashes') == [766439870]
    ev = lookup(loop, '/TaskList/0')
    assert lookup(ev, '/DynamicValues/BE_Count/PostfixExpr/DynamicHashes') == [766439870]
    assert lookup(ev, '/EventID/FixedValue/Value') == excel('BattleEventConfig', '/50/BattleEventID') == 11408
    assert excel('BattleEventConfig', '/50/AbilityList/0') == avatar(name, '/AbilityList/19/Name')
    flag = '/AbilityList/19/Modifiers/MAvatar_Phainon_00_Skill03_BattleEvent_Passive/_CallbackList/1'
    assert avatar(name, flag + '/Event') == 'OnPhase1'
    request = avatar(name, flag + '/CallbackConfig/0/SuccessTaskList/0')
    operation(request, 'TurnInsertAbility')
    assert request['AbilityName']['Value'] == avatar(name, '/AbilityList/21/Name')
    operation(avatar(name, flag + '/CallbackConfig/0/FailedTaskList/1'), 'TurnInsertAction')
    charge = '/GlobalTemplates/1/TaskList/0/TaskList/0'
    assert avatar(name, charge + '/FailedTaskList/0/Key/Value') == 'CurOverflowSpecialSP'
    assert avatar(name, charge + '/SuccessTaskList/0/FixedAddValue/FixedValue/Value') == 1
    overflow_key = avatar(name, charge + '/FailedTaskList/0/Key/Value')
    watcher = '/AbilityList/24/Modifiers/MAvatar_Phainon_00_PassiveSkill01/OnDynamicValueChange/0'
    assert avatar(name, watcher + '/Key/Hash') == alternating_djb2(overflow_key)
    attach = avatar(name, watcher + '/Ranges/0/OnChange/0/SuccessTaskList/2/SuccessTaskList/0/SuccessTaskList/0')
    assert attach['ModifierName']['Value'] == 'MAvatar_Phainon_00_SPOverflow'
    assert lookup(attach, '/DynamicValues/MDF_Count/PostfixExpr/DynamicHashes') == [alternating_djb2(overflow_key)]
    restock = avatar(name, '/GlobalModifiers/MAvatar_Phainon_00_SPOverflow/_CallbackList/0/CallbackConfig/1')
    assert restock['Name'] == avatar(name, '/GlobalTemplates/1/Name')
    assert lookup(restock, '/DynamicValues/Arg0_AddValue/PostfixExpr/DynamicHashes') == [alternating_djb2('MDF_Count')]


if __name__ == '__main__':
    for check in (acheron, archer_danhengil, sparkle_sparxie, phainon):
        check()
        print('verified', check.__name__)
