#!/usr/bin/env python3
"""Verify reference counts, primary evidence fragments, and scoped matches."""
from collections import Counter, defaultdict
import csv
import json
import sys

sys.dont_write_bytecode = True
from build_events import HERE, GLOBAL_RULES, connect, lookup, source

def read(name):
    with (HERE / (name + '.tsv')).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    assert all(None not in row and None not in row.values() for row in rows), name
    return rows

def check_source(path, pointer, expected):
    got = lookup(source(path),pointer)
    assert got == expected, (path,pointer,got,expected)

def main():
    callback_rows = read('callback-sites')
    names = defaultdict(set)
    priorities = []
    for row in callback_rows:
        names[row['domain']].add(row['event'])
        priorities.extend(json.loads(row['declaration_fields']).values())
    assert Counter(row['domain'] for row in callback_rows) == {'core':35295,'rt-mode':601}
    assert len(names['core'])==216 and len(names['rt-mode'])==38
    assert len(names['core'] | names['rt-mode'])==224 and len(names['core'] & names['rt-mode'])==30
    assert len(priorities)==1524 and min(priorities)==-101 and max(priorities)==999999
    assert len({(r['path'],r['pointer']) for r in callback_rows})==len(callback_rows)
    assert sum(int(r['sites']) for r in read('callback-catalog'))==len(callback_rows)
    assert all(r['runtime_dispatch']=='Unknown' for r in read('callback-catalog'))
    print(f'callback positions {len(callback_rows)}, distinct raw names 224, priority fields {len(priorities)}')

    hook_rows = read('hook-sites')
    assert len(hook_rows)==83668
    top = Counter(r['hook'] for r in hook_rows if (r['domain'],r['anchor_kind'],r['relative_depth'])
                  ==('core','ability','1'))
    assert top == {'OnStart':11855,'OnAdd':5481,'OnInsertAbort':110,'OnRemove':35}
    assert sum(int(r['sites']) for r in read('hook-catalog'))==len(hook_rows)
    with connect() as db:
        full = db.execute("SELECT count(*) FROM event_locations WHERE form='callback-selector'").fetchone()[0]
        assert full==len(callback_rows)
        assert db.execute("SELECT count(*) FROM type_counts WHERE lower(type) LIKE '%mixtrigger%' OR lower(type) LIKE '%mixability%'").fetchone()==(0,)
        assert db.execute("SELECT count(*) FROM event_locations WHERE lower(name) IN ('mixability','mixtrigger') AND form='container'").fetchone()==(0,)
    print(f'hook/container positions {len(hook_rows)}, direct core lifecycle counts {dict(top)}')

    raw = read('named-event-sites')
    assert len(raw)==38074
    assert len(read('named-event-catalog'))==803
    assert len(read('trigger-type-candidates'))==368
    assert Counter(x['form'] for x in raw if x['domain']=='animation')=={
        'animation-record':18,'animation-state':34560,'animation-group-record':3253}
    sites = read('animation-wait-links')
    assert len(sites)==26 and len({x['event_name'] for x in sites})==16
    assert all(x['status']=='explicit-character-import' for x in sites)
    for site in sites:
        check_source(site['wait_path'],site['wait_pointer']+'/EventName',site['event_name'])
        for char,cp,anim,ap in json.loads(site['explicit_character_imports']):
            check_source(char,cp,anim)
            check_source(anim,ap,site['event_name'])
    print('animation WaitAnimEvent: all 26 locations and linked roots verified')

    flags = source(GLOBAL_RULES)
    assert len(flags['ForbidRecallModifierEventList'])==12
    assert flags['ServantModifierEventWhiteList']==[]
    assert [m['EventType']['Value'] for m in flags['ModifierCustomEvents']
            if m.get('SortBy')=='Phase1Priority']==[1,2,3,4,5,6]
    links = read('custom-event-links')
    assert len(links)==14
    assert Counter(r['status'] for r in links)=={
        'equal-tuple-candidate':6,'producer-only':6,'consumer-only':1,'declaration-only':1}
    custom_sites = read('custom-event-sites')
    assert len(custom_sites)==181
    for row in links:
        check_source(GLOBAL_RULES, row['global_declaration_pointer']+'/BehaviorFlags',
                     json.loads(row['global_behavior_flags']))
    for row in custom_sites:
        check_source(row['path'],row['pointer'],{'EnumIndex':int(row['enum_index']),'Value':int(row['value'])})
    assert len(read('global-event-policies'))==3
    print('14 declared custom event tokens and 181 exact references verified')

    token = {'EnumIndex':4,'Value':13}
    mod_path = 'Config/ConfigAbility/Avatar/Avatar_Nihilux_10_Ability.json'
    mod_ptr = '/AbilityList/16/Modifiers/MAvatar_Nihilux_10_SkillAeon_DirtyHP_Property'
    cb = mod_ptr+'/_CallbackList/1'
    check_source(GLOBAL_RULES,'/ModifierCustomEvents/8',{'BehaviorFlags':[1006],'EventType':token})
    check_source(mod_path,mod_ptr+'/BehaviorFlagList',[1006,'KeepOnDeathrattle'])
    check_source(mod_path,cb+'/Event','OnCustomEvent')
    check_source(mod_path,cb+'/CallbackConfig/0/Predicate/PredicateList/1/EventType',token)
    check_source(mod_path,cb+'/CallbackConfig/0/SuccessTaskList/0/Value/FixedValue/Value',0)
    check_source('Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json','/TaskListTemplate/0/TaskList/0/EventType',token)
    check_source(GLOBAL_RULES,'/ModifierBehaviorFlagEventMap/501/ModifierBehaviorFlagEventConfigs/0/CallbackConfig/0/Condition/PredicateList/0/TargetTypeB/Alias','CallBackModifierCaster')
    check_source('Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json','/GlobalModifiers/MAvatar_Robin_00_SkillRank04_DispelControl/_CallbackList/1/CallbackConfig/0/$type','RPG.GameCore.RemoveSelfModifier')
    print('three-way (4,13) and behavior-flag/RemoveSelfModifier samples verified')

if __name__ == '__main__':
    main()
