"""Exercise training and validation through each installed TRL trainer command.

The maintained project launcher uses this module to check an isolated bounded
run and verify the saved checkpoint before starting a full recipe.
"""

import json
import math
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from safetensors import safe_open


def execute(command, log_path, timeout):
    """Record a subprocess result and stop its launcher and workers on timeout."""
    started = perf_counter()
    environment = dict(os.environ)
    for variable in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        environment.setdefault(variable, '1')
    with log_path.open('w', encoding='utf-8') as output:
        with subprocess.Popen(
            command, stdout=output, stderr=subprocess.STDOUT, start_new_session=True, env=environment
        ) as process:
            try:
                result = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
    if result:
        message = log_path.read_text(encoding='utf-8').strip().splitlines()[-1:]
        raise RuntimeError(f'TRL exited with status {result}. {" ".join(message)} See {log_path}.')
    return perf_counter() - started


def readable_model(directory):
    """Open a real tensor from a saved model and confirm it is finite."""
    shards = sorted(directory.glob('model*.safetensors'))
    if not shards:
        raise FileNotFoundError(f'No trained model found in {directory}.')
    with safe_open(shards[0], framework='pt') as artifact:
        tensor_name = next(iter(artifact.keys()))
        tensor = artifact.get_tensor(tensor_name)
        if not tensor.isfinite().all():
            raise ValueError(f'The saved tensor {tensor_name} contains nonfinite values.')
    return {'file': shards[0].name, 'tensor': tensor_name, 'shape': list(tensor.shape)}


def check_training(command, destination, log_path, *, steps, train_rows, validation_rows, timeout):
    """Verify completed optimizer steps, validation, and checkpoint readback."""
    started = perf_counter()
    bounded = [
        *command, '--output_dir', str(destination), '--max_steps', str(steps),
        '--eval_strategy', 'steps', '--eval_steps', str(steps), '--save_strategy', 'steps',
        '--save_steps', str(steps), '--save_only_model', 'true', '--logging_steps', '1',
    ]
    elapsed = execute(bounded, log_path, timeout)
    state_path = destination / f'checkpoint-{steps}/trainer_state.json'
    state = json.loads(state_path.read_text(encoding='utf-8'))
    history = state['log_history']
    losses = [entry['loss'] for entry in history if 'loss' in entry]
    validation = next((entry for entry in reversed(history) if 'eval_runtime' in entry), None)
    if state['global_step'] != steps or len(losses) != steps or not all(math.isfinite(loss) for loss in losses):
        raise ValueError('The bounded trainer did not report the expected finite optimizer steps.')
    if validation is None:
        raise ValueError('The bounded trainer did not report validation metrics.')
    checkpoint = readable_model(destination)
    runtimes = re.findall(r"['\"]train_runtime['\"]:\s*['\"]?([\d.]+)", log_path.read_text(encoding='utf-8'))
    return {
        'samples_checked': train_rows, 'validation_samples': validation_rows, 'optimizer_steps': steps,
        'losses': losses, 'validation': validation, 'model_readback': checkpoint,
        'process_seconds': elapsed, 'precheck_seconds': perf_counter() - started,
        'train_loop_seconds': float(runtimes[-1]) if runtimes else None,
        'command': bounded,
    }


def installed_command(subcommand):
    """Find the installed command associated with this interpreter."""
    return [str(Path(sys.executable).with_name('trl')), subcommand]
