"""Purpose and main function: Copy the selected file, check the published language, Skill Get ready inside. Git Differences, submissions, version packages and GitHub Release.

Scope: github-publish Skill ;the original release directory is read-only, all local writings are located on Skill Internal.
Run Usage Python Standard library, Git with GitHub CLI,Reads login already in; defaults only to prepare, remotely write with a stand-alone command.
"""
from __future__ import annotations

import argparse
import codecs
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid
import zipfile

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
RESULTS = SKILL / 'results'
ACTIVE_RUN = None


def internal(path):
    path = Path(path).resolve()
    path.relative_to(SKILL)
    return path


def relative(value, *, root=False):
    if root and value == '.':
        return ''
    if not value or '\\' in value or '\x00' in value:
        raise ValueError('Path should be relative, root position used .')
    parts = value.split('/')
    if PurePosixPath(value).is_absolute() or any(p in {'', '.', '..'} for p in parts):
        raise ValueError('Path should be in the selected directory:' + value)
    if any(p.lower() == '.git' for p in parts):
        raise ValueError('Git The metadata are managed by the internal warehouse itself')
    return value


def repository(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value):
        raise ValueError('Repository usage owner/name format')
    if any(p in {'.', '..'} for p in value.split('/')):
        raise ValueError('Repository name invalid')
    return value


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    path = internal(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.writing')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    os.replace(temporary, path)


class Run:
    def __init__(self, name, *, create=False):
        global ACTIVE_RUN
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', name):
            raise ValueError('Job identification can only include letters, numbers, hyphens and underlineds')
        self.path = internal(RESULTS / name)
        if create:
            self.path.mkdir(parents=True, exist_ok=False)
        elif not self.path.is_dir():
            raise ValueError('Mission does not exist:' + name)
        self.name = name
        self.checkout = self.path / 'checkout'
        self.token = None
        self.receipt = self.load('result.json') if (self.path / 'result.json').exists() else {
            'purpose': 'Record actual GitHub publishing outcomes.',
            'scope': 'This prepared publication only.', 'run': name,
        }
        ACTIVE_RUN = self

    def load(self, name):
        return json.loads(internal(self.path / name).read_text(encoding='utf-8'))

    def record(self, **values):
        self.receipt.update(values)
        save(self.path / 'result.json', self.receipt)
        self.log('result.json', 'Update actual release status')

    def log(self, name, content):
        path = internal(self.path / name)
        with (self.path / 'log_updates.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
                'path': path.relative_to(SKILL).as_posix(), 'content': content,
                'source': 'scripts/publish.py'}, ensure_ascii=False) + '\n')

    def env(self, *, auth=False):
        env = os.environ.copy()
        # Inherited Git routing must never redirect a write to the source repository.
        for key in list(env):
            if key.startswith('GIT_') and key not in {
                'GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL'
            }:
                env.pop(key)
        for key in ['GH_REPO', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN']:
            env.pop(key, None)
        for name in ['tmp', 'cache', 'config/gh', 'hooks']:
            internal(self.path / name).mkdir(parents=True, exist_ok=True)
        env.update({'TMPDIR': str(self.path / 'tmp'), 'TMP': str(self.path / 'tmp'),
            'TEMP': str(self.path / 'tmp'), 'XDG_CACHE_HOME': str(self.path / 'cache'),
            'GH_CONFIG_DIR': str(self.path / 'config/gh'), 'GH_HOST': 'github.com',
            'GH_PROMPT_DISABLED': '1', 'GIT_TERMINAL_PROMPT': '0', 'GIT_LFS_SKIP_SMUDGE': '1'})
        if auth:
            if self.token is None:
                self.token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
                if not self.token:
                    # Read an existing login once. The token stays in process memory.
                    original = os.environ.copy()
                    original.update({'GH_HOST': 'github.com', 'TMPDIR': str(self.path / 'tmp'),
                        'TMP': str(self.path / 'tmp'), 'TEMP': str(self.path / 'tmp'),
                        'XDG_CACHE_HOME': str(self.path / 'cache'), 'GH_PROMPT_DISABLED': '1'})
                    result = subprocess.run(['gh', 'auth', 'token', '--hostname', 'github.com'],
                        cwd=self.path, env=original, capture_output=True, text=True)
                    if result.returncode:
                        raise ValueError('We need what we have. GitHub Login or provision through the environment GH_TOKEN')
                    self.token = result.stdout.strip()
            env['GH_TOKEN'] = self.token
        return env

    def command(self, args, *, cwd=None, auth=False, allow_failure=False):
        cwd = internal(cwd or self.path)
        result = subprocess.run(args, cwd=cwd, env=self.env(auth=auth),
            capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode and not allow_failure:
            reason = result.stderr.strip() or result.stdout.strip()
            if self.token:
                reason = reason.replace(self.token, '[credential]')
            raise ValueError(args[0] + ' Operation not completed:' + reason[:3000])
        return result

    def git(self, *args, auth=False, cwd=None, allow_failure=False):
        return self.command(['git', '-c', 'core.hooksPath=' + str(self.path / 'hooks'),
            '-c', 'commit.gpgSign=false', '-c', 'core.autocrlf=false', '-c', 'core.fsmonitor=false',
            '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
            *args], cwd=cwd or self.checkout, auth=auth, allow_failure=allow_failure)

    def branch(self, value):
        if value.startswith('-'):
            raise ValueError('Branch Name Invalid')
        self.git('check-ref-format', 'refs/heads/' + value, cwd=self.path)
        return value

    def remote_head(self, repo, branch):
        result = self.git('ls-remote', '--heads', 'https://github.com/' + repo + '.git',
            'refs/heads/' + branch, auth=True, cwd=self.path)
        return result.stdout.split()[0] if result.stdout.strip() else None


def collect(root, maps, excludes, run):
    chosen = {}
    omitted = []
    for mapping in maps:
        if '=' not in mapping:
            raise ValueError('--map Use Source Relative Path=Target relative path')
        source_name, destination = mapping.split('=', 1)
        source_name = relative(source_name, root=True)
        destination = relative(destination, root=True)
        source = root / source_name
        # Reject links rather than following a link back into the original object.
        for part in [source, *source.parents]:
            if part == root.parent:
                break
            if part.is_symlink():
                raise ValueError('Select the actual file or directory, the current path contains a symbol link:' + str(source))
        source = source.resolve(strict=True)
        source.relative_to(root)
        if source.is_relative_to(run.path):
            raise ValueError('The product of this task is not entered as such')
        if not (source.is_dir() or source.is_file()):
            raise ValueError('Only general files or directories received:' + str(source))
        explicit_results = source.is_relative_to(RESULTS)

        def excluded(path):
            rel = path.relative_to(root).as_posix()
            reason = ('.git' in path.relative_to(root).parts
                or path.is_relative_to(run.path)
                or not explicit_results and path.is_relative_to(RESULTS)
                or any(rel == p or rel.startswith(p.rstrip('/') + '/') or fnmatch.fnmatchcase(rel, p)
                       for p in excludes))
            if reason:
                omitted.append(rel)
            return reason

        def add(path):
            if path.is_symlink() or not path.is_file():
                raise ValueError('Copy only normal files; please handle separate links or special files:' + str(path))
            suffix = path.relative_to(source).as_posix() if source.is_dir() else ''
            target = '/'.join(p for p in [destination, suffix] if p)
            if not target:
                target = source.name
            target = relative(target)
            if target in chosen:
                raise ValueError('Multiple sources correspond to the same target:' + target)
            chosen[target] = path

        if excluded(source):
            continue
        if source.is_file():
            add(source)
        else:
            for directory, dirs, files in os.walk(source, followlinks=False):
                parent = Path(directory)
                kept = []
                for name in sorted(dirs):
                    path = parent / name
                    if excluded(path):
                        continue
                    if path.is_symlink():
                        raise ValueError('Directory contains symbolic links:' + str(path))
                    kept.append(name)
                dirs[:] = kept
                for name in sorted(files):
                    path = parent / name
                    if not excluded(path):
                        add(path)
    if not chosen:
        raise ValueError('No normal files to be published in the selected range')
    for name in chosen:
        for parent in PurePosixPath(name).parents:
            if parent.as_posix() in chosen:
                raise ValueError('Conflict of target files and directories:' + name)
    return chosen, sorted(set(omitted))


def check_snapshot(run, plan):
    expected = {item['target']: item for item in plan['files']}
    actual = {p.relative_to(run.path / 'source').as_posix()
              for p in (run.path / 'source').rglob('*') if p.is_file() or p.is_symlink()}
    if actual != set(expected):
        raise ValueError('Internal copy file collection has changed; please repreparate and see changes')
    for name, item in expected.items():
        path = run.path / 'source' / name
        if path.is_symlink() or digest(path) != item['sha256'] or bool(path.stat().st_mode & 0o111) != item['executable']:
            raise ValueError('internal copy changed; please repreparate and see changes:' + name)


def bilingual_match(target, rule):
    return target.startswith(rule) if rule.endswith('/') else target == rule


def chinese_lines(text):
    return [number for number, line in enumerate(text.splitlines(), start=1)
            if any(char == '0' or unicodedata.name(char, '').startswith(
                ('CJK UNIFIED IDEOGRAPH-', 'CJK COMPATIBILITY IDEOGRAPH-'))
                for char in line if not char.isascii())]


def read_publication_text(path):
    data = path.read_bytes()
    if data.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        encoding = 'utf-32'
    elif data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        encoding = 'utf-16'
    elif b'\x00' in data:
        return None
    else:
        encoding = 'utf-8-sig'
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        return None


def check_publication_language(run, files, bilingual):
    findings = []
    unread = []
    for item in files:
        target = item['target']
        if any(bilingual_match(target, rule) for rule in bilingual):
            continue
        if chinese_lines(target):
            findings.append({'path': target, 'location': 'path'})
        content = read_publication_text(run.path / 'source' / target)
        if content is None:
            unread.append(target)
            continue
        lines = chinese_lines(content)
        if lines:
            findings.append({'path': target, 'location': 'content', 'lines': lines})
    save(run.path / 'language-check.json', {
        'purpose': 'Record Chinese-character findings before GitHub publication.',
        'scope': 'Selected destination paths and decodable text in this run.',
        'bilingual_paths': bilingual,
        'findings': findings,
        'unread_as_text': unread,
    })
    run.log('language-check.json', 'Recording of the results of language tests and bilingual coverage')
    if findings:
        locations = [item['path'] + (':' + str(item['lines'][0]) if 'lines' in item else '(Path Name)')
                     for item in findings[:8]]
        raise ValueError('Published in Chinese, please re-preparate after translation in internal copy.'
                         'I’ll see you in full position. language-check.json.\n' + '\n'.join(locations))


def check_metadata_language(**fields):
    for name, value in fields.items():
        if value and chinese_lines(value):
            raise ValueError('GitHub The publication of the notes should be in English:' + name)


def prepare(args):
    root = args.root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('--root It should be the root source directory')
    repo = repository(args.repo) if args.repo else None
    if args.new and (not repo or not args.visibility):
        raise ValueError('Make it clear when preparing the new warehouse. --repo and --visibility')
    if args.visibility and not args.new:
        raise ValueError('--visibility For the new warehouse only')
    if args.delete and (not repo or args.new):
        raise ValueError('Remove the target file to specify an existing repository')
    if args.bilingual_path and not repo:
        raise ValueError('Bilingual path to specify GitHub Preparation for the release of targets')
    run = Run(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8], create=True)
    run.record(state='preparing')
    chosen, omitted = collect(root, args.map, args.exclude, run)
    bilingual = sorted({relative(path.removesuffix('/')) + ('/' if path.endswith('/') else '')
                        for path in args.bilingual_path})
    for rule in bilingual:
        if not any(bilingual_match(target, rule) for target in chosen):
            raise ValueError('Bilingual path does not match any of the current release documents:' + rule)
    run.branch(args.base)
    branch = run.branch(args.branch or args.base)
    rows = []
    for target, source in sorted(chosen.items()):
        before = digest(source)
        output = internal(run.path / 'source' / target)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output)
        if before != digest(source) or before != digest(output):
            raise ValueError('Source changed during copying. Reprepared.:' + str(source))
        rows.append({'source': source.relative_to(root).as_posix(), 'target': target,
                     'sha256': before, 'executable': bool(output.stat().st_mode & 0o111)})
    run.log('source', 'Save a stand-alone copy of the user selected content')
    if repo:
        check_publication_language(run, rows, bilingual)
    deletes = [relative(p) for p in args.delete]
    if set(deletes).intersection(chosen):
        raise ValueError('The same document cannot be published and deleted')
    base_commit = None
    if repo and not args.new:
        if branch != args.base and run.remote_head(repo, branch):
            raise ValueError('Target branch already exists; it is also designated as a direct update --base with --branch,Or choose a new branch')
        run.git('clone', '--no-checkout', '--single-branch', '--branch', args.base,
                '--no-recurse-submodules', 'https://github.com/' + repo + '.git',
                str(run.checkout), cwd=run.path, auth=True)
        base_commit = run.git('rev-parse', 'HEAD').stdout.strip()
        if branch == args.base:
            run.git('checkout', args.base)
        else:
            run.git('checkout', '-b', branch)
    else:
        run.checkout.mkdir()
        run.git('init', '--initial-branch=' + branch)
    for target in deletes:
        run.git('--literal-pathspecs', 'rm', '--', target)
    for item in rows:
        target = run.checkout / item['target']
        internal(target)
        for part in [target, *target.parents]:
            if part == run.checkout.parent:
                break
            if part.is_symlink():
                raise ValueError('Target path contains symbolic links:' + item['target'])
        if target.is_dir():
            raise ValueError('Target has a directory with the same name.:' + item['target'])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run.path / 'source' / item['target'], target)
    paths = [r['target'] for r in rows]
    for start in range(0, len(paths), 100):
        run.git('--literal-pathspecs', 'add', '-f', '--', *paths[start:start + 100])
    tree = run.git('write-tree').stdout.strip()
    diff = run.git('diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv').stdout
    (run.path / 'changes.diff').write_text(diff, encoding='utf-8')
    summary = run.git('diff', '--cached', '--stat', '--no-ext-diff').stdout
    plan = {'purpose': 'Describe the exact publication prepared from independent file copies.',
        'scope': 'Only this run and the explicitly selected repository paths.',
        'run': run.name, 'source_root': str(root), 'repo': repo, 'new': args.new,
        'visibility': args.visibility, 'base': args.base, 'branch': branch,
        'base_commit': base_commit, 'tree': tree, 'files': rows, 'delete': deletes,
        'omitted': omitted, 'bilingual_paths': bilingual, 'summary': summary, 'has_changes': bool(diff)}
    save(run.path / 'plan.json', plan)
    run.log('checkout', 'Prepare target warehouse and identify selected changes')
    run.log('plan.json', 'Save source, target path, file summary and scope of release')
    run.log('changes.diff', 'Save actual discrepancies to be published')
    run.record(state='prepared', last_attempt='succeeded', last_error=None)
    print(json.dumps({'run': run.name, 'files': len(rows), 'repo': repo, 'branch': branch,
        'source': str(run.path / 'source'), 'diff': str(run.path / 'changes.diff'),
        'omitted': omitted, 'summary': summary}, ensure_ascii=False, indent=2))


