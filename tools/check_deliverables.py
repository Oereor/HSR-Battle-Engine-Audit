#!/usr/bin/env python3
"""Check audit deliverables, relative navigation and fully written source pointers."""
import argparse
from collections import Counter
import functools
from pathlib import Path
import re
from urllib.parse import unquote
from query import ROOT, lookup, source

EXPECTED = [
    '00-data-survey', '01-entity-ability', '02-atomic-operations', '03-modifier',
    '04-callback-trigger', '05-context-expression', '06-resource-scheduling',
    '07-case-studies', '08-engine-reconstruction',
]
GLOBALS = ['README.md', 'PLAN.md', 'PROGRESS.md', 'CLAIMS.md', 'SUMMARY.md']
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')
EVIDENCE = re.compile(r'`((?:Config|ExcelOutput|Stages|Story|TextMap)/[^#`\n]+\.json)#[ \t]*(/[^`\n]*)`')
PLAIN_EVIDENCE = re.compile(r'((?:Config|ExcelOutput|Stages|Story|TextMap)/[\w./-]+\.json)\s*·\s*(/[\w./~+-]+)')
CLAIM = re.compile(r'^\|\s*([A-Z][A-Z0-9]+-\d+)\s*\|\s*[^|]+\|\s*(\w+)\s*\|', re.MULTILINE)
cached_source = functools.lru_cache(maxsize=6)(source)

def markdown(p):
    return p.read_text(encoding='utf-8')

def local_targets(document):
    for target in LINK.findall(markdown(document)):
        target = target.strip('<>').split('#', 1)[0]
        if target and '://' not in target and not target.startswith(('mailto:', 'tel:')):
            yield (document.parent / unquote(target)).resolve()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pointers-only', action='store_true')
    args = parser.parse_args()
    missing = []
    pointer_issues = []
    seen = set()
    docs = sorted(p for pattern in ('*.md', '[0-9][0-9]-*/*.md', 'index/*.md') for p in ROOT.glob(pattern))
    if not args.pointers_only:
        required = [ROOT / f for f in GLOBALS] + [
            ROOT / group / filename for group in EXPECTED for filename in ('report.md', 'inventory.md')]
        missing.extend(p for p in required if not p.is_file())
        for doc in docs:
            if doc.name == 'AUDIT_SPEC.md':
                continue
            missing.extend(target for target in local_targets(doc) if target.is_relative_to(ROOT) and not target.exists())
        cases = ROOT / '07-case-studies'
        case_files = sorted(cases.glob('[0-9][0-9]-*.md'))
        case_numbers = [int(p.name.split('-', 1)[0]) for p in case_files]
        assert case_numbers == list(range(1, 16)), ('case numbering', case_numbers)
        case_links = set(local_targets(cases / 'inventory.md'))
        assert set(case_files) <= case_links, ('cases missing from inventory', set(case_files) - case_links)
        print(f'{len(case_files)} independent cases linked from the inventory')
    for doc in docs:
        body = markdown(doc)
        for rel, pointer in EVIDENCE.findall(body) + PLAIN_EVIDENCE.findall(body):
            key = rel, pointer
            if key in seen:
                continue
            seen.add(key)
            try:
                evidence = cached_source(rel)
                # Some tables give the value inline after the pointer.
                location = re.split(r'\s*=\s*(?=[\[{"\-\d]|true\b|false\b|null\b)', pointer, maxsplit=1)[0]
                lookup(evidence, location.rstrip())
            except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
                pointer_issues.append((doc.relative_to(ROOT), rel, pointer, str(exc)))
    for p in sorted(set(missing)):
        print('MISSING', p.relative_to(ROOT))
    for issue in pointer_issues:
        print('POINTER', *issue)
    ids = CLAIM.findall(markdown(ROOT / 'CLAIMS.md'))
    duplicates = [claim for claim, n in Counter(claim for claim, _ in ids).items() if n > 1]
    print('claim levels', dict(Counter(level for _, level in ids)), 'duplicate IDs', duplicates)
    print(f'{len(docs)} Markdown files and {len(seen)} full source pointers checked')
    raise SystemExit(int(bool(missing or pointer_issues or duplicates)))

if __name__ == '__main__':
    main()
