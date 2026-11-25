#!/usr/bin/env python3
"""Generate context, targeting and expression references from the v2 shared index."""
import base64
from collections import Counter, defaultdict
import csv
from itertools import chain
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / 'tools'))
os.environ['AUDIT_INDEX_VERSION'] = '2'
from query import connect, lookup, source

CORE = (
    'Config/ConfigAbility/', 'Config/ConfigGlobalModifier/',
    'Config/ConfigGlobalTaskListTemplate/', 'Config/ConfigCharacter/',
    'Config/ConfigCommonSkillPool/',
)
MODES = {'rt-battle': 'Config/Activity/RtBattle/', 'rt-defence': 'Config/Activity/RtDefence/'}
COMMON = 'Config/GlobalConfig/'
SOURCE_SCOPE = {'common', 'core', *MODES}
CONTROL = re.compile(r'(PredicateTaskList|^ForEach|^Retarget$|^LoopExecute|^ConditionLoop|^SwitchCase|^SequenceConfig|^IncludeTaskListTemplate|^TaskTemplateFetchParam)')
VARIABLE = re.compile(r'(DynamicValue|DynamicString|DynamicEntity|CustomValue|CustomString|Blackboard|Snapshot|ParamValue|ParamString|ParamFlag|AbilityProperty|ParamModifierCustomEvent)')
TARGET_FIELD = re.compile(r'(?i)(TargetType\d*$|TargetInfo$|^Target(?:s|Entity|Alias)?$|(?:^|Skill|Ability|Main|Sub|Source|Param|Override|Redirect|Split|Attack|Compare|Read|Write|PropertyFrom)Target(?:Type|s)?$)')
PREDICATE_FIELD = re.compile(r'(?:^|[A-Z])Predicate(?:List|Filter)?$|(?:^|[A-Z])(?:UsableCondition|PreCheck)$')
POINTER_PART = re.compile(r'^[A-Za-z0-9_]+$')

def domain(path):
    if path.startswith(COMMON):
        return 'common'
    if path.startswith(CORE):
        return 'core'
    for name, prefix in MODES.items():
        if path.startswith(prefix):
            return name
    return 'adjacent'

def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))

def shape(value):
    return type(value).__name__ if value is not None else 'null'

def child(pointer, key):
    return pointer + '/' + str(key).replace('~', '~0').replace('/', '~1')

def enumerate_objects(node, pointer=''):
    if isinstance(node, dict):
        yield pointer, node
        for key, value in node.items():
            yield from enumerate_objects(value, child(pointer, key))
    elif isinstance(node, list):
        for i, member in enumerate(node):
            yield from enumerate_objects(member, child(pointer, i))

def tsv(name, fields, rows):
    with (HERE / f'{name}.tsv').open('w', encoding='utf-8', newline='') as handle:
        out = csv.writer(handle, delimiter='\t', lineterminator='\n')
        out.writerow(fields)
        out.writerows(rows)

def target_family(type_name, parent):
    short = type_name.split('.')[-1]
    if not short.endswith(('Task', 'TaskList')) and (short.startswith(('Target', 'RtTarget')) or
            (TARGET_FIELD.search(parent) and not PREDICATE_FIELD.search(parent))):
        return 'target-structure'
    if PREDICATE_FIELD.search(parent) or short.startswith(('By', 'RtBy', 'VP_')):
        return 'predicate'
    if short.startswith('VE_'):
        return 'value-evaluator'
    if VARIABLE.search(short):
        return 'value-or-state-operation'
    if CONTROL.search(short):
        return 'control'
    return ''

