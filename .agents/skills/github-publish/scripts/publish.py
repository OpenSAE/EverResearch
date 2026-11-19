"""目的和主要功能：复制选定文件，检查发布语言，在 Skill 内准备 Git 差异、提交、版本包及 GitHub 发布。

适用范围：github-publish Skill 的明确发布任务；原发布目录只读，所有本地写入位于 Skill 内。
运行使用 Python 标准库、Git 与 GitHub CLI，读取已有登录；默认仅准备，远程写入使用独立命令。
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
        raise ValueError('路径应为相对路径，根位置使用 .')
    parts = value.split('/')
    if PurePosixPath(value).is_absolute() or any(p in {'', '.', '..'} for p in parts):
        raise ValueError('路径应位于所选目录内：' + value)
    if any(p.lower() == '.git' for p in parts):
        raise ValueError('Git 元数据由内部仓库自行管理')
    return value


def repository(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value):
        raise ValueError('仓库使用 owner/name 格式')
    if any(p in {'.', '..'} for p in value.split('/')):
        raise ValueError('仓库名称无效')
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
            raise ValueError('任务标识只能包含字母、数字、连字符和下划线')
        self.path = internal(RESULTS / name)
        if create:
            self.path.mkdir(parents=True, exist_ok=False)
        elif not self.path.is_dir():
            raise ValueError('任务不存在：' + name)
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
        self.log('result.json', '更新实际发布状态')

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
                        raise ValueError('需要已有的 GitHub 登录，或通过环境提供 GH_TOKEN')
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
            raise ValueError(args[0] + ' 操作未完成：' + reason[:3000])
        return result

    def git(self, *args, auth=False, cwd=None, allow_failure=False):
        return self.command(['git', '-c', 'core.hooksPath=' + str(self.path / 'hooks'),
            '-c', 'commit.gpgSign=false', '-c', 'core.autocrlf=false', '-c', 'core.fsmonitor=false',
            '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
            *args], cwd=cwd or self.checkout, auth=auth, allow_failure=allow_failure)

    def branch(self, value):
        if value.startswith('-'):
            raise ValueError('分支名称无效')
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
            raise ValueError('--map 使用 来源相对路径=目标相对路径')
        source_name, destination = mapping.split('=', 1)
        source_name = relative(source_name, root=True)
        destination = relative(destination, root=True)
        source = root / source_name
        # Reject links rather than following a link back into the original object.
        for part in [source, *source.parents]:
            if part == root.parent:
                break
            if part.is_symlink():
                raise ValueError('选择实际文件或目录，当前路径包含符号链接：' + str(source))
        source = source.resolve(strict=True)
        source.relative_to(root)
        if source.is_relative_to(run.path):
            raise ValueError('本次任务的产物不作为自身输入')
        if not (source.is_dir() or source.is_file()):
            raise ValueError('仅接收普通文件或目录：' + str(source))
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
                raise ValueError('仅复制普通文件；请单独处理链接或特殊文件：' + str(path))
            suffix = path.relative_to(source).as_posix() if source.is_dir() else ''
            target = '/'.join(p for p in [destination, suffix] if p)
            if not target:
                target = source.name
            target = relative(target)
            if target in chosen:
                raise ValueError('多个来源对应同一目标：' + target)
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
                        raise ValueError('目录包含符号链接：' + str(path))
                    kept.append(name)
                dirs[:] = kept
                for name in sorted(files):
                    path = parent / name
                    if not excluded(path):
                        add(path)
    if not chosen:
        raise ValueError('选定范围内没有要发布的普通文件')
    for name in chosen:
        for parent in PurePosixPath(name).parents:
            if parent.as_posix() in chosen:
                raise ValueError('目标文件和目录发生冲突：' + name)
    return chosen, sorted(set(omitted))


def check_snapshot(run, plan):
    expected = {item['target']: item for item in plan['files']}
    actual = {p.relative_to(run.path / 'source').as_posix()
              for p in (run.path / 'source').rglob('*') if p.is_file() or p.is_symlink()}
    if actual != set(expected):
        raise ValueError('内部副本的文件集合已变化；请重新准备并查看变化')
    for name, item in expected.items():
        path = run.path / 'source' / name
        if path.is_symlink() or digest(path) != item['sha256'] or bool(path.stat().st_mode & 0o111) != item['executable']:
            raise ValueError('内部副本已变化；请重新准备并查看变化：' + name)


def bilingual_match(target, rule):
    return target.startswith(rule) if rule.endswith('/') else target == rule


def chinese_lines(text):
    return [number for number, line in enumerate(text.splitlines(), start=1)
            if any(char == '〇' or unicodedata.name(char, '').startswith(
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
    run.log('language-check.json', '记录发布语言检查结果和双语范围')
    if findings:
        locations = [item['path'] + (':' + str(item['lines'][0]) if 'lines' in item else '（路径名称）')
                     for item in findings[:8]]
        raise ValueError('发布内容包含中文，请在内部副本中翻译后重新准备。'
                         '完整位置见 language-check.json。\n' + '\n'.join(locations))


def check_metadata_language(**fields):
    for name, value in fields.items():
        if value and chinese_lines(value):
            raise ValueError('GitHub 发布说明应使用英文：' + name)


def prepare(args):
    root = args.root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('--root 应为来源根目录')
    repo = repository(args.repo) if args.repo else None
    if args.new and (not repo or not args.visibility):
        raise ValueError('准备新仓库时明确提供 --repo 和 --visibility')
    if args.visibility and not args.new:
        raise ValueError('--visibility 仅用于新仓库')
    if args.delete and (not repo or args.new):
        raise ValueError('删除目标文件需要指定已有仓库')
    if args.bilingual_path and not repo:
        raise ValueError('双语路径用于指定 GitHub 目标的发布准备')
    run = Run(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8], create=True)
    run.record(state='preparing')
    chosen, omitted = collect(root, args.map, args.exclude, run)
    bilingual = sorted({relative(path.removesuffix('/')) + ('/' if path.endswith('/') else '')
                        for path in args.bilingual_path})
    for rule in bilingual:
        if not any(bilingual_match(target, rule) for target in chosen):
            raise ValueError('双语路径未匹配任何本次发布文件：' + rule)
    run.branch(args.base)
    branch = run.branch(args.branch or args.base)
    rows = []
    for target, source in sorted(chosen.items()):
        before = digest(source)
        output = internal(run.path / 'source' / target)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output)
        if before != digest(source) or before != digest(output):
            raise ValueError('复制期间来源发生变化，请重新准备：' + str(source))
        rows.append({'source': source.relative_to(root).as_posix(), 'target': target,
                     'sha256': before, 'executable': bool(output.stat().st_mode & 0o111)})
    run.log('source', '保存用户选定内容的独立副本')
    if repo:
        check_publication_language(run, rows, bilingual)
    deletes = [relative(p) for p in args.delete]
    if set(deletes).intersection(chosen):
        raise ValueError('同一文件不能既发布又删除')
    base_commit = None
    if repo and not args.new:
        if branch != args.base and run.remote_head(repo, branch):
            raise ValueError('目标分支已存在；直接更新时将它同时指定为 --base 与 --branch，或选择新分支')
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
                raise ValueError('目标路径包含符号链接：' + item['target'])
        if target.is_dir():
            raise ValueError('目标已有同名目录：' + item['target'])
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
    run.log('checkout', '准备目标仓库及明确选定的变化')
    run.log('plan.json', '保存来源、目标路径、文件摘要和发布范围')
    run.log('changes.diff', '保存待发布的实际差异')
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
        raise ValueError('待提交内容已变化；请重新准备并查看差异')
    if run.git('diff', '--name-only', '--no-ext-diff').stdout.strip():
        raise ValueError('内部仓库还有未准备的修改；请重新准备')
    if run.git('ls-files', '--others', '--exclude-standard').stdout.strip():
        raise ValueError('内部仓库出现额外文件；请重新准备')
    if args.pr and (plan['new'] or plan['branch'] == plan['base'] or not args.title or not args.body_file):
        raise ValueError('PR 需要已有仓库、新分支以及 --title、--body-file')
    if args.pr and not plan['has_changes']:
        raise ValueError('没有待发布差异，本次无需创建 PR')
    if args.draft and not args.pr:
        raise ValueError('--draft 在此命令中用于草稿 PR，请同时提供 --pr')
    body = internal(args.body_file).read_text(encoding='utf-8') if args.body_file else None
    check_metadata_language(commit_message=args.message, pull_request_title=args.title,
                            pull_request_body=body)
    commit = run.receipt.get('commit')
    if not commit:
        if plan['has_changes']:
            author = []
            if bool(args.author_name) != bool(args.author_email):
                raise ValueError('同时提供 --author-name 和 --author-email')
            if args.author_name:
                author = ['-c', 'user.name=' + args.author_name, '-c', 'user.email=' + args.author_email]
            run.git(*author, 'commit', '-m', args.message)
            commit = run.git('rev-parse', 'HEAD').stdout.strip()
        elif plan['base_commit']:
            commit = plan['base_commit']
        else:
            raise ValueError('没有可提交内容')
        run.record(commit=commit, state='committed')
    if run.git('rev-parse', 'HEAD').stdout.strip() != commit:
        raise ValueError('本地提交已变化，停止发布')
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
            raise ValueError('目标分支已变化；保留本次副本，请查看远程状态后重新准备')
        if not plan['new'] and run.remote_head(repo, plan['base']) != plan['base_commit']:
            raise ValueError('目标基础分支已变化，请重新准备差异')
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
            run.log('pull_request_body.md', '保存本次 PR 说明')
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
    run.log(output.relative_to(run.path), '保存选定文件的 ZIP 版本包')
    run.record(package=output.relative_to(run.path).as_posix(), package_sha256=digest(output),
               last_attempt='succeeded', last_error=None)
    return output


def release(args):
    run = Run(args.run)
    plan = run.load('plan.json')
    repo = repository(plan['repo'] or '')
    commit = run.receipt.get('commit')
    if not commit or not run.receipt.get('commit_url'):
        raise ValueError('先发布已准备内容，再为该提交创建 Release')
    if not args.tag or args.tag.startswith('-'):
        raise ValueError('提供明确的版本标签')
    notes = internal(args.notes_file).read_text(encoding='utf-8')
    check_metadata_language(release_tag=args.tag, release_title=args.title, release_notes=notes)
    run.git('check-ref-format', 'refs/tags/' + args.tag)
    ref = 'refs/tags/' + args.tag
    existing = run.git('ls-remote', '--tags', 'https://github.com/' + repo + '.git',
                       ref, ref + '^{}', auth=True, cwd=run.path)
    tags = {line.split()[1]: line.split()[0] for line in existing.stdout.splitlines() if line.strip()}
    tagged_commit = tags.get(ref + '^{}', tags.get(ref))
    if tagged_commit and tagged_commit != commit:
        raise ValueError('已有版本标签指向其他提交，请明确选择其他版本或处理已有标签')
    output = pack(run)
    notes_path = run.path / 'release_notes.md'
    notes_path.write_text(notes, encoding='utf-8')
    run.log('release_notes.md', '保存版本说明')
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
    command = commands.add_parser('prepare', help='只复制和准备差异，不修改 GitHub')
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
                         help='保留明确支持双语的目标文件或以 / 结尾的目标目录')
    command = commands.add_parser('publish', help='按任务授权提交并推送已准备内容')
    command.add_argument('--run', required=True)
    command.add_argument('--message', required=True)
    command.add_argument('--author-name')
    command.add_argument('--author-email')
    command.add_argument('--pr', action='store_true')
    command.add_argument('--title')
    command.add_argument('--body-file', type=Path)
    command.add_argument('--draft', action='store_true')
    command = commands.add_parser('pack', help='在 Skill 内生成选定副本的 ZIP')
    command.add_argument('--run', required=True)
    command = commands.add_parser('release', help='为已发布提交创建 GitHub Release')
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
            message += '\n任务资料：' + str(ACTIVE_RUN.path)
        parser.exit(2, 'GitHub Publish: ' + message + '\n')


if __name__ == '__main__':
    main()
