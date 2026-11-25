#!/usr/bin/env python3
"""Index local JSON as data, one file at a time, without executing any contents."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'TurnBasedGameData'
DATABASE = ROOT / 'index' / 'audit.sqlite'
SCHEMA = """
CREATE TABLE files(id INTEGER PRIMARY KEY, path TEXT UNIQUE, bytes INTEGER, sha256 TEXT,
 bucket TEXT, status TEXT, root_shape TEXT, error TEXT);
CREATE TABLE types(file_id INTEGER, pointer TEXT, type TEXT, parent_field TEXT,
 parent_type TEXT, in_array INTEGER, anchor TEXT, anchor_kind TEXT, child_keys TEXT);
CREATE TABLE fields(type TEXT, field TEXT, shape TEXT, count INTEGER);
CREATE TABLE defs(id INTEGER PRIMARY KEY, file_id INTEGER, pointer TEXT, kind TEXT,
 name TEXT, scope TEXT, keys_json TEXT);
CREATE TABLE refs(id INTEGER PRIMARY KEY, file_id INTEGER, pointer TEXT, kind TEXT,
 name TEXT, field TEXT, parent_type TEXT, anchor TEXT, anchor_kind TEXT);
CREATE TABLE events(file_id INTEGER, pointer TEXT, name TEXT, form TEXT, anchor TEXT,
 anchor_kind TEXT, issuer_type TEXT);
CREATE TABLE excel_rows(file_id INTEGER, pointer TEXT, data TEXT);
CREATE TABLE resolved(ref_id INTEGER PRIMARY KEY, status TEXT, candidate_count INTEGER, def_id INTEGER);
CREATE TABLE excel_edges(file_id INTEGER, pointer TEXT, field TEXT, value TEXT,
 target_file_id INTEGER, target_pointer TEXT, key_field TEXT);
