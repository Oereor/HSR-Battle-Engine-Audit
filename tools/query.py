#!/usr/bin/env python3
"""Read-only queries and JSON Pointer lookup for the audit."""
import argparse
import json
import os
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT.parent / 'TurnBasedGameData').resolve()
DB = ROOT / 'index' / ('audit-v2.sqlite' if os.getenv('AUDIT_INDEX_VERSION') == '2' else 'audit.sqlite')

def connect():
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    db.execute('PRAGMA query_only=ON')
    return db

def lookup(root, pointer):
    if not pointer:
        return root
    if not pointer.startswith('/'):
        raise ValueError('JSON Pointer must be empty or start with /')
    for escaped in pointer[1:].split('/'):
        key = escaped.replace('~1', '/').replace('~0', '~')
        root = root[int(key)] if isinstance(root, list) else root[key]
    return root

def source(path):
    p = (SOURCE / path).resolve()
    if not p.is_relative_to(SOURCE) or '.git' in p.relative_to(SOURCE).parts:
        raise ValueError('path must be within TurnBasedGameData data')
    return json.loads(p.read_bytes())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='mode', required=True)
    for mode in ('type', 'definition', 'reference', 'event', 'sql'):
        command = subs.add_parser(mode)
        command.add_argument('query')
        command.add_argument('--limit', type=int, default=50)
    command = subs.add_parser('show')
    command.add_argument('path')
    command.add_argument('pointer', nargs='?', default='')
    args = parser.parse_args()
    if args.mode == 'show':
        print(json.dumps(lookup(source(args.path), args.pointer), indent=2, ensure_ascii=False))
        return
    cases = {
        'type': ('occurrences', 'type'),
        'definition': ('definition_locations', 'name'),
        'reference': ('reference_locations', 'name'),
        'event': ('event_locations', 'name'),
    }
    with connect() as db:
        if args.mode == 'sql':
            cur = db.execute(args.query)
        else:
            table, field = cases[args.mode]
            cur = db.execute(f'SELECT * FROM {table} WHERE {field}=? ORDER BY path,pointer', (args.query,))
        print('\t'.join(item[0] for item in cur.description))
        for row in cur.fetchmany(args.limit):
            print('\t'.join(str(value) if value is not None else '' for value in row))

if __name__ == '__main__':
    main()