def publish(args):
    run = Run(args.run)
    plan = run.load('plan.json')
    repo = repository(plan['repo'] or '')
    check_snapshot(run, plan)
    check_publication_language(run, plan['files'], plan.get('bilingual_paths', []))
    if run.git('write-tree').stdout.strip() != plan['tree']:
        raise ValueError('The content to be submitted has changed; please repreparate and view the differences')
    if run.git('diff', '--name-only', '--no-ext-diff').stdout.strip():
        raise ValueError('There are still unprepared changes in the internal warehouse; please re-preparate')
    if run.git('ls-files', '--others', '--exclude-standard').stdout.strip():
        raise ValueError('Additional documents appear at the internal warehouse; please repreparate')
    if args.pr and (plan['new'] or plan['branch'] == plan['base'] or not args.title or not args.body_file):
        raise ValueError('PR Need to have a warehouse, a new branch, and --title,--body-file')
    if args.pr and not plan['has_changes']:
        raise ValueError('No difference to be published, no need to create this PR')
    if args.draft and not args.pr:
        raise ValueError('--draft Use this command for drafts PR,Please provide at the same time. --pr')
    body = internal(args.body_file).read_text(encoding='utf-8') if args.body_file else None
    check_metadata_language(commit_message=args.message, pull_request_title=args.title,
                            pull_request_body=body)
    commit = run.receipt.get('commit')
    if not commit:
        if plan['has_changes']:
            author = []
            if bool(args.author_name) != bool(args.author_email):
                raise ValueError('It’s also available. --author-name and --author-email')
            if args.author_name:
                author = ['-c', 'user.name=' + args.author_name, '-c', 'user.email=' + args.author_email]
            run.git(*author, 'commit', '-m', args.message)
            commit = run.git('rev-parse', 'HEAD').stdout.strip()
        elif plan['base_commit']:
            commit = plan['base_commit']
        else:
            raise ValueError('No content to submit')
        run.record(commit=commit, state='committed')
    if run.git('rev-parse', 'HEAD').stdout.strip() != commit:
        raise ValueError('Local submission changed, release stopped')
    if plan['has_changes']:
        message = run.git('show', '-s', '--format=%B', commit).stdout
        check_metadata_language(commit_message=message)
    if plan['new'] and not run.receipt.get('repository_created'):
        run.command(['gh', 'repo', 'create', repo, '--' + plan['visibility']], auth=True)
        run.record(repository_created=True, state='repository_created')
    remote = run.remote_head(repo, plan['branch'])
    if remote != commit:
        expected = plan['base_commit'] if plan['branch'] == plan['base'] else None
        if remote != expected:
            raise ValueError('Target branch changed; this copy is retained, re-prepared after viewing remote status')
        if not plan['new'] and run.remote_head(repo, plan['base']) != plan['base_commit']:
            raise ValueError('Target base branch has changed, please repreparate the difference.')
        run.git('push', 'https://github.com/' + repo + '.git',
                commit + ':refs/heads/' + plan['branch'], auth=True)
    url = 'https://github.com/' + repo + '/commit/' + commit
    run.record(repo=repo, branch=plan['branch'], commit_url=url, state='pushed')
    if args.pr:
        found = run.command(['gh', 'pr', 'list', '--repo', repo, '--head', plan['branch'],
            '--base', plan['base'], '--state', 'open', '--json', 'url'], auth=True)
        matches = json.loads(found.stdout)
        if matches:
            pr_url = matches[0]['url']
        else:
            body_path = run.path / 'pull_request_body.md'
            body_path.write_text(body, encoding='utf-8')
            run.log('pull_request_body.md', 'Save this one PR Annotations')
            command = ['gh', 'pr', 'create', '--repo', repo, '--base', plan['base'],
                '--head', plan['branch'], '--title', args.title, '--body-file', str(body_path)]
            if args.draft:
                command.append('--draft')
            pr_url = run.command(command, auth=True).stdout.strip()
        run.record(pr_url=pr_url, state='pull_request_created')
    run.record(last_attempt='succeeded', last_error=None)
    print(json.dumps(run.receipt, ensure_ascii=False, indent=2))


