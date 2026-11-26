"""Launch maintained TRL recipes through the installed trainer commands.

Use the same pinned data, models, and training arguments for the bounded gate
and formal operation. Each invocation writes an independent experiment record.
"""

import math
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4

from huggingface_hub import snapshot_download

from base.experiment_runner import write_json
from tasks.precheck.training import check_training, execute, installed_command, readable_model


def recipe_command(name, config, recipe):
    model = config['model']
    data = config['dataset']
    benchmark = config['benchmark']
    batch_size = str(recipe['batch_size'])
    command = [
        *installed_command(name), '--dataset_name', data['repository'], '--dataset_config', recipe['dataset_configuration'],
        '--dataset_revision', benchmark['dataset_revision'], '--dataset_train_split', data['split'],
        '--dataset_test_split', 'test', '--model_name_or_path', model['repository'], '--model_revision', model['revision'],
        '--per_device_train_batch_size', batch_size, '--per_device_eval_batch_size', batch_size,
        '--gradient_accumulation_steps', '1', '--dataloader_num_workers', '0', '--use_cpu', 'true', '--bf16', 'false',
        '--report_to', 'none', *recipe['arguments'],
    ]
    if recipe.get('teacher_model'):
        command.extend(['--teacher_model_name_or_path', model['repository'], '--teacher_model_revision', model['revision']])
    if recipe.get('reward_model'):
        reward = snapshot_download(
            benchmark['reward_repository'], revision=benchmark['reward_revision'], local_files_only=True
        )
        command.extend(['--reward_model_name_or_path', reward])
    return command


def run_training_recipe(config, name, directory, *, precheck_only, formal_steps=None):
    """Run the bounded gate and optionally start training on the full official split."""
    recipe = config['recipes'][name]
    benchmark = config['benchmark']
    for category in ('artifacts', 'metadata', 'reports', 'logs', 'tmp'):
        (directory / category).mkdir()
    config['task'] = {'name': recipe['name'], 'command': name}
    config['dataset']['configuration'] = recipe['dataset_configuration']
    config['dataset']['revision'] = benchmark['dataset_revision']
    config['training'] = {'epochs': 1, 'formal_step_limit': formal_steps, 'device': 'cpu', 'workers': 0}
    write_json(directory / 'metadata/config.json', config)
    manifest = {
        'run_id': str(uuid4()), 'subname': directory.name, 'task': recipe['name'],
        'effective_config': 'metadata/config.json', 'status': 'running', 'outputs': {},
        'formal_started': False, 'diagnostics': [],
    }
    manifest_path = directory / 'metadata/manifest.json'
    write_json(manifest_path, manifest)
    started = perf_counter()
    try:
        command = recipe_command(name, config, recipe)
        rows_per_step = recipe['batch_size'] // recipe.get('completions_per_prompt', 1)
        target = min(benchmark['sample_target'], benchmark['training_rows'])
        steps = math.ceil(target / rows_per_step)
        with TemporaryDirectory(dir=directory / 'tmp', prefix='gate_') as temporary:
            report = check_training(
                command, Path(temporary), directory / 'logs/precheck.log', steps=steps,
                train_rows=min(steps * rows_per_step, benchmark['training_rows']),
                validation_rows=benchmark['validation_rows'], timeout=benchmark['seconds'] - (perf_counter() - started),
            )
        manifest['precheck_seconds'] = perf_counter() - started
        report['total_seconds'] = manifest['precheck_seconds']
        write_json(directory / 'reports/precheck.json', report)
        manifest['outputs']['precheck'] = 'reports/precheck.json'
        if not precheck_only:
            manifest['formal_started'] = True
            write_json(manifest_path, manifest)
            with TemporaryDirectory(dir=directory / 'tmp', prefix='formal_') as temporary:
                checkpoint = Path(temporary)
                formal = [
                    *command, '--output_dir', str(checkpoint), '--num_train_epochs', '1',
                    '--eval_strategy', 'epoch', '--save_strategy', 'no',
                ]
                if formal_steps is not None:
                    formal.extend(['--max_steps', str(formal_steps)])
                timeout = benchmark['seconds'] - (perf_counter() - started) if formal_steps else None
                elapsed = execute(formal, directory / 'logs/training.log', timeout)
                readback = readable_model(checkpoint)
                write_json(directory / 'reports/training.json', {'seconds': elapsed, 'command': formal, 'model': readback})
                manifest['outputs']['training'] = 'reports/training.json'
                shutil.make_archive(str(directory / 'artifacts/checkpoint'), 'zip', checkpoint)
            manifest['outputs']['checkpoint'] = 'artifacts/checkpoint.zip'
        manifest['status'] = 'succeeded'
    except KeyboardInterrupt:
        manifest['status'] = 'interrupted'
        raise
    except Exception as error:
        stage = 'formal_training' if manifest['formal_started'] else 'automatic_precheck'
        manifest['diagnostics'].append({'stage': stage, 'message': str(error)})
        manifest['status'] = 'failed'
        raise
    finally:
        write_json(manifest_path, manifest)
    return manifest
