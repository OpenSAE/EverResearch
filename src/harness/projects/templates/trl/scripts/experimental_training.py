"""Run bounded checks for public Python trainers using cached TRL fixtures.

Use this script to check cached inputs or run a full Zen epoch through a tested
experimental trainer. Each operation uses its public trainer API.
"""

import argparse
import importlib
import json
import math
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

started = perf_counter()


REPOSITORY = 'trl-internal-testing/zen'
REVISION = '47aee340f33dd6161e2baa618240b8514666c822'
MODEL = 'trl-internal-testing/tiny-Qwen2ForCausalLM-2.5'
MODEL_REVISION = 'edca82771e1fad8f0b7ce110ffe770c682043fec'
REWARD = 'trl-internal-testing/tiny-Qwen2ForSequenceClassification-2.5'
REWARD_REVISION = '58b5b1655194e908b2af57189fccd4254b894f20'


CASES = {
    'a2po': ('a2po', 'A2PO', 'standard_prompt_only'),
    'cpo': ('cpo', 'CPO', 'standard_preference'),
    'orpo': ('orpo', 'ORPO', 'standard_preference'),
    'gkd': ('gkd', 'GKD', 'conversational_language_modeling'),
    'gmpo': ('gmpo', 'GMPO', 'standard_prompt_only'),
    'gold': ('gold', 'GOLD', 'standard_prompt_completion'),
    'iwopd': ('iw_opd', 'IWOPD', 'conversational_language_modeling'),
    'online_dpo': ('online_dpo', 'OnlineDPO', 'standard_prompt_only'),
    'sdpo': ('sdpo', 'SDPO', 'standard_prompt_only'),
    'sdft': ('sdft', 'SDFT', 'standard_prompt_completion'),
    'bema': ('bema_for_ref_model', 'DPO', 'standard_preference'),
}


def parity(completions, **kwargs):
    return [float(len(completion) % 2) for completion in completions]


def run(task, output, *, phase_started, full=False):
    from datasets import load_dataset
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from tasks.precheck.training import readable_model

    module_name, prefix, data_config = CASES[task]
    module = importlib.import_module(f'trl.experimental.{module_name}')
    trainer_type = getattr(module, prefix + 'Trainer')
    if task == 'bema':
        from trl import DPOConfig as config_type
    else:
        config_type = getattr(module, prefix + 'Config')
    dataset = load_dataset(REPOSITORY, name=data_config, revision=REVISION)
    count = len(dataset['train']) if full else min(10, len(dataset['train']))
    model = snapshot_download(MODEL, revision=MODEL_REVISION, local_files_only=True)
    args = {'max_length': 64}
    setup = {}
    rows_per_step = 1
    batch = 1
    if task in {'gkd', 'gold', 'iwopd'}:
        setup['teacher_model'] = AutoModelForCausalLM.from_pretrained(model)
        setup['processing_class'] = AutoTokenizer.from_pretrained(model)
        args['max_new_tokens' if task == 'gkd' else 'max_completion_length'] = 8
    if task == 'sdft':
        dataset = dataset.map(lambda row: {'privileged_context': row['completion']})
        args = {'max_completion_length': 8, 'max_prompt_length': 56, 'num_generations': 1}
    if task in {'gmpo', 'sdpo'}:
        args = {'max_completion_length': 8, 'num_generations': 2}
        batch = 2
        setup['reward_funcs'] = snapshot_download(REWARD, revision=REWARD_REVISION, local_files_only=True)
    if task == 'online_dpo':
        args = {'max_new_tokens': 8}
        setup['reward_funcs'] = snapshot_download(REWARD, revision=REWARD_REVISION, local_files_only=True)
    if task == 'a2po':
        args = {'max_completion_length': 8, 'num_value_samples': 2, 'filter_all_incorrect': False}
        setup['reward_funcs'] = parity
        batch = rows_per_step = 2
    if task == 'bema':
        setup['callbacks'] = [module.BEMACallback(update_ref_model=True)]
    if task == 'sdpo':
        args.update(distillation_mode='topk_logits', distillation_topk=5, distillation_is_clip=None)
    with TemporaryDirectory(dir=output.parent, prefix='weights_') as directory:
        cfg = config_type(
            output_dir=directory, use_cpu=True, bf16=False, num_train_epochs=1,
            per_device_train_batch_size=batch, per_device_eval_batch_size=batch, gradient_accumulation_steps=1,
            max_steps=math.ceil(count / rows_per_step), save_strategy='no', report_to='none', **args,
        )
        trainer = trainer_type(
            model=model, args=cfg, train_dataset=dataset['train'].select(range(count)), eval_dataset=dataset['test'], **setup
        )
        init = perf_counter()
        result = trainer.train()
        trained = perf_counter()
        evaluation = trainer.evaluate()
        checked = perf_counter()
        trainer.save_model(directory)
        tensor = readable_model(Path(directory))
        if full:
            archive_base = output.with_name(output.stem + '_checkpoint')
            tensor['archive'] = shutil.make_archive(str(archive_base), 'zip', directory)
    if not math.isfinite(result.training_loss):
        raise ValueError('The experimental trainer reported nonfinite loss.')
    record = {
        'model': MODEL, 'model_revision': MODEL_REVISION, 'dataset': data_config,
        'train_rows': count, 'full_train_rows': len(dataset['train']), 'validation_rows': len(dataset['test']),
        'batch_size': batch, 'startup_seconds': init - phase_started, 'train_seconds': trained - init,
        'validation_seconds': checked - trained, 'seconds': perf_counter() - phase_started,
        'steps': result.global_step, 'metrics': result.metrics, 'validation': evaluation, 'checkpoint_readback': tensor,
    }
    output.write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('precheck', 'run'))
    parser.add_argument('task', choices=sorted(CASES))
    parser.add_argument('--report', type=Path, required=True)
    options = parser.parse_args()
    options.report.parent.mkdir(parents=True, exist_ok=True)
    gate_log = options.report
    if options.operation == 'run':
        gate_log = options.report.with_name(options.report.stem + '_precheck.json')
    if options.report.exists() or gate_log.exists():
        parser.error('Choose a fresh report path.')
    run(options.task, gate_log, phase_started=started)
    if options.operation == 'run':
        run(options.task, options.report, phase_started=perf_counter(), full=True)
    print(options.report)


if __name__ == '__main__':
    main()
