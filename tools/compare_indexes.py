#!/usr/bin/env python3
"""Verify content and type equality across index versions; report added coverage."""
import sqlite3
from query import ROOT

INDEX = ROOT / 'index'

def main():
    with sqlite3.connect(f"file:{INDEX / 'audit.sqlite'}?mode=ro", uri=True) as db:
        db.execute("ATTACH ? AS v2", (f"file:{INDEX / 'audit-v2.sqlite'}?mode=ro",))
        for table, columns in [
            ('files', 'path,bytes,sha256,bucket,status'),
            ('type_counts', 'type,occurrences,files'),
        ]:
            for a, b in [('main', 'v2'), ('v2', 'main')]:
                sql = f'SELECT count(*) FROM (SELECT {columns} FROM {a}.{table} EXCEPT SELECT {columns} FROM {b}.{table})'
                count, = db.execute(sql).fetchone()
                assert count == 0, (table, a, b, count)
            print(table, 'identical in v1/v2')
        for table, column in [('definition_locations', 'kind'), ('reference_locations','kind'),
                              ('event_locations', 'form')]:
            rows = db.execute(f'''
                SELECT 1 AS version,{column} AS category,count(*) AS nodes FROM main.{table} GROUP BY 2
                UNION ALL
                SELECT 2,{column},count(*) FROM v2.{table} GROUP BY 2 ORDER BY 2,1
            ''')
            for row in rows:
                print(table, *row, sep='\t')

if __name__ == '__main__':
    main()
