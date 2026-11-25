#!/usr/bin/env python3
"""Supplement v2 with StageAbilityConfig and lexical task-template candidates."""
import collections
import csv
import json
import os

os.environ['AUDIT_INDEX_VERSION'] = '2'
from query import ROOT, connect

OUT = ROOT / 'index' / 'reference-overlay.tsv'

def scope(pointer):
    return pointer.rsplit('/', 2)[0]

def stage_refs(db, abilities):
    query = """
      SELECT f.path,e.pointer,e.data FROM excel_rows e JOIN files f ON f.id=e.file_id
      WHERE json_array_length(json_extract(e.data,'$.StageAbilityConfig'))>0
      ORDER BY f.path,e.pointer
    """
    for path, p, raw in db.execute(query):
        for i, item in enumerate(json.loads(raw)['StageAbilityConfig']):
            if isinstance(item, str) and item:
                matches = abilities.get(item, [])
                reason = {0: 'unresolved', 1: 'candidate'}.get(len(matches), 'ambiguous')
                yield 'stage-ability', path, f'{p}/StageAbilityConfig/{i}', item, reason, matches

def template_refs(db, templates):
    query = """
      SELECT path,pointer,name FROM reference_locations
      WHERE kind='template' AND parent_type LIKE '%.IncludeTaskListTemplate'
      ORDER BY path,pointer
    """
    for path, p, name in db.execute(query):
        matches = templates.get(name, [])
        local = [(target, loc) for target, loc in matches if target == path and
                 (not scope(loc) or p.startswith(scope(loc) + '/'))]
        if local:
            nearest = max(len(scope(loc)) for _, loc in local)
            selected = [(target, loc) for target, loc in local if len(scope(loc)) == nearest]
            yield 'include-template', path, p, name, 'lexical-candidate' if len(selected) == 1 else 'ambiguous', selected
        elif matches:
            outer = [(target, loc) for target, loc in matches if not scope(loc)]
            if outer:
                yield 'include-template', path, p, name, 'candidate' if len(outer) == 1 else 'ambiguous', outer
            else:
                yield 'include-template', path, p, name, 'outside-lexical-scope', matches
        else:
            yield 'include-template', path, p, name, 'unresolved', []

def main():
    definitions = collections.defaultdict(lambda: collections.defaultdict(list))
    with connect() as db, OUT.open('w', encoding='utf-8', newline='') as handle:
        for kind, name, path, p in db.execute(
            "SELECT kind,name,path,pointer FROM definition_locations WHERE kind IN ('ability','template') ORDER BY path,pointer"
        ):
            definitions[kind][name].append((path, p))
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(['kind','path','pointer','literal','status','static_candidates'])
        counts = collections.Counter()
        for group in (stage_refs(db, definitions['ability']), template_refs(db, definitions['template'])):
            for kind, path, p, name, status, matches in group:
                writer.writerow([kind, path, p, name, status, json.dumps(matches, ensure_ascii=False)])
                counts[kind, status] += 1
        for (kind, status), n in sorted(counts.items()):
            print(kind, status, n, sep='\t')

if __name__ == '__main__':
    main()
