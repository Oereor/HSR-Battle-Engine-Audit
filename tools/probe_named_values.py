#!/usr/bin/env python3
"""Compare singleton AddModifier binding candidates with common text hashes."""
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import itertools
import os
import zlib

os.environ['AUDIT_INDEX_VERSION'] = '2'
from query import ROOT, connect, lookup, source

MASK = 0xffffffff
BASE = 2166136261
FNV = 16777619
OUT = ROOT / '05-context-expression'

def roll(data, initial, step):
    for value in data:
        initial = step(initial, value) & MASK
    return initial

def candidates():
    return {
        'crc32': zlib.crc32, 'adler32': zlib.adler32,
        'fnv1': lambda b: roll(b, BASE, lambda h, char: h * FNV ^ char),
        'fnv1a': lambda b: roll(b, BASE, lambda h, char: (h ^ char) * FNV),
        'multiply31': lambda b: roll(b, 0, lambda h, char: h * 31 + char),
        'bkdr131': lambda b: roll(b, 0, lambda h, char: h * 131 + char),
        'djb2': lambda b: roll(b, 5381, lambda h, char: h * 33 + char),
        'djb2xor': lambda b: roll(b, 5381, lambda h, char: h * 33 ^ char),
        'sdbm': lambda b: roll(b, 0, lambda h, char: h * 65599 + char),
    }

def alternating_djb2(text):
    """Candidate over two accumulators and UTF-16 code units."""
    encoded = text.encode('utf-16-le', errors='surrogatepass')
    accumulators = [5381, 5381]
    for index in range(0, len(encoded), 2):
        char = int.from_bytes(encoded[index:index + 2], 'little')
        lane = index // 2 % 2
        accumulators[lane] = (accumulators[lane] * 33 ^ char) & MASK
    first, second = accumulators
    value = (first + second * 1566083941) & MASK
    return value if value < 2**31 else value - 2**32

def dynamic_hashes(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'DynamicHashes' and isinstance(value, list):
                yield from (item for item in value if isinstance(item, int))
            elif isinstance(value, (dict, list)):
                yield from dynamic_hashes(value)
    elif isinstance(node, list):
        for item in node:
            yield from dynamic_hashes(item)

def bindings(db):
    rows = db.execute("""
      SELECT path,pointer,def_pointer FROM reference_locations
       WHERE status='scoped' AND path=def_path AND parent_type='RPG.GameCore.AddModifier'
         AND field='ModifierName' AND path LIKE 'Config/ConfigAbility/%' ORDER BY path,pointer
    """)
    for path, records in itertools.groupby(rows, key=lambda row: row[0]):
        root = source(path)

        @lru_cache
        def local_hash_slot(p):
            recipient = lookup(root, p)
            floats = recipient.get('DynamicValues', {}).get('Floats', {})
            if len(floats) == 1:
                key, = floats
                used = frozenset(dynamic_hashes(recipient))
                if key.lstrip('-').isdigit() and int(key) in used:
                    return int(key), used

        for _, pointer, def_pointer in records:
            operation_pointer = pointer.rsplit('/ModifierName', 1)[0]
            operation = lookup(root, operation_pointer)
            if not isinstance(operation, dict) or operation.get('$type') != 'RPG.GameCore.AddModifier':
                continue
            values = operation.get('DynamicValues', {})
            if isinstance(values, dict) and len(values) == 1:
                name, = values
                target = local_hash_slot(def_pointer)
                if target is not None:
                    key, used = target
                    yield name, key, path, operation_pointer, def_pointer, alternating_djb2(name) in used

def main():
    with connect() as db:
        pairs = list(dict.fromkeys(bindings(db)))
    hypotheses = defaultdict(Counter)
    support = defaultdict(set)
    methods = candidates()
    for name, hashed, path, src, dst, used in pairs:
        support[name, hashed].add((path, dst))
        hypotheses['alternating-djb2', 'utf-16-code-units'][alternating_djb2(name) == hashed] += 1
        for encoding in ('utf-8', 'utf-16-le'):
            for method, compute in methods.items():
                hypotheses[method, encoding][compute(name.encode(encoding)) == hashed & MASK] += 1
    with (OUT / 'hash-probe-pairs.tsv').open('w', encoding='utf-8', newline='') as out:
        writer = csv.writer(out, delimiter='\t', lineterminator='\n')
        writer.writerow(['name','candidate_signed_hash','path','operation_pointer','recipient_pointer','predicted_hash_in_recipient'])
        writer.writerows(sorted(pairs))
    print(f'{len(pairs)} singleton bindings; {len(support)} distinct name/hash pairs; {len({name for name, _ in support})} names')
    for (name, hashed), locations in sorted(support.items(), key=lambda item: (-len(item[1]), *item[0]))[:12]:
        print('pair', name, hashed, len(locations), sep='\t')
    conflicts = {name: sorted(h for k, h in support if name == k)
                 for name, n in Counter(k for k, _ in support).items() if n > 1}
    print('names having multiple candidates:', len(conflicts))
    for name, possible in sorted(conflicts.items()):
        print('conflict', name, *possible, sep='\t')
    for (method, encoding), counts in sorted(hypotheses.items()):
        print(method, encoding, counts[True], counts[False], sep='\t')
    print('distinct matches', sum(alternating_djb2(name) == hashed for name, hashed in support), '/', len(support))
    print('mismatched singleton bindings with predicted alternative hash in recipient:',
          sum(used and alternating_djb2(name) != hashed for name, hashed, _, _, _, used in pairs))
    for name in ('MDF_PropertyValue','MDF_1','ADF_1','DV_AddPoint','MDF_Windfury_Flag','MDF_Windfury_Flag_Sum',
                 'Rank02','Rank2','ExRank01'):
        print('computed', name, alternating_djb2(name), sep='\t')
    for table in ('AvatarRankConfig', 'AvatarRankConfigLD', 'AvatarRankConfigTrial'):
        counts = Counter()
        for row in source(f'ExcelOutput/{table}.json'):
            if isinstance(row.get('Rank'), int) and isinstance(row.get('Trigger'), dict):
                key = f"Rank{row['Rank']:02}"
                counts[alternating_djb2(key) == row['Trigger'].get('Hash')] += 1
        print('rank control', table, counts[True], counts[False], sep='\t')

if __name__ == '__main__':
    main()