CREATE TABLE shapes(file_id INTEGER, pointer TEXT, role TEXT, field TEXT, value TEXT);
"""
MASTER = re.compile(r'^(Avatar(?:Config|Skill|Rank|Enhanced|Servant|ExRank|SpecialSkill|LevelSkill)|'
                    r'Monster(?:Config|Template|Skill)|Battle(?:Event|ActionEvent|Condition|Target)|'
                    r'Stage(?:Config|Infinite|Event)|Equipment(?:Config|Skill)|RelicSet|SummonUnit|Servant|'
                    r'(?:MazeSkill|Elation|FinalityBattle|ChallengePeak|RogueBuff))')
ABILITY_FIELDS = {
    'AbilityName', 'AbilityNameList', 'AbilityList', 'EntryAbility', 'PrepareAbility',
    'RankAbility', 'PointAbilityList', 'ExtraAbility', 'ExtraAbilityList', 'Ability',
    'AbilityNameOnSuccess', 'AbilityNames', 'AbilityNameListInBattle',
}
MODIFIER_FIELDS = {'ModifierName', 'ModifierNameList', 'ModifierNames', 'ModName',
                   'Modifier', 'ModifierList', 'GlobalModifierName', 'GlobalModifierList'}
MAP_DEFS = {'GlobalModifiers': 'modifier', 'Modifiers': 'modifier', 'ModifierMap': 'modifier',
            'GlobalTargetAlias': 'alias'}
LIST_DEFS = {'AbilityList': 'ability', 'TaskListTemplate': 'template',
             'GlobalTemplates': 'template', 'PoolList': 'skill_pool'}
KEYS = {'AbilityName', 'ModifierName', 'SkillType', 'TargetType', 'SubTargetType', 'ContextScope',
        'DynamicKey', 'EventName', 'AnimStateName', 'Stacking', 'LifeStepMoment', 'BehaviorFlagList',
        'BPNeed', 'SPNeed', 'Skill', 'Alias', 'Order', 'Priority', 'SkillName'}
FILE_SUFFIX = ('.json',)
EVENT_CONTAINERS = {'_CallbackList', 'CallbackList', 'MixTrigger', 'MixAbility'}
PHASE = re.compile(r'^On[A-Z]')
LINKS = {
  'AvatarConfig': {'SkillList': [('AvatarSkillConfig', 'SkillID')], 'RankIDList': [('AvatarRankConfig','RankID')]},
  'AvatarConfigEnhanced': {'SkillList': [('AvatarEnhancedSkill', 'SkillID')], 'RankIDList': [('AvatarEnhancedRank','RankID')]},
  'AvatarServantConfig': {'SkillIDList': [('AvatarServantSkillConfig','SkillID')], 'HPSkill': [('AvatarSkillConfig','SkillID')], 'SpeedSkill': [('AvatarSkillConfig','SkillID')]},
  'MonsterConfig': {'MonsterTemplateID': [('MonsterTemplateConfig','MonsterTemplateID')], 'SkillList': [('MonsterSkillConfig','SkillID')]},
  'EquipmentConfig': {'SkillID': [('EquipmentSkillConfig','SkillID')]},
  'RelicSetSkillConfig': {'SetID': [('RelicSetConfig','SetID')]},
  'StageConfig': {'MonsterList': [('MonsterConfig','MonsterID')]},
  'BattleEventConfig': {'BattleEventID': [('BattleEventSkillConfig','BattleEventID'),('BattleEventData','BattleEventID')]},
}

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

def pointer(path, part):
    return path + '/' + str(part).replace('~', '~0').replace('/', '~1')

def shape(value):
    return 'null' if value is None else type(value).__name__

def files():
    for parent, dirs, names in os.walk(SOURCE, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != '.git' and not (Path(parent) / d).is_symlink())
        for name in sorted(names):
            path = Path(parent) / name
            if path.is_file() and not path.is_symlink():
                yield path, path.relative_to(SOURCE).as_posix()

def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def bucket(rel):
    if not rel.endswith(FILE_SUFFIX):
        return 'non-json'
    if rel.endswith('.layout.json'):
        return 'layout'
    if rel.startswith('TextMap/'):
        return 'text'
    if rel.startswith(('Config/', 'Stages/', 'ExcelOutput/', 'Story/')):
        return 'scan'
    return 'other-json'

class Scanner:
    def __init__(self, connection, file_id, path, version):
        self.db = connection
        self.file_id = file_id
        self.path = path
        self.extended = version >= 2
        self.ability_container = path.startswith('Config/ConfigAbility/')
        self.modifier_container = path.startswith('Config/ConfigGlobalModifier/')
        self.root_excel = path.startswith('ExcelOutput/') and MASTER.match(Path(path).stem)
        self.records = collections.defaultdict(list)
        self.fields = collections.Counter()

    def record(self, table, *values):
        self.records[table].append((self.file_id, *values))

    def definition(self, p, kind, name, scope, obj):
        self.record('defs', p, kind, name, scope, dump(sorted(obj)))

    def symbol(self, value, p, field, ptype, anchor, kind):
        if not value or not isinstance(value, str):
            return
        if self.extended and field == 'Name' and ptype.endswith('.IncludeTaskListTemplate'):
            tag = 'template'
        elif field in ABILITY_FIELDS or re.search(r'(?:AbilityName|AbilityNameList|EntryAbility)$', field):
            tag = 'ability'
        elif field in MODIFIER_FIELDS or re.search(r'(?:ModifierName|ModifierNameList)$', field):
            tag = 'modifier'
        elif field == 'Alias' and ptype and 'Target' in ptype:
            tag = 'alias'
        elif 'Template' in field and ('Task' in field or ptype and 'Template' in ptype):
            tag = 'template'
        elif value.endswith('.json') and value.startswith(('Config/', 'Stages/', 'ExcelOutput/', 'Story/')):
            tag = 'file'
        else:
            return
        self.record('refs', p, tag, value, field, ptype, *anchor)

    def walk(self, obj, p='', field='', parent_type='', array=False, anchor=('', ''),
             inherited_ref='', context=''):
        if isinstance(obj, dict):
            local_type = obj.get('$type')
            valid_type = isinstance(local_type, str)
            ability_slot = self.ability_container or self.extended and re.fullmatch(r'/AbilityList/\d+', p)
            if ability_slot and field == 'AbilityList' and array and isinstance(obj.get('Name'), str):
                self.definition(p, 'ability', obj['Name'], 'file', obj)
                anchor = (p, 'ability')
            elif field in LIST_DEFS and array and field != 'AbilityList':
                name = obj.get('Name', obj.get('UniqueName'))
                if isinstance(name, str):
                    self.definition(p, LIST_DEFS[field], name, 'file', obj)
                    anchor = (p, LIST_DEFS[field])
            if valid_type:
                self.record('types', p, local_type, field, parent_type, int(array), *anchor,
                            dump(sorted(obj)))
                self.fields.update((local_type, k, shape(v)) for k, v in obj.items())
            next_type = local_type if valid_type else parent_type
            if field in EVENT_CONTAINERS or 'CallbackConfig' in obj:
                event = obj.get('Event', obj.get('EventName'))
                if isinstance(event, (str, int)) and not isinstance(event, bool):
                    event_field = 'Event' if 'Event' in obj else 'EventName'
                    self.record('events', pointer(p, event_field), str(event), 'callback-selector', *anchor, next_type)
            if array and isinstance(obj.get('EventName'), str) and self.path.startswith('Config/ConfigAnimEvents/'):
                self.record('events', pointer(p, 'EventName'), obj['EventName'], 'animation-record', *anchor, next_type)
            if self.extended and array and self.path.startswith('Config/ConfigAnimEvents/'):
                state = obj.get('AnimatorStateName')
                if isinstance(state, str):
                    self.record('events', pointer(p, 'AnimatorStateName'), state, 'animation-state', *anchor, next_type)
                if field in {'AnimatorStateGroupEvents','AnimatorBehaviourEvents'}:
                    self.record('events', p, field, 'animation-group-record', *anchor, next_type)
            if not p and self.root_excel:
                self.record('excel_rows', p, dump(obj))
            for k, value in obj.items():
                pp = pointer(p, k)
                if isinstance(value, dict) and k in MAP_DEFS and (
                    k == 'GlobalTargetAlias' or k == 'Modifiers' and anchor[1] == 'ability'
                    or k == 'GlobalModifiers' and (self.ability_container or self.extended and not p)
                    or k == 'ModifierMap' and (self.modifier_container or self.extended and not p)):
                    for name, member in value.items():
                        if not isinstance(member, dict):
                            continue
                        dp = pointer(pp, name)
                        definition_kind = MAP_DEFS[k]
                        self.definition(dp, definition_kind, name, anchor[0] if k == 'Modifiers' else k, member)
                        self.walk(member, dp, k, next_type, anchor=(dp, definition_kind))
                    continue
                if k in EVENT_CONTAINERS or k == 'CallbackConfig' or PHASE.match(k) and isinstance(value, (list, dict)):
                    self.record('events', pp, k, 'container' if k in EVENT_CONTAINERS or k == 'CallbackConfig' else 'hook', *anchor, next_type)
                if k in KEYS and ((anchor[1] or valid_type) or k in {'SkillType', 'BPNeed', 'SPNeed', 'Skill'}):
                    self.record('shapes', pp, anchor[1], k, dump(value))
                if k == 'EventName' and isinstance(value, str) and not self.path.startswith('Config/ConfigAnimEvents/'):
                    self.record('events', pp, value, 'named-event-field', *anchor, next_type)
                if k == 'EventType' and ('Event' in next_type or 'Callback' in next_type):
                    self.record('events', pp, dump(value), 'event-type-field', *anchor, next_type)
                ref_field = inherited_ref if k == 'Value' and inherited_ref else k
                self.walk(value, pp, k, next_type, anchor=anchor, inherited_ref=ref_field)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                pp = pointer(p, i)
                if not p and self.root_excel and isinstance(item, dict):
                    self.record('excel_rows', pp, dump(item))
                self.walk(item, pp, field, parent_type, True, anchor, inherited_ref)
        elif isinstance(obj, str):
            self.symbol(obj, p, inherited_ref or field, parent_type, anchor, anchor[1])

    def insert(self):
        for name, rows in self.records.items():
            if name == 'defs':
                sql = 'INSERT INTO defs(file_id,pointer,kind,name,scope,keys_json) VALUES (?,?,?,?,?,?)'
            elif name == 'refs':
                sql = 'INSERT INTO refs(file_id,pointer,kind,name,field,parent_type,anchor,anchor_kind) VALUES (?,?,?,?,?,?,?,?)'
            else:
                template = ','.join('?' for _ in rows[0])
                sql = f'INSERT INTO {name} VALUES ({template})'
            self.db.executemany(sql, rows)

def finalize(db):
    db.executescript("""
    CREATE INDEX types_name ON types(type);
    CREATE INDEX types_file ON types(file_id,anchor);
    CREATE INDEX defs_name ON defs(kind,name);
    CREATE INDEX defs_file ON defs(file_id,pointer);
    CREATE INDEX refs_name ON refs(kind,name);
    CREATE INDEX refs_file ON refs(file_id,anchor);
    CREATE INDEX events_name ON events(name,form);
    CREATE INDEX events_file ON events(file_id,anchor);
    CREATE INDEX shapes_field ON shapes(field);
    CREATE INDEX shapes_file ON shapes(file_id);
    CREATE INDEX excel_file ON excel_rows(file_id);
    CREATE VIEW type_counts AS
      SELECT type, count(*) occurrences, count(DISTINCT file_id) files FROM types GROUP BY type;
    CREATE VIEW type_context AS
      SELECT type,parent_field,parent_type,in_array,anchor_kind,count(*) occurrences
      FROM types GROUP BY 1,2,3,4,5;
    CREATE VIEW occurrences AS
      SELECT f.path,t.pointer,t.type,t.parent_field,t.parent_type,t.in_array,t.anchor,t.anchor_kind
      FROM types t JOIN files f ON f.id=t.file_id;
    CREATE VIEW definition_locations AS
      SELECT d.id,f.path,d.pointer,d.kind,d.name,d.scope,d.keys_json FROM defs d JOIN files f ON f.id=d.file_id;
    CREATE VIEW event_locations AS
      SELECT f.path,e.pointer,e.name,e.form,e.anchor,e.anchor_kind,e.issuer_type FROM events e JOIN files f ON f.id=e.file_id;
    CREATE VIEW reference_locations AS
      SELECT r.id,f.path,r.pointer,r.kind,r.name,r.field,r.parent_type,r.anchor,r.anchor_kind,
             s.status,s.candidate_count,d.path AS def_path,d.pointer AS def_pointer
      FROM refs r JOIN files f ON f.id=r.file_id JOIN resolved s ON s.ref_id=r.id
      LEFT JOIN definition_locations d ON d.id=s.def_id;
    """)
    definitions = collections.defaultdict(list)
    for row in db.execute('SELECT id,file_id,pointer,kind,name,scope FROM defs'):
        definitions[row[3], row[4]].append(row)
    path_ids = dict(db.execute('SELECT path,id FROM files'))
    batch = []
    for rid, fid, p, k, n, field, ptype, anchor, ak in db.execute('SELECT * FROM refs'):
        candidates = definitions[k, n]
        if k == 'file':
            exists = n in path_ids
            result = ('confirmed' if exists else 'unresolved', int(exists), None)
        else:
            same = [d for d in candidates if d[1] == fid]
            lexical = [d for d in same if d[5].startswith('/') and (anchor == d[5] or anchor.startswith(d[5] + '/'))]
            visible_file = [d for d in same if not d[5].startswith('/')]
            selected = lexical or visible_file
            if len(selected) == 1:
                result = ('scoped', len(candidates), selected[0][0])
            elif not candidates:
                result = ('unresolved', 0, None)
            elif len(candidates) == 1:
                result = ('candidate', 1, candidates[0][0])
            else:
                result = ('ambiguous', len(candidates), None)
        batch.append((rid, *result))
    db.executemany('INSERT INTO resolved VALUES (?,?,?,?)', batch)
    db.execute('CREATE INDEX resolved_status ON resolved(status)')
    db.execute('ANALYZE')

def excel_links(db, version):
    tables = collections.defaultdict(list)
    for fid, path, p, data in db.execute('SELECT e.file_id,f.path,e.pointer,e.data FROM excel_rows e JOIN files f ON f.id=e.file_id'):
        tables[Path(path).stem].append((fid, p, json.loads(data)))
    targets = collections.defaultdict(list)
    rules_by_table = LINKS
    if version >= 2:
        rules_by_table = {
            **LINKS,
            'AvatarConfigEnhanced': {
                'SkillList': [('AvatarSkillConfig','SkillID'),('AvatarEnhancedSkill','SkillID')],
                'RankIDList': [('AvatarRankConfig','RankID'),('AvatarEnhancedRank','RankID')],
            },
            'AvatarConfigLD': {'SkillList': [('AvatarSkillConfigLD','SkillID')], 'RankIDList': [('AvatarRankConfigLD','RankID')]},
            'AvatarConfigTrial': {'SkillList': [('AvatarSkillConfigTrial','SkillID')], 'RankIDList': [('AvatarRankConfigTrial','RankID')]},
            'BattleEventConfig': {'BattleEventID': [('BattleEventData','BattleEventID')]},
            'BattleEventConfigLD': {'BattleEventID': [('BattleEventDataLD','BattleEventID')]},
            'BattleEventData': {'SkillIDList': [('BattleEventSkillConfig','SkillID')]},
            'BattleEventDataLD': {'SkillIDList': [('BattleEventSkillConfigLD','SkillID')]},
        }
    for table, key in sorted({pair for rules in rules_by_table.values() for pairs in rules.values() for pair in pairs}):
        for fid, p, row in tables[table]:
            value = row.get(key)
            if isinstance(value, (int, str)) and value != '':
                targets[table, key, value].append((fid, p))
    edges = []
    for table, rules in rules_by_table.items():
        for fid, p, row in tables[table]:
            for field, specs in rules.items():
                values = row.get(field)
                if values is None:
                    continue
                if isinstance(values, list):
                    members = []
                    for i, value in enumerate(values):
                        sub = pointer(pointer(p, field), i)
                        if field == 'MonsterList' and isinstance(value, dict):
                            members.extend((pointer(sub, k), v) for k, v in value.items() if k.startswith('Monster'))
                        else:
                            members.append((sub, value))
                else:
                    members = [(pointer(p, field), values)]
                for loc, value in members:
                    if not isinstance(value, (int, str)) or value in ('', 0):
                        continue
                    for target, key in specs:
                        matches = targets[target, key, value] or [(None, None)]
                        edges.extend((fid, loc, field, dump(value), tid, tp, f'{target}.{key}') for tid, tp in matches)
    db.executemany('INSERT INTO excel_edges VALUES (?,?,?,?,?,?,?)', edges)
    db.execute('CREATE INDEX excel_edges_file ON excel_edges(file_id,pointer)')

def build(database, version):
    pending = database.with_suffix('.building.sqlite')
    if pending.exists():
        pending.unlink()
    db = sqlite3.connect(pending)
    db.execute('PRAGMA journal_mode=OFF')
    db.execute('PRAGMA synchronous=OFF')
    db.executescript(SCHEMA)
    all_fields = collections.Counter()
    for fid, (path, rel) in enumerate(files(), 1):
        group = bucket(rel)
        status = 'excluded'
        root_shape = error = None
        size = path.stat().st_size
        if group == 'scan':
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            try:
                obj = json.loads(data)
                root_shape = shape(obj)
                status = 'parsed'
            except (ValueError, UnicodeError, RecursionError) as exc:
                error = str(exc)
                status = 'failed'
            if status == 'parsed':
                scan = Scanner(db, fid, rel, version)
                scan.walk(obj)
                scan.insert()
                all_fields.update(scan.fields)
        else:
            sha = digest(path)
        db.execute('INSERT INTO files VALUES (?,?,?,?,?,?,?,?)',
                   (fid, rel, size, sha, group, status, root_shape, error))
        if fid % 2000 == 0:
            print(f'{fid:,} files', flush=True)
            db.commit()
    db.executemany('INSERT INTO fields VALUES (?,?,?,?)',
                   ((*key, value) for key, value in all_fields.items()))
    db.execute('CREATE INDEX fields_type ON fields(type)')
    print('Resolving and indexing', flush=True)
    finalize(db)
    excel_links(db, version)
    db.execute(f'PRAGMA user_version={version}')
    db.commit()
    print(db.execute('PRAGMA quick_check').fetchone(), flush=True)
    db.close()
    pending.replace(database)

def verify(database):
    with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as db:
        expected = {path: (size, sha) for path, size, sha in db.execute('SELECT path,bytes,sha256 FROM files')}
    seen = set()
    issues = []
    for path, rel in files():
        seen.add(rel)
        actual = path.stat().st_size, digest(path)
        if actual != expected.get(rel):
            issues.append(rel)
    missing = sorted(expected.keys() - seen)
    for rel in sorted(issues):
        print('changed or added', rel)
    for rel in missing:
        print('missing', rel)
    print(f'{len(seen)} files rehashed; {len(issues)} changed/added; {len(missing)} missing')
    return int(bool(issues or missing))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify-source', action='store_true')
    ap.add_argument('--version', type=int, choices=(1, 2), default=1)
    args = ap.parse_args()
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        ap.error('local TurnBasedGameData directory required')
    database = DATABASE if args.version == 1 else DATABASE.with_stem('audit-v2')
    if args.verify_source:
        raise SystemExit(verify(database))
    build(database, args.version)
