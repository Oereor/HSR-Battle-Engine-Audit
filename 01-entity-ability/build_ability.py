#!/usr/bin/env python3
"""Build the stage 01 reference tables and static Ability reachability checks."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sqlite3
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from query import connect, lookup, source

REQUESTS = {
    'TriggerAbility': 'trigger-request', 'TriggerParallelAbility': 'parallel-request',
    'AdventureSkillTriggerAbility': 'adventure-trigger-request',
    'TurnInsertAbility': 'insert-ability-request', 'TurnInsertAction': 'insert-action-request',
}
DEPENDENCIES = {
    'OwnerEntityAddAbility': 'install', 'OwnerEntityRemoveAbility': 'remove',
    'AddStageAbilityByName': 'install', 'RemoveStageAbilityByName': 'remove',
    'AbortInsertAbility': 'abort', 'ByCompareUnusedInsertAbilityCount': 'query',
    'SetDynamicValueByBattleTargetID': 'data-reference',
}
FIELDS = {'EntryAbility': 'skill-entry', 'PrepareAbility': 'skill-prepare',
          'RankAbility': 'rank-injection', 'AbilityNameList': 'declared-membership'}
FAMILIES = (
    ('AvatarConfig', 'SkillList', 'AvatarSkillConfig', 'JsonPath'),
    ('AvatarConfigEnhanced', 'SkillList', 'AvatarSkillConfig', 'JsonPath'),
    ('AvatarConfigLD', 'SkillList', 'AvatarSkillConfigLD', 'JsonPath'),
    ('AvatarConfigTrial', 'SkillList', 'AvatarSkillConfigTrial', 'JsonPath'),
    ('AvatarServantConfig', 'SkillIDList', 'AvatarServantSkillConfig', 'Config'),
    ('MonsterConfig', 'SkillList', 'MonsterSkillConfig', None),
    ('BattleEventData', 'SkillIDList', 'BattleEventSkillConfig', 'Config'),
)

def export(name, headers, rows):
    with (HERE / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(headers)
        writer.writerows(rows)

def role(field, parent_type, pointer, kind):
    parent = parent_type.rsplit('.', 1)[-1]
    if kind == 'modifier':
        return 'apply-modifier' if parent in {'AddModifier', 'AddModifierWithPerform'} else 'modifier-reference'
    if kind == 'template':
        return 'template-reference'
    if parent in REQUESTS:
        return REQUESTS[parent]
    if parent in DEPENDENCIES:
        return DEPENDENCIES[parent]
    if field == 'AbilityList':
        return 'skill-membership' if '/SkillAbility' in pointer else 'declared-membership'
    return FIELDS.get(field, 'ability-reference')

def scc(edges):
    """Iterative Kosaraju since paths can contain more than recursion-limit vertices."""
    outward, inward = defaultdict(set), defaultdict(set)
    vertices = set()
    for a, b in edges:
        outward[a].add(b)
        inward[b].add(a)
        vertices.update((a, b))
    visited = set()
    order = []
    for node in sorted(vertices):
        if node in visited:
            continue
        visited.add(node)
        active = [(node, iter(sorted(outward[node])))]
        while active:
            top, children = active[-1]
            nxt = next(children, None)
            if nxt is None:
                order.append(top)
                active.pop()
            elif nxt not in visited:
                visited.add(nxt)
                active.append((nxt, iter(sorted(outward[nxt]))))
    visited.clear()
    for node in reversed(order):
        if node in visited:
            continue
        component = []
        active = [node]
        visited.add(node)
        while active:
            top = active.pop()
            component.append(top)
            for nxt in sorted(inward[top]):
                if nxt not in visited:
                    visited.add(nxt)
                    active.append(nxt)
        if len(component) > 1 or node in outward[node]:
            yield sorted(component)

def master(db, names):
    by_name = defaultdict(list)
    queried = ('ExcelOutput/' + key + '.json' for key in names)
    for path in sorted(queried):
        for pointer, data in db.execute(
            'SELECT pointer,data FROM excel_rows JOIN files ON id=file_id WHERE path=? ORDER BY length(pointer),pointer',
            (path,),
        ):
            by_name[Path(path).stem].append((pointer, json.loads(data)))
    return by_name

def excel_chains(db, definitions):
    names = {table for family in FAMILIES for table in (family[0], family[2])}
    names.update(('MonsterTemplateConfig', 'MonsterTemplateUniqueConfig', 'MonsterSkillUniqueConfig'))
    tables = master(db, names)
    files = {path for (path,) in db.execute("SELECT path FROM files WHERE status='parsed' AND path LIKE 'Config/ConfigCharacter/%'")}
    pointers = {}
    templates = defaultdict(list)
    for table in ('MonsterTemplateConfig', 'MonsterTemplateUniqueConfig'):
        for pointer, row in tables[table]:
            templates[row.get('MonsterTemplateID')].append((f'ExcelOutput/{table}.json', pointer, row.get('JsonConfig')))
    rows = []
    for entity_table, ids_field, skill_table, config_field in FAMILIES:
        skill_rows = defaultdict(list)
        skill_tables = [skill_table]
        if skill_table == 'MonsterSkillConfig':
            skill_tables.append('MonsterSkillUniqueConfig')
        for table in skill_tables:
            for ptr, row in tables[table]:
                skill_rows[row.get('SkillID')].append((f'ExcelOutput/{table}.json', ptr, row))
        for ep, entity in tables[entity_table]:
            chosen_templates = (
                templates.get(entity.get('MonsterTemplateID'), []) or [(None, None, None)]
                if config_field is None else [(None, None, entity.get(config_field))]
            )
            for i, sid in enumerate(entity.get(ids_field, [])):
                for template_path, template_pointer, path in chosen_templates:
                    if path in files and path not in pointers:
                        doc = source(path)
                        names = defaultdict(list)
                        for j, sk in enumerate(doc.get('SkillList', [])):
                            if isinstance(sk, dict):
                                names[sk.get('Name')].append((j, sk))
                        pointers[path] = names
                    for spath, sp, skill in skill_rows.get(sid, [(None, None, {})]):
                        key = skill.get('SkillTriggerKey')
                        matches = pointers.get(path, {}).get(key, []) if key else []
                        for j, sub in matches or [(None, {})]:
                            entry = sub.get('EntryAbility')
                            ptr = f'/SkillList/{j}/EntryAbility' if entry else None
                            status = ('skill-master-missing' if not sp else
                                      'config-path-missing' if path not in files else
                                      'trigger-key-empty' if not key else
                                      'skill-name-missing' if j is None else
                                      'entry-not-present' if not entry else 'entry-observed')
                            rows.append((f'ExcelOutput/{entity_table}.json', f'{ep}/{ids_field}/{i}',
                                         sid, template_path, template_pointer, spath, sp, skill.get('Level'),
                                         key, path, ptr, entry, len(definitions.get(entry, ())), status))
    export('excel-character-skill.tsv',
           ('entity_path', 'entity_skill_id_pointer', 'skill_id', 'template_path', 'template_pointer',
            'skill_master_path', 'skill_master_pointer', 'level', 'skill_trigger_key', 'character_path',
            'entry_pointer', 'entry_ability', 'same_name_definitions', 'join_status'), rows)
    return Counter(row[-1] for row in rows)

def extra_entries(db, definitions):
    """Literal registrations and extension entry points beyond a skill's EntryAbility."""
    fields = {
        'AvatarSkillTreeConfig': ('AbilityName',),
        'AvatarSkillTreeConfigLD': ('AbilityName',),
        'AvatarSkillTreeConfigTrial': ('AbilityName',),
        'AvatarRankConfig': ('RankAbility',),
        'AvatarRankConfigLD': ('RankAbility',),
        'AvatarRankConfigTrial': ('RankAbility',),
        'MonsterConfig': ('AbilityNameList',),
        'EquipmentSkillConfig': ('AbilityName',),
        'RelicSetSkillConfig': ('AbilityName',),
        'BattleEventConfig': ('AbilityList',),
        'StageConfig': ('StageAbilityConfig',),
    }
    entries = []
    for table, rows in master(db, fields).items():
        for pointer, row in rows:
            for key in fields[table]:
                value = row.get(key)
                members = enumerate(value) if isinstance(value, list) else [(None, value)]
                for index, member in members:
                    if not member or not isinstance(member, str):
                        continue
                    location = f'{pointer}/{key}' if index is None else f'{pointer}/{key}/{index}'
                    options = definitions.get(member, ())
                    for d in options or [(None, None, None)]:
                        entries.append((f'ExcelOutput/{table}.json', location, key, member, len(options), d[1], d[2]))
    export('excel-extension-entries.tsv',
           ('path', 'pointer', 'field', 'name', 'candidate_count', 'definition_path', 'definition_pointer'),
           entries)
    return Counter(row[2] for row in entries)