def typed_inventory(db):
    contexts = defaultdict(Counter)
    selected = {}
    short_total = dict(db.execute('SELECT type,occurrences FROM type_counts'))
    # Type context limits review to structurally relevant placements or recognizable names.
    routes = []
    query = """SELECT type,parent_field,parent_type,anchor_kind,sum(occurrences)
               FROM type_context GROUP BY 1,2,3,4"""
    for typ, field, ptype, anchor, n in db.execute(query):
        group = target_family(typ, field)
        if group:
            contexts[typ, group][field] += n
            routes.append((typ, group, field, ptype, anchor, n))
            selected.setdefault(typ, set()).add(group)
    fields = defaultdict(dict)
    for typ, k, v, n in db.execute('SELECT type,field,shape,count FROM fields ORDER BY 1,2,3'):
        if typ in selected:
            fields[typ][f'{k}:{v}'] = n
    positions = defaultdict(Counter)
    exemplars = {}
    for typ in sorted(selected):
        rows = db.execute("""SELECT f.path,t.pointer,t.parent_field
                             FROM types t JOIN files f ON f.id=t.file_id WHERE t.type=?""", (typ,))
        for path, loc, field in rows:
            group = target_family(typ, field)
            if not group:
                continue
            key = typ, group
            bucket = domain(path)
            positions[key][bucket] += 1
            score = (bucket not in SOURCE_SCOPE, bucket != 'core', path, loc)
            if key not in exemplars or score < exemplars[key][0]:
                exemplars[key] = score, path, loc
    result = []
    for typ, group in sorted(contexts):
        key = typ, group
        counts = positions[key]
        assert sum(contexts[key].values()) == counts.total(), key
        result.append((typ, group, short_total[typ], *[counts[r] for r in ('core','common','rt-battle','rt-defence','adjacent')],
                       compact(dict(sorted(contexts[key].items()))), compact(fields[typ]), *exemplars[key][1:]))
    tsv('typed-context-inventory', ('type','role_candidate','all_type_occurrences','core','common','rt_battle',
                                   'rt_defence','adjacent','parent_fields','global_field_shapes','path','pointer'), result)
    tsv('typed-context-positions', ('type','role_candidate','parent_field','parent_type','anchor_kind','occurrences'), sorted(routes))
    for group in sorted({row[1] for row in result}):
        selected_rows = [r for r in result if r[1] == group and sum(r[3:7])]
        print('typed-role', group, 'primary-type-count', len(selected_rows),
              'primary-matches', sum(sum(r[3:7]) for r in selected_rows),
              'all-type-count', sum(r[1] == group for r in result))

def dictionaries(db):
    definitions = []
    for domain_name, relative, root, kind in [
        ('common', f'{COMMON}TargetAliasConfig.json', 'AliasDict', 'alias'),
        ('common', f'{COMMON}TargetOperationConfig.json', 'OperationDict', 'operation'),
        *[(group, prefix + f'Target{stem}Config_{"RtBattle" if group == "rt-battle" else "RtDefence"}.json', key, kind)
          for group, prefix in MODES.items()
          for stem, key, kind in (('Alias','AliasDict','alias'),('Operation','OperationDict','operation'))],
    ]:
        payload = source(relative)
        if root not in payload:
            print('target dictionary container absent', relative, root, sorted(payload))
        data = payload.get(root, {})
        definitions.extend((domain_name, kind, name, relative, f'/{root}/' + child('', name)[1:], value)
                           for name, value in data.items())
    local_files = defaultdict(list)
    for path, p, name in db.execute("SELECT path,pointer,name FROM definition_locations WHERE kind='alias'"):
        local_files[path].append((p, name))
    for path, defs in local_files.items():
        data = source(path)
        definitions.extend(('file-local','alias',name,path,p,lookup(data,p)) for p,name in defs)
    tsv('target-dictionaries', ('domain','kind','name','path','pointer','node'),
        ((scope,kind,name,path,p,compact(value)) for scope,kind,name,path,p,value in sorted(definitions, key=lambda x:x[:5])))
    named = defaultdict(list)
    for scope,kind,name,path,p,_ in definitions:
        named[kind,name].append((scope,path,p))
    print('target dictionaries', dict(Counter((r[0], r[1]) for r in definitions)))
    return named

