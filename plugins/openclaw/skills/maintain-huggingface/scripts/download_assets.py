"""目的和主要功能：下载指定 Hugging Face 仓库，建立来源副本、工作副本和版本记录。

适用范围：用户指定的模型、数据集与 Space 仓库；全部下载与缓存保存在本技能内，远端保持原样。
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys

SKILL = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get('RH_SKILL_WORK_DIR') or SKILL).expanduser().resolve()
sys.dont_write_bytecode = True


def relative(value):
    parts = value.split('/')
    if not value or '\\' in value or PurePosixPath(value).is_absolute() or any(p in {'', '.', '..'} for p in parts):
        raise ValueError('Use an ordinary relative name')
    return value


def save(task, path, value, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log(task, path, content)


def log(task, path, content):
    with (task / 'log_updates.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(),
            'path': path.relative_to(WORK).as_posix(), 'content': content,
            'source': 'scripts/download_assets.py; huggingface_hub'}, ensure_ascii=False) + '\n')


def download(task_name, repositories, *, resume=False):
    relative(task_name)
    if '/' in task_name:
        raise ValueError('Task name must be one directory name')
    task = (WORK / 'results' / task_name).resolve()
    task.relative_to((WORK / 'results').resolve())
    task.mkdir(parents=True, exist_ok=resume)
    cache = task / 'cache' / 'hub'
    # Keep authentication at its existing location and isolate downloaded content.
    os.environ['HF_HUB_CACHE'] = str(cache)
    os.environ['HF_XET_CACHE'] = str(task / 'cache' / 'xet')
    from huggingface_hub import HfApi, snapshot_download
    api = HfApi()
    plan_path = task / 'inventory.json'
    if resume:
        plan = json.loads(plan_path.read_text(encoding='utf-8'))
        requested = {(kind, name) for kind, name in repositories}
        if requested != {(r['repo_type'], r['repo_id']) for r in plan['repositories']}:
            raise ValueError('Resume with the original repository selection')
    else:
        plan = {'purpose': '记录选定仓库的下载版本、本地位置与完成状态。',
                'scope': '本次下载的来源副本与工作副本。',
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
        if record['status'] == 'complete':
            continue
        owner, repository = name.split('/')
        base = task / owner / {'space': 'spaces', 'dataset': 'datasets', 'model': 'models'}[kind] / repository
        source, checkout = base / 'source', base / 'checkout'
        try:
            snapshot = Path(snapshot_download(name, repo_type=kind, revision=record['revision'],
                cache_dir=cache, max_workers=4))
            # Copy the pinned snapshot's real bytes, independently of cache symlinks.
            if source.exists():
                raise ValueError('Source already exists; preserve it and inspect the unfinished task')
            shutil.copytree(snapshot, source, symlinks=False)
            log(task, source, 'Download source snapshot at ' + record['revision'])
            if checkout.exists():
                raise ValueError('Working copy already exists; preserve existing local edits')
            shutil.copytree(source, checkout, symlinks=False)
            log(task, checkout, 'Create independent working copy from downloaded source')
            record.update(status='complete', source=str(source.relative_to(task)),
                          checkout=str(checkout.relative_to(task)),
                          file_count=len(record['files']),
                          known_bytes=sum(item['size'] or 0 for item in record['files']))
            save(task, base / 'repository.json', {'purpose': '记录本地仓库副本的远端来源及固定提交。',
                'scope': '同目录 source 与 checkout 的来源和文件清单。', **record}, 'Record downloaded repository identity')
            print(json.dumps({'repo_id': name, 'status': 'complete', 'files': record['file_count'],
                              'checkout': str(checkout)}, ensure_ascii=False), flush=True)
        except Exception as error:
            # Persist a bounded error type; authenticated URLs and credentials stay out of logs.
            record.update(status='incomplete', error_type=type(error).__name__)
            failed.append(name)
            print(json.dumps({'repo_id': name, 'status': 'incomplete', 'error_type': type(error).__name__}), flush=True)
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
