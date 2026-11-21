"""Purpose and main function: Download Assigned Hugging Face Repository, create source copy, working copy and version record.

Scope of application: user-designated models, data sets and Space warehouse;all downloads and caches are stored within this skill and stay as they are at a remote end.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile

SKILL = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def relative(value):
    parts = value.split('/')
    if not value or '\\' in value or PurePosixPath(value).is_absolute() or any(p in {'', '.', '..'} for p in parts):
        raise ValueError('Use an ordinary relative name')
    return value


def save(task, path, value, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    log(task, path, content)


def log(task, path, content):
    with (task / 'log_updates.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
            'path': path.relative_to(SKILL).as_posix(), 'content': content,
            'source': 'scripts/download_assets.py; huggingface_hub'}, ensure_ascii=False) + '\n')


def same_files(left, right):
    """Recognize complete source copies from tasks created before phase records."""
    import filecmp

    expected = {p.relative_to(right) for p in right.rglob('*') if p.is_file()}
    actual = {p.relative_to(left) for p in left.rglob('*') if p.is_file()}
    return actual == expected and all(filecmp.cmp(left / p, right / p, shallow=False) for p in expected)


def staged_copy(source, destination):
    """Publish complete directories atomically and preserve existing working copies."""
    if destination.exists():
        if not destination.is_dir():
            raise ValueError('Repository copy must be a directory')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name('.' + destination.name + '-copying')
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(source, staging, symlinks=False)
    staging.rename(destination)


def download(task_name, repositories, *, resume=False):
    relative(task_name)
    if '/' in task_name:
        raise ValueError('Task name must be one directory name')
    task = (SKILL / 'results' / task_name).resolve()
    task.relative_to((SKILL / 'results').resolve())
    task.mkdir(parents=True, exist_ok=resume)
    cache = task / 'cache' / 'hub'
    scratch = task / 'tmp'
    scratch.mkdir(exist_ok=True)
    # Keep authentication at its existing location and isolate downloaded content.
    os.environ['HF_HUB_CACHE'] = str(cache)
    os.environ['HF_XET_CACHE'] = str(task / 'cache' / 'xet')
    for variable in ('TMPDIR', 'TMP', 'TEMP'):
        os.environ[variable] = str(scratch)
    from huggingface_hub import HfApi, snapshot_download
    api = HfApi()
    plan_path = task / 'inventory.json'
    if resume:
        plan = json.loads(plan_path.read_text(encoding='utf-8'))
        requested = {(kind, name) for kind, name in repositories}
        if requested != {(r['repo_type'], r['repo_id']) for r in plan['repositories']}:
            raise ValueError('Resume with the original repository selection')
    else:
        plan = {'purpose': 'Record downloads, local location and completion status of selected repository.',
                'scope': 'A copy of this download source and a copy of the job.',
                'created_at': datetime.now(timezone.utc).isoformat(), 'repositories': []}
        for kind, name in repositories:
            relative(name)
            if len(name.split('/')) != 2 or kind not in {'space', 'dataset', 'model'}:
                raise ValueError('Select space, dataset or model and an owner/repository name')
            info = api.repo_info(name, repo_type=kind, files_metadata=True)
            plan['repositories'].append({'repo_id': name, 'repo_type': kind, 'revision': info.sha,
                'url': 'https://huggingface.co/' + {'space': 'spaces/', 'dataset': 'datasets/', 'model': ''}[kind] + name,
                'private': info.private, 'status': 'planned',
                'files': [{'path': item.rfilename, 'size': item.size} for item in info.siblings]})
        save(task, plan_path, plan, 'Record selected remote commits before downloading')
    failed = []
    for record in plan['repositories']:
        kind, name = record['repo_type'], record['repo_id']
        owner, repository = name.split('/')
        base = task / owner / {'space': 'spaces', 'dataset': 'datasets', 'model': 'models'}[kind] / repository
        source, checkout = base / 'source', base / 'checkout'
        if record['status'] == 'complete' and source.is_dir() and checkout.is_dir() and (base / 'repository.json').is_file():
            continue

        def checkpoint(phase):
            record['phase'] = phase
            save(task, plan_path, plan, 'Record repository copy phase: ' + phase)

        try:
            if source.is_dir() and record.get('source_revision') == record['revision']:
                snapshot = source
            else:
                checkpoint('downloading')
                snapshot = Path(snapshot_download(name, repo_type=kind, revision=record['revision'],
                    cache_dir=cache, max_workers=4))
            if source.exists() and record.get('source_revision') != record['revision']:
                # Older interrupted tasks had no phase record. Compare their source once.
                if not same_files(source, snapshot):
                    raise ValueError('Existing source differs from the pinned snapshot')
            record['source_revision'] = record['revision']
            checkpoint('source_copying')
            staged_copy(snapshot, source)
            log(task, source, 'Complete source snapshot at ' + record['revision'])
            checkpoint('source_complete')
            checkpoint('checkout_copying')
            staged_copy(source, checkout)
            log(task, checkout, 'Keep independent working copy and its existing edits')
            checkpoint('checkout_complete')
            record.update(status='complete', phase='complete', source=str(source.relative_to(task)),
                          checkout=str(checkout.relative_to(task)),
                          file_count=len(record['files']),
                          known_bytes=sum(item['size'] or 0 for item in record['files']))
            record.pop('error_type', None)
            record.pop('error_code', None)
            save(task, base / 'repository.json', {'purpose': 'Record the remote source and regular submission of local repository copies.',
                'scope': 'Table of contents source with checkout Sources and list of documents.', **record}, 'Record downloaded repository identity')
            checkpoint('complete')
            print(json.dumps({'repo_id': name, 'status': 'complete', 'files': record['file_count'],
                              'checkout': str(checkout)}, ensure_ascii=False), flush=True)
        except Exception as error:
            record.update(status='incomplete', error_type=type(error).__name__)
            if isinstance(error, ValueError) and str(error) == 'Existing source differs from the pinned snapshot':
                record['error_code'] = 'source_differs_from_pinned_revision'
            for partial in (base / '.source-copying', base / '.checkout-copying'):
                if partial.exists():
                    log(task, partial, 'Keep partial copy for the next resume attempt')
            failed.append(name)
            print(json.dumps({'repo_id': name, 'status': 'incomplete', 'phase': record.get('phase'),
                              'error_type': type(error).__name__, 'error_code': record.get('error_code')}), flush=True)
        save(task, plan_path, plan, 'Update actual download completion status')
    if (task / 'cache').exists():
        log(task, task / 'cache', 'Keep official Hub download cache for this task')
    print(json.dumps({'task': str(task), 'completed': sum(r['status'] == 'complete' for r in plan['repositories']),
                      'incomplete': failed}, ensure_ascii=False), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True, help='Named directory inside this skill results')
    parser.add_argument('--repo', action='append', required=True, help='space:owner/name, dataset:owner/name or model:owner/name')
    parser.add_argument('--resume', action='store_true', help='Resume unchanged selection after interrupted downloads')
    args = parser.parse_args()
    try:
        repositories = [tuple(value.split(':', 1)) for value in args.repo]
        if any(len(item) != 2 for item in repositories) or len(set(repositories)) != len(repositories):
            raise ValueError('Provide distinct type:owner/name selections')
        raise SystemExit(download(args.task, repositories, resume=args.resume))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, 'Download preparation failed: ' + type(error).__name__ + '\n')
