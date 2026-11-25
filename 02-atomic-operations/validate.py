#!/usr/bin/env python3
"""Independently check the stage 02 artifacts and cross-context anchors."""
import csv
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from query import connect, lookup, source

def read_tsv(filename):
    with (HERE / filename).open(encoding='utf-8') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))

def original(stem, pointer):
    return lookup(source('Config/ConfigAbility/' + stem + '.json'), pointer)

def check_inventory():
    rows = read_tsv('operations.tsv')
    site_counts = {key: sum(int(row[key]) for row in rows) for key in ('core', 'adjacent', 'special')}
    ids = [row['type'] for row in rows]
    assert len(set(ids)) == len(ids) == 1279
    assert site_counts == {'core': 296845, 'adjacent': 65011, 'special': 2280}, site_counts
    with connect() as db:
        count_map = dict(db.execute('SELECT type,occurrences FROM type_counts'))
    for row in rows:
        assert int(row['all_indexed_occurrences']) == count_map[row['type']]
        expected = sum(int(row[key]) for key in site_counts)
        assert 0 < expected <= count_map[row['type']]
        assert sum(json.loads(row['slots']).values()) == expected
        assert sum(json.loads(row['placement']).values()) == expected
        assert sum(json.loads(row['families']).values()) == expected
        assert json.loads(row['fields'])['$type:str'] == expected
        assert bool(row['contrasting_path']) == (expected > 1)
    for row in read_tsv('semantic-evidence.tsv'):
        raw = lookup(source(row['path']), row['pointer'])
        snippet = json.loads(row['observed_fragment'])
        assert {row['type'], raw['$type'], snippet['$type']} == {row['type']}
        assert snippet.keys() <= raw.keys()
    print(f'{len(ids)} types; {sum(site_counts.values())} nodes; {site_counts}')
    print('All catalogue aggregates match the shared type totals and slot sums.')

def check_raw_anchors():
    a = 'Avatar/Avatar_Asta_00_Ability'
    start = original(a, '/AbilityList/0/OnStart/1')
    normal = original(a, '/AbilityList/1/OnStart/7')
    assert start['AbilityName']['Value'] == original(a, '/AbilityList/1/Name')
    assert normal['AttackProperty']['DamageType']['DamageType'] == 'Fire'
    assert 'AttackType' not in normal['AttackProperty']

    h = 'Avatar/Avatar_Himeko_00_Ability'
    listener = '/AbilityList/7/Modifiers/Avatar_Himeko_Passive1_Modifier/_CallbackList/0/CallbackConfig/0'
    inserted = original(h, listener + '/SuccessTaskList/0/SuccessTaskList/0/SuccessTaskList/0')
    assert inserted['AbilityName']['Value'] == original(h, '/AbilityList/8/Name')
    call = original(h, '/AbilityList/8/OnStart/0/SuccessTaskList/7')
    assert call['AbilityName']['Value'] == original(h, '/AbilityList/9/Name')
    followup = original(h, '/AbilityList/9/OnStart/7')
    assert followup['AttackProperty']['AttackType'] == 'Insert'
    projectile = original('Monster/Monster_W1_Bronya_00_Ability', '/AbilityList/1/OnStart/1/OnProjectileHit/0')
    composite = original('Avatar/Avatar_Klara_00_Ability', '/AbilityList/3/OnStart/3')
    assert composite['$type'] == 'RPG.GameCore.FireWaveProjectile'
    assert {node['$type'] for node in [normal, followup, projectile, composite['PerProjectileDamage']]} == {
        'RPG.GameCore.DamageByAttackProperty'
    }

    c = 'Avatar/Avatar_Acheron_00_Ability'
    fragment = original(c, '/AbilityList/19/OnStart/6/TaskList/0')
    template_path = 'Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json'
    template = lookup(source(template_path), '/TaskListTemplate/30')
    assert fragment['Name'] == template['Name'] == 'Bounce_SelectTarget'
    assert fragment['TemplateParamSequences']['ParamTaskList']['TaskList'][0]['$type'] == normal['$type']
    assert template['TaskList'][0]['TaskList'][0]['$type'].endswith('TaskTemplateFetchParamSequence')
    pairs = [r for r in read_tsv('template-links.tsv') if r['name'] == 'Bounce_SelectTarget']
    assert any(r['static_status'] == 'candidate' and r['def_pointer'] == '/TaskListTemplate/30' for r in pairs)

    start_shield = original('Avatar/Avatar_Mar_7th_00_Ability',
                            '/GlobalModifiers/MAvatar_March7th_00_BPSkill_Shield/_CallbackList')
    assert (start_shield[3]['Event'], start_shield[3]['CallbackConfig'][1]['$type']) == (
        'OnStack', 'RPG.GameCore.InitShield'
    )
    assert (start_shield[1]['Event'], start_shield[1]['CallbackConfig'][0]['$type']) == (
        'OnDestroy', 'RPG.GameCore.RemoveShield'
    )
    aglaea = original('Avatar/Avatar_Aglaea_00_Ability', '/AbilityList/3/OnStart/1/SuccessTaskList/0')
    assert aglaea['ServantID']['FixedValue']['Value'] == lookup(source('ExcelOutput/AvatarServantConfig.json'), '/0/ServantID')
    nova = original('Avatar/Avatar_HimekoNova_00_Ability',
                    '/GlobalModifiers/MAvatar_HimekoNova_00_AssistAsBpSkill/_CallbackList')
    assert nova[1]['CallbackConfig'][0]['OriginalSkillType'] == nova[0]['CallbackConfig'][0]['OriginalSkillType'] == 'Assist'
    assert nova[1]['CallbackConfig'][0]['RegardSkillType'] == 'Skill'
    print('Verified normal / inserted / projectile / composite hit, shield, typed template and servant joins, and skill mapping.')

if __name__ == '__main__':
    check_inventory()
    check_raw_anchors()