def resolve_alias(ref, path, named):
    bucket = domain(path)
    scopes = {'common'} | ({bucket} if bucket in MODES else set())
    def visible(kind, name):
        return [match for match in named.get((kind,name),[]) if match[0] in scopes or match[1] == path]
    direct = visible('alias',ref)
    if direct:
        return ('exact-unique' if len(direct) == 1 else 'exact-multiple'), [ref], direct
    terms = re.split(r'\s*[+|\-]\s*', ref)
    terms = [term.split('.') for term in terms]
    composed = len(terms) > 1 or any(len(term) > 1 for term in terms)
    if composed and all(POINTER_PART.fullmatch(part) for term in terms for part in term):
        components = [(kind,name) for term in terms for kind,name in zip(
            chain(('alias',), ('operation' for _ in term[1:])), term)]
        missing = [name for kind,name in components if not visible(kind,name)]
        all_matches = [(name,*match) for kind,name in components for match in visible(kind,name)]
        status = 'component-candidates' if not missing else 'components-unresolved'
        return status, [x[1] for x in components], all_matches
    if named.get(('alias',ref)):
        return 'outside-domain-or-file', [ref], named['alias',ref]
    return 'unresolved', [ref], []

def alias_inventory(db, named):
    counts = Counter()
    names = defaultdict(Counter)
    samples = {}
    stmt = """SELECT path,pointer,name,parent_type,anchor_kind,status FROM reference_locations WHERE kind='alias' ORDER BY path,pointer"""
    def rows():
        for path,p,ref,typ,anchor,status in db.execute(stmt):
            new,words,matches = resolve_alias(ref, path, named)
            bucket = domain(path)
            counts[bucket,status,new] += 1
            names[ref][new] += 1
            samples.setdefault(ref,(path,p))
            yield bucket, path, p, ref, typ, anchor, status, new, compact(words), compact(matches)
    tsv('alias-references', ('domain','path','pointer','literal','node_type','anchor_kind','index_v2_status',
                             'supplement_status','tokens','candidate_definitions'), rows())
    tsv('alias-counts', ('domain','index_v2_status','supplement_status','nodes'), ((*key,n) for key,n in sorted(counts.items())))
    tsv('alias-literals', ('literal','occurrences','supplement_status_counts','path','pointer'),
        ((lit,stat.total(),compact(stat),*samples[lit]) for lit,stat in sorted(names.items())))
    print('alias references', sum(counts.values()), 'distinct',len(names))
    print('v2 unresolved matched by exact unique', sum(n for (_,s,t),n in counts.items() if s=='unresolved' and t=='exact-unique'))
    print('v2 unresolved with all component candidates', sum(n for (_,s,t),n in counts.items() if s=='unresolved' and t=='component-candidates'))

def raw_manifest(db):
    # Exact indexed definition resources, character schemas, and target dictionaries.
    stmt = """SELECT DISTINCT path FROM (
                SELECT path FROM definition_locations WHERE kind IN ('ability','modifier','skill_pool','template','alias')
                UNION ALL
                SELECT path FROM occurrences WHERE pointer='' AND type IN
                    ('RPG.GameCore.CharacterConfig','RPG.GameCore.CharacterOverrideConfig','RPG.GameCore.ServantConfig')
                UNION ALL
                SELECT path FROM files WHERE path LIKE '%/Target%Config%.json' AND status='parsed'
              ) ORDER BY path"""
    return [path for (path,) in db.execute(stmt) if domain(path) in SOURCE_SCOPE]

class Rollup:
    def __init__(self):
        self.counts = Counter()
        self.examples = {}

    def add(self, key, path, pointer):
        self.counts[key] += 1
        self.examples.setdefault(key, (path,pointer))

    def rows(self):
        return ((*key,num,*self.examples[key]) for key,num in sorted(self.counts.items()))