def pack(run):
    plan = run.load('plan.json')
    check_snapshot(run, plan)
    if plan['repo']:
        check_publication_language(run, plan['files'], plan.get('bilingual_paths', []))
    directory = internal(run.path / 'release')
    directory.mkdir(exist_ok=True)
    output = directory / ('publication_' + run.name + '.zip')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for item in plan['files']:
            archive.write(run.path / 'source' / item['target'], item['target'])
    run.log(output.relative_to(run.path), 'Save selected file ZIP Version Package')
    run.record(package=output.relative_to(run.path).as_posix(), package_sha256=digest(output),
               last_attempt='succeeded', last_error=None)
    return output


def release(args):
    run = Run(args.run)
    plan = run.load('plan.json')
    repo = repository(plan['repo'] or '')
    commit = run.receipt.get('commit')
    if not commit or not run.receipt.get('commit_url'):
        raise ValueError('Release prepared content and create for this submission Release')
    if not args.tag or args.tag.startswith('-'):
        raise ValueError('Provide a clear version of the label')
    notes = internal(args.notes_file).read_text(encoding='utf-8')
    check_metadata_language(release_tag=args.tag, release_title=args.title, release_notes=notes)
    run.git('check-ref-format', 'refs/tags/' + args.tag)
    ref = 'refs/tags/' + args.tag
    existing = run.git('ls-remote', '--tags', 'https://github.com/' + repo + '.git',
                       ref, ref + '^{}', auth=True, cwd=run.path)
    tags = {line.split()[1]: line.split()[0] for line in existing.stdout.splitlines() if line.strip()}
    tagged_commit = tags.get(ref + '^{}', tags.get(ref))
    if tagged_commit and tagged_commit != commit:
        raise ValueError('Existing version labels point to other submissions, please clearly select another version or handle existing labels')
    output = pack(run)
    notes_path = run.path / 'release_notes.md'
    notes_path.write_text(notes, encoding='utf-8')
    run.log('release_notes.md', 'Save Version Description')
    command = ['gh', 'release', 'create', args.tag, str(output), '--repo', repo,
        '--target', commit, '--title', args.title, '--notes-file', str(notes_path)]
    if args.draft:
        command.append('--draft')
    url = run.command(command, auth=True).stdout.strip()
    run.record(release_url=url, tag=args.tag, draft=args.draft, state='release_created',
               last_attempt='succeeded', last_error=None)
    print(json.dumps(run.receipt, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('prepare', help='Duplicate and prepare differences only, not modified GitHub')
    command.add_argument('--root', type=Path, required=True)
    command.add_argument('--map', action='append', required=True)
    command.add_argument('--exclude', action='append', default=[])
    command.add_argument('--repo')
    command.add_argument('--base', default='main')
    command.add_argument('--branch')
    command.add_argument('--new', action='store_true')
    command.add_argument('--visibility', choices=['private', 'public'])
    command.add_argument('--delete', action='append', default=[])
    command.add_argument('--bilingual-path', action='append', default=[],
                         help='Retain or maintain target documents that explicitly support bilingualism / End of destination directory')
    command = commands.add_parser('publish', help='Submission and forwarding of prepared content in accordance with mandates')
    command.add_argument('--run', required=True)
    command.add_argument('--message', required=True)
    command.add_argument('--author-name')
    command.add_argument('--author-email')
    command.add_argument('--pr', action='store_true')
    command.add_argument('--title')
    command.add_argument('--body-file', type=Path)
    command.add_argument('--draft', action='store_true')
    command = commands.add_parser('pack', help='Yes. Skill _Other Organiser ZIP')
    command.add_argument('--run', required=True)
    command = commands.add_parser('release', help='Create for published submission GitHub Release')
    command.add_argument('--run', required=True)
    command.add_argument('--tag', required=True)
    command.add_argument('--title', required=True)
    command.add_argument('--notes-file', type=Path, required=True)
    command.add_argument('--draft', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            prepare(args)
        elif args.command == 'publish':
            publish(args)
        elif args.command == 'release':
            release(args)
        else:
            print(pack(Run(args.run)))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        message = str(error)
        if ACTIVE_RUN is not None:
            if ACTIVE_RUN.token:
                message = message.replace(ACTIVE_RUN.token, '[credential]')
            try:
                ACTIVE_RUN.record(last_attempt='failed', last_error=message)
            except OSError:
                pass
            message += '\n Mission information:' + str(ACTIVE_RUN.path)
        parser.exit(2, 'GitHub Publish: ' + message + '\n')


if __name__ == '__main__':
    main()
