#!/usr/bin/env python3
"""Recount type occurrences and check index pointers against the local JSON."""
from collections import Counter
import json
import random
from query import connect, lookup, source

def recount(node, counter):
    if isinstance(node, dict):
        identifier = node.get('$type')
        if isinstance(identifier, str):
            counter[identifier] += 1
        for value in node.values():
            recount(value, counter)
    elif isinstance(node, list):
        for value in node:
            recount(value, counter)

def main():
    with connect() as db:
        assert db.execute('PRAGMA quick_check').fetchone() == ('ok',)
        indexed = Counter(dict(db.execute('SELECT type,occurrences FROM type_counts')))
        regenerated = Counter()
        paths = [p for (p,) in db.execute("SELECT path FROM files WHERE status='parsed' ORDER BY path")]
        # An independent tree traversal that makes no decisions about roles or refs.
        for path in paths:
            recount(source(path), regenerated)
        assert regenerated == indexed, (regenerated - indexed, indexed - regenerated)
        print(f'recount: {len(paths)} parsed files, {len(indexed)} types, {indexed.total()} occurrences')
        rows = ['SELECT path,pointer,type FROM occurrences',
                "SELECT path,pointer,name FROM definition_locations WHERE kind='ability'",
                'SELECT path,pointer,name FROM reference_locations',
                "SELECT path,pointer,name FROM event_locations WHERE form='callback-selector'"]
        for select in rows:
            row_ids = list(db.execute(select.replace('SELECT path,pointer,', 'SELECT DISTINCT path,pointer,') +
                                      ' ORDER BY path,pointer LIMIT 4000'))
            if not row_ids:
                continue
            sampled = random.Random(31).sample(row_ids, min(len(row_ids), 32))
            for path, pointer, expected in sampled:
                node = lookup(source(path), pointer)
                value = node.get('$type', node.get('Name')) if isinstance(node, dict) else str(node)
                assert value == expected, (path, pointer, value, expected)
            print(f'checked {len(sampled)} pointers from {select}')
        counts = dict(db.execute('SELECT status,count(*) FROM resolved GROUP BY status'))
        total, = db.execute('SELECT count(*) FROM refs').fetchone()
        assert sum(counts.values()) == total
        print('ref statuses:', counts)
        joins = db.execute('SELECT count(*),sum(target_file_id IS NULL) FROM excel_edges').fetchone()
        print('Excel candidate join rows / unmatched:', joins)

if __name__ == '__main__':
    main()
