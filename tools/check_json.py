#!/usr/bin/env python3
"""Check duplicate object keys and unquoted nonfinite tokens in parsed files."""
from collections import Counter
import json
from query import SOURCE, connect

def annotated_types(value):
    if isinstance(value, dict):
        return int(isinstance(value.get('$type'), str)) + sum(annotated_types(v) for v in value.values())
    if isinstance(value, list):
        return sum(annotated_types(v) for v in value)
    return 0

def main():
    issues = Counter()
    checked = 0
    shadowed_types = 0
    with connect() as db:
        for rel, in db.execute("SELECT path FROM files WHERE status='parsed' ORDER BY path"):
            def pairs(items):
                nonlocal shadowed_types
                obj = dict(items)
                if len(items) != len(obj):
                    issues[rel, 'duplicate keys'] += len(items) - len(obj)
                    seen = set()
                    for key, value in reversed(items):
                        if key in seen:
                            shadowed_types += int(key == '$type' and isinstance(value, str)) + annotated_types(value)
                        seen.add(key)
                return obj

            def constant(token):
                issues[rel, token] += 1

            json.loads((SOURCE / rel).read_bytes(), object_pairs_hook=pairs, parse_constant=constant)
            checked += 1
    for (rel, kind), n in sorted(issues.items()):
        print(f'{rel}\t{kind}\t{n}')
    print(f'checked {checked} files; {len(issues)} file/category issues; {issues.total()} instances')
    print(f'string type annotations in shadowed properties: {shadowed_types}')

if __name__ == '__main__':
    main()
