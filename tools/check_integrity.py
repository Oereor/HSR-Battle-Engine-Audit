#!/usr/bin/env python3
"""Rehash the source tree and compare its read-only Git status to the initial state."""
import argparse
import subprocess
from build_index import DATABASE, ROOT, SOURCE, verify

def git(*arguments):
    proc = subprocess.run(
        ['git', '--no-optional-locks', '-C', str(SOURCE), *arguments],
        check=True, text=True, capture_output=True,
    )
    return proc.stdout

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-existing-audit-git', action='store_true',
                        help='Accept an existing audit .git entry only with an explicit waiver.')
    args = parser.parse_args()
    status = git('log', '-1', '--format=%H%n%aI%n%s') + git('status', '--porcelain=v1', '-uall')
    expected = (ROOT / 'index' / 'source-start.git.txt').read_text(encoding='utf-8')
    result = verify(DATABASE.with_stem('audit-v2'))
    git_unchanged = status == expected
    print('Git revision and porcelain snapshot match:', git_unchanged)
    print('Current read-only Git snapshot:')
    print(status, end='')
    audit_git_absent = not (ROOT / '.git').exists() and not (ROOT / '.git').is_symlink()
    print('Audit directory has no .git entry:', audit_git_absent)
    if args.allow_existing_audit_git and not audit_git_absent:
        print('Existing audit .git accepted under explicit user waiver.')
    print('Manifest scope: regular files outside .git; symlinks and Git objects excluded.')
    audit_directory_accepted = audit_git_absent or args.allow_existing_audit_git
    raise SystemExit(result or not git_unchanged or not audit_directory_accepted)

if __name__ == '__main__':
    main()