def raw_inventory(db):
    paths = raw_manifest(db)
    tsv('raw-scan-manifest', ('path','domain'), ((path,domain(path)) for path in paths))
    shapes, strings, fixed, postfix, reads, scope, vocab = [Rollup() for _ in range(7)]
    for path in paths:
        document = source(path)
        bucket = domain(path)
        for loc, obj in enumerate_objects(document):
            for field,value in obj.items():
                p = child(loc,field)
                if TARGET_FIELD.search(field) or field in {'ByRandom','MaxNumber','SubTargetType','PredicateFilter','AliveStateMask','EntityTypeMask','TeamTypeMask','AliveOnly'}:
                    shapes.add((bucket,field,shape(value)),path,p)
                    if isinstance(value,str):
                        strings.add((bucket,field,value),path,p)
                if field == 'ContextScope':
                    scope.add((bucket,str(value),str(obj.get('$type','[untyped]'))),path,p)
                if field in ('DynamicKey','CustomKey','ParamIndex','DynamicString','DynamicValues','DynamicStrings','CustomValues','ReadTargetType','WriteTargetType','ResetValue','OnDynamicValueChange','OnAbilityPropertyChange'):
                    vocab.add((bucket,str(obj.get('$type','[untyped]')),field,shape(value)),path,p)
                if field == 'FixedValue':
                    fixed.add((bucket,shape(obj.get('IsDynamic')),str(obj.get('IsDynamic')),shape(value),
                               shape(value.get('Value')) if isinstance(value,dict) else '-'),path,p)
                if field == 'PostfixExpr' and isinstance(value,dict):
                    code = value.get('OpCodes')
                    try:
                        data = base64.b64decode(code,validate=True).hex(' ')
                    except (TypeError, ValueError):
                        data = '[non-base64]'
                    length = lambda label: len(value[label]) if isinstance(value.get(label),list) else -1
                    postfix.add((bucket,str(code),data,length('FixedValues'),length('DynamicHashes'),
                                 compact(sorted(value)),str(obj.get('IsDynamic'))),path,p)
                if field == 'ReadInfo' and isinstance(value,dict):
                    reads.add((bucket,str(value.get('Type','[absent]')),shape(value.get('TriggerKey')),
                               shape(value.get('Index')),compact(sorted(value))),path,p)
    tsv('target-field-shapes', ('domain','field','shape','occurrences','path','pointer'),shapes.rows())
    tsv('target-string-values', ('domain','field','value','occurrences','path','pointer'),strings.rows())
    tsv('fixed-value-shapes', ('domain','is_dynamic_shape','is_dynamic','fixed_shape','value_shape','occurrences','path','pointer'),fixed.rows())
    tsv('postfix-shapes', ('domain','base64','hex_bytes','fixed_pool_size','dynamic_pool_size','expression_fields','is_dynamic','occurrences','path','pointer'),
        postfix.rows())
    tsv('read-info-shapes', ('domain','read_type','trigger_shape','index_shape','fields','occurrences','path','pointer'),
        reads.rows())
    tsv('context-scopes', ('domain','scope_value','typed_owner','occurrences','path','pointer'), scope.rows())
    tsv('context-variable-fields', ('domain','typed_owner','field','shape','occurrences','path','pointer'),vocab.rows())
    print('raw files',len(paths), dict(Counter(domain(x) for x in paths)))
    for key, table in [('target fields',shapes),('target literal',strings),('FixedValue',fixed),('PostfixExpr',postfix),('ReadInfo',reads),('ContextScope',scope),('variable fields',vocab)]:
        print(key, table.counts.total(), 'rows',len(table.counts))
    print('postfix patterns',len({key[1] for key in postfix.counts}))

def main():
    with connect() as db:
        named = dictionaries(db)
        alias_inventory(db,named)
        raw_inventory(db)
        typed_inventory(db)

if __name__ == '__main__':
    main()