def parameter_checks():
    char = source('Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json')
    ability = source('Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json')
    skills = source('ExcelOutput/AvatarSkillConfig.json')
    points = source('ExcelOutput/AvatarSkillTreeConfig.json')
    checks = [
        ('/AbilityList/1/OnStart/7/AttackProperty/DamagePercentage', skills, 191, 'SkillParam', 'SkillTriggerKey', 0.5),
        ('/AbilityList/6/OnStart/2/DynamicValues/MDF_PropertyValue', skills, 215, 'SkillParam', 'SkillTriggerKey', 36),
        ('/AbilityList/6/OnStart/2/LifeTime', skills, 215, 'SkillParam', 'SkillTriggerKey', 2),
        ('/AbilityList/1/OnStart/6/SuccessTaskList/0/Chance', points, 487, 'SkillTreeParam', 'PointTriggerKey', 0.8),
        ('/AbilityList/1/OnStart/6/SuccessTaskList/0/LifeTime', points, 487, 'SkillTreeParam', 'PointTriggerKey', 3),
    ]
    for position, rows, row_index, kind, key, expected in checks:
        expression = lookup(ability, position)['PostfixExpr']
        dynamic_hash, = expression['DynamicHashes']
        binding = char['DynamicValues']['Floats'][str(dynamic_hash)]['ReadInfo']
        assert binding['Type'] == kind and binding['TriggerKey'] == rows[row_index][key]
        assert rows[row_index]['ParamList'][binding['Index']]['Value'] == expected
    assert skills[192]['SkillID'] == skills[191]['SkillID'] and skills[192]['ParamList'][0]['Value'] == 0.6
    print('parameter bindings: 5 cross-file pointer and ID checks, level 1 vs 2 row verified')

