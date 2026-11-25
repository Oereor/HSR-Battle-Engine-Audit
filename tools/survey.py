#!/usr/bin/env python3
"""Produce the data survey tables and the complete observed type inventory."""
import csv
from query import ROOT, connect

OUT = ROOT / '00-data-survey'

def export(db, name, sql):
    cur = db.execute(sql)
    with (OUT / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(item[0] for item in cur.description)
        writer.writerows(cur)

def md_table(data, columns):
    result = ['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join('---' for _ in columns) + ' |']
    result.extend('| ' + ' | '.join(str(v) for v in row) + ' |' for row in data)
    return '\n'.join(result)

def main():
    with connect() as db:
        export(db, 'types.tsv', 'SELECT * FROM type_counts ORDER BY type')
        export(db, 'parse-failures.tsv', "SELECT path,error FROM files WHERE status='failed' ORDER BY path")
        export(db, 'ref-totals.tsv', 'SELECT kind,status,count(*) count FROM reference_locations GROUP BY 1,2 ORDER BY 1,2')
        export(db, 'definition-collisions.tsv',
               'SELECT kind,name,count(*) definitions,count(DISTINCT file_id) files FROM defs GROUP BY 1,2 HAVING count(*)>1 ORDER BY 1,2')
        groups = db.execute('SELECT bucket,status,count(*),sum(bytes) FROM files GROUP BY 1,2 ORDER BY 1,2').fetchall()
        roots = db.execute("""SELECT CASE WHEN instr(path,'/')>0 THEN substr(path,1,instr(path,'/')-1) ELSE '.' END,
                           count(*),sum(bytes),sum(status='parsed') FROM files GROUP BY 1 ORDER BY 1""").fetchall()
        config_dirs = db.execute("""WITH p AS (SELECT substr(path,8) p,bytes,status FROM files WHERE path LIKE 'Config/%')
                           SELECT CASE WHEN instr(p,'/')>0 THEN substr(p,1,instr(p,'/')-1) ELSE '.' END,
                           count(*),sum(bytes),sum(status='parsed') FROM p GROUP BY 1 ORDER BY 1""").fetchall()
        counts = db.execute('SELECT count(*),sum(occurrences) FROM type_counts').fetchone()
        defs = db.execute('SELECT kind,count(*),count(DISTINCT name) FROM defs GROUP BY kind ORDER BY kind').fetchall()
        refs = db.execute('SELECT status,count(*) FROM resolved GROUP BY status ORDER BY status').fetchall()
        events = db.execute('SELECT form,count(*),count(DISTINCT name) FROM events GROUP BY form ORDER BY form').fetchall()
    lines = [
        '# 数据与公共索引清单', '',
        '由 [survey.py](../tools/survey.py) 从 SQLite 生成。字节为实际文件大小。同一类型或名称可跨多个类别出现。', '',
        '## 文件及解析', '', md_table(groups, ['类别', '状态', '文件', '字节']), '',
        '## 顶层目录', '', md_table(roots, ['目录', '文件', '字节', '成功解析']), '',
        '## 类型与符号', '', f'观测到 {counts[0]:,} 个不同的字符串 `$type`，共 {counts[1]:,} 次出现。', '',
        md_table(defs, ['定义类别', '定义节点', '不同名称']), '', md_table(refs, ['引用状态','节点']), '',
        md_table(events, ['事件索引形态','记录','不同原始值']), '',
        '详见 [全部类型 counts](types.tsv)、[引用汇总](ref-totals.tsv)、[同名定义](definition-collisions.tsv) 和 [JSON 解析失败](parse-failures.tsv)。', '',
        '## Config 子树', '', md_table(config_dirs, ['目录', '文件', '字节', '成功解析']), '',
    ]
    (OUT / 'inventory.md').write_text('\n'.join(lines), encoding='utf-8')

if __name__ == '__main__':
    main()
