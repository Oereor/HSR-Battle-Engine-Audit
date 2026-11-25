#!/usr/bin/env python3
"""Rehash the source tree and compare its read-only Git status to the initial state."""
import subprocess
from build_index import DATABASE, ROOT, SOURCE, verify

def git(*arguments):
    proc = subprocess.run(
        ['git', '--no-optional-locks', '-C', str(SOURCE), *arguments],
        check=True, text=True, capture_output=True,
    )
    return proc.stdout

def main():
    status = git('log', '-1', '--format=%H%n%aI%n%s') + git('status', '--porcelain=v1', '-uall')
    expected = (ROOT / 'index' / 'source-start.git.txt').read_text(encoding='utf-8')
    result = verify(DATABASE.with_stem('audit-v2'))
    git_unchanged = status == expected
    print('Git revision and porcelain snapshot match:', git_unchanged)
    print('Current read-only Git snapshot:')
    print(status, end='')
    audit_git_absent = not (ROOT / '.git').exists() and not (ROOT / '.git').is_symlink()
    print('Audit directory has no .git entry:', audit_git_absent)
    print('Manifest scope: regular files outside .git; symlinks and Git objects excluded.')
    raise SystemExit(result or not git_unchanged or not audit_git_absent)

if __name__ == '__main__':
    main()