def v2_domains():
    db_path = HERE.parent / 'index' / 'audit-v2.sqlite'
    if not db_path.exists():
        print('optional v2 domain supplement unavailable')
        return
    with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA user_version').fetchone() == (2,)
        rows = db.execute("""
            SELECT path,pointer,name,scope,keys_json
            FROM definition_locations WHERE kind='ability' AND path NOT LIKE 'Config/ConfigAbility/%'
            ORDER BY path,pointer
        """).fetchall()
    export('other-ability-domains-v2.tsv', ('path', 'pointer', 'name', 'scope', 'keys_json'), rows)
    print('additional Ability definitions in v2:', dict(sorted(Counter('/'.join(r[0].split('/')[:3]) for r in rows).items())))

def main():
    with connect() as db:
        all_defs = db.execute(
            'SELECT id,path,pointer,kind,name,scope,keys_json FROM definition_locations ORDER BY path,pointer'
        ).fetchall()
        by_location = {(d[1], d[2]): d for d in all_defs}
        by_name = defaultdict(list)
        for d in all_defs:
            if d[3] == 'ability':
                by_name[d[4]].append(d)
        ability_defs = [d for d in all_defs if d[3] == 'ability']
        export('ability-definitions.tsv', ('id', 'path', 'pointer', 'kind', 'name', 'scope', 'keys_json'), ability_defs)
        refs = db.execute("""
          SELECT id,path,pointer,kind,name,field,parent_type,anchor,anchor_kind,status,candidate_count,
                 def_path,def_pointer
          FROM reference_locations
          WHERE kind='ability' OR (kind IN ('modifier','template') AND anchor_kind IN ('ability','modifier','template'))
          ORDER BY path,pointer
        """)
        ref_rows, graph_rows, ambiguous = [], [], []
        direct_scoped, direct_possible, bridge_possible = set(), set(), set()
        for rid, path, p, kind, name, field, parent, anchor, origin_kind, status, count, dst_path, dst_p in refs:
            origin, dst = by_location.get((path, anchor)), by_location.get((dst_path, dst_p))
            relation = role(field, parent, p, kind)
            record = (rid, path, p, kind, name, field, parent, anchor, origin_kind,
                      status, count, dst_path, dst_p, relation)
            if kind == 'ability':
                ref_rows.append(record)
                if status == 'ambiguous':
                    options = by_name.get(name, ())
                    assert len(options) == count
                    ambiguous.extend((rid, path, p, opt[1], opt[2], name) for opt in options)
            if origin and kind in {'ability', 'modifier', 'template'}:
                graph_rows.append((*record, origin[4], origin[0], dst[0] if dst else None))
            if not (origin and dst):
                continue
            endpoints = (origin[0], dst[0])
            is_request = relation in REQUESTS.values()
            if is_request and origin_kind == 'ability' and kind == 'ability':
                direct_possible.add(endpoints)
                if status == 'scoped':
                    direct_scoped.add(endpoints)
            if is_request or relation in {'apply-modifier', 'template-reference'}:
                bridge_possible.add(endpoints)
        columns = ('id', 'path', 'pointer', 'kind', 'name', 'field', 'parent_type', 'anchor', 'anchor_kind',
                   'status', 'candidate_count', 'def_path', 'def_pointer', 'relation')
        export('ability-references.tsv', columns, ref_rows)
        export('ambiguous-ability-candidates.tsv', ('reference_id', 'path', 'pointer', 'def_path', 'def_pointer', 'name'), ambiguous)
        export('ability-static-graph.tsv', (*columns, 'source_name', 'source_id', 'destination_id'), graph_rows)
        nodes = {d[0]: d for d in all_defs}
        cycle_rows = []
        for name, edges in (('direct-scoped', direct_scoped), ('direct-with-unique-candidates', direct_possible),
                            ('with-modifier-and-template-bridges', bridge_possible)):
            components = sorted(scc(edges), key=lambda component: (-len(component), component))
            print(f'{name}: {len(edges)} unique edges, {len(components)} cyclic SCCs')
            for i, component in enumerate(components, 1):
                for node in component:
                    d = nodes[node]
                    cycle_rows.append((name, i, len(component), d[3], d[4], d[1], d[2]))
        export('static-cycles.tsv', ('graph', 'component', 'size', 'kind', 'name', 'path', 'pointer'), cycle_rows)
        stats = excel_chains(db, by_name)
        extensions = extra_entries(db, by_name)
        print('ability definitions:', len(ability_defs), 'unique names:', len(by_name))
        print('ability field locations:', len(ref_rows), 'statuses:', dict(sorted(Counter(row[9] for row in ref_rows).items())))
        print('ambiguous candidate records:', len(ambiguous), 'typed graph rows (including unresolved):', len(graph_rows))
        print('Excel row levels and config key matches:', dict(sorted(stats.items())))
        print('Excel extension candidate rows by field:', dict(sorted(extensions.items())))
        for path, pointer, expected in (
            ('Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json', '/SkillList/0/EntryAbility', 'Avatar_Asta_00_Skill01_Phase01'),
            ('Config/ConfigCharacter/Monster/Monster_W1_CocoliaP1_01_Config.json', '/SkillList/0/EntryAbility', 'Monster_Boss_Cocolia_P1_Weapon_Skill04_Phase01'),
            ('Config/ConfigCharacter/Servant/Servant_AglaeaServant_00_Config.json', '/SkillList/0/EntryAbility', 'Servant_AglaeaServant_00_Skill11_Phase01'),
        ):
            assert lookup(source(path), pointer) == expected
            assert len(by_name[expected]) == 1
            d = by_name[expected][0]
            assert lookup(source(d[1]), d[2])['Name'] == expected
        assert sorted(scc({(1, 2), (2, 1), (2, 3), (3, 3)})) == [[1, 2], [3]]
        assert db.execute("SELECT count(*) FROM defs WHERE kind='ability'").fetchone()[0] == len(ability_defs)
        parameter_checks()
        print('static checks passed: sample path and unique definition agreement, SCC fixture, and index count')
    v2_domains()

if __name__ == '__main__':
    main()
