"""Train an LLM using GRPO over Reasoning Gym procedural dataset(s)."""

from dataclasses import replace

import hydra
from omegaconf import OmegaConf
from reasoning_gym.training_rows import ReasoningGymDataset, make_dataset

import reasoning_gym
import reasoning_gym.utils
from reasoning_gym.coaching.curriculum_config import CurriculumAttributeConfig, CurriculumExperimentConfig
from reasoning_gym.coaching.experiment import CurriculumExperiment
from reasoning_gym.composite import CompositeDataset, DatasetSpec
from reasoning_gym.training_checkpoint.tokenizer import load_training_tokenizer


def prepare_datasets(config, tokenizer) -> tuple[ReasoningGymDataset, ReasoningGymDataset]:
    """Prepare training and validation datasets."""
    dataset_size = config.reasoning_gym.dataset_size
    developer_prompt_setting = config.reasoning_gym.developer_prompt
    developer_prompt = reasoning_gym.utils.SYSTEM_PROMPTS[developer_prompt_setting]

    if config.curriculum.enabled:
        curricula = config.curriculum.curricula
        curriculum_config = CurriculumExperimentConfig(
            curricula={
                curriculum_name: CurriculumAttributeConfig(**curriculum_config)
                for curriculum_name, curriculum_config in curricula.items()
            }
        )

        train_data_source = CurriculumExperiment(
            name=config.trainer.experiment_name, config=curriculum_config, size=dataset_size, seed=1
        )
        val_data_source = CompositeDataset(config=replace(train_data_source.composite.config, seed=2))
    else:
        dataset_specs = [
            DatasetSpec(
                name=name,
                weight=ds.weight,
                config=OmegaConf.to_container(ds.config, resolve=True) if "config" in ds else {},
            )
            for name, ds in config.reasoning_gym.datasets.items()
        ]
        train_data_source = reasoning_gym.create_dataset("composite", seed=1, size=dataset_size, datasets=dataset_specs)
        val_data_source = reasoning_gym.create_dataset("composite", seed=2, size=dataset_size, datasets=dataset_specs)
    train_dataset = make_dataset(
        tokenizer, train_data_source, developer_prompt, max_prompt_length=config.data.max_prompt_length
    )
    val_dataset = make_dataset(
        tokenizer, val_data_source, developer_prompt, max_prompt_length=config.data.max_prompt_length
    )
    return train_dataset, val_dataset


def main_task(config):
    from pprint import pprint

    pprint(OmegaConf.to_container(config, resolve=True))  # resolve=True will eval symbol values
    OmegaConf.resolve(config)

    _, tokenizer = load_training_tokenizer(config.actor_rollout_ref.model.path)

    train_dataset, val_dataset = prepare_datasets(config, tokenizer)
    for dataset in (train_dataset, val_dataset):
        row = dataset[0]
        if not row["attention_mask"].any():
            raise ValueError("The training precheck produced an empty tokenized prompt")
    if config.get("precheck", False):
        print("Training precheck tokenized one training row and one validation row.")
        return

    import ray

    from .trainers import RayGRPOTrainer

    # define worker classes
    if config.actor_rollout_ref.actor.strategy == "fsdp":
        assert config.actor_rollout_ref.actor.strategy == config.critic.strategy
        from verl.single_controller.ray import RayWorkerGroup
        from verl.workers.fsdp_workers import ActorRolloutRefWorker, CriticWorker

        ray_worker_group_cls = RayWorkerGroup
    elif config.actor_rollout_ref.actor.strategy == "megatron":
        assert config.actor_rollout_ref.actor.strategy == config.critic.strategy
        from verl.single_controller.ray.megatron import NVMegatronRayWorkerGroup
        from verl.workers.megatron_workers import ActorRolloutRefWorker, CriticWorker

        ray_worker_group_cls = NVMegatronRayWorkerGroup
    else:
        raise NotImplementedError

    from verl.trainer.ppo.ray_trainer import ResourcePoolManager, Role

    role_worker_mapping = {
        Role.ActorRollout: ray.remote(ActorRolloutRefWorker),
        Role.Critic: ray.remote(CriticWorker),
        Role.RefPolicy: ray.remote(ActorRolloutRefWorker),
    }

    global_pool_id = "global_pool"
    resource_pool_spec = {
        global_pool_id: [config.trainer.n_gpus_per_node] * config.trainer.nnodes,
    }
    mapping = {
        Role.ActorRollout: global_pool_id,
        Role.Critic: global_pool_id,
        Role.RefPolicy: global_pool_id,
    }

    resource_pool_manager = ResourcePoolManager(resource_pool_spec=resource_pool_spec, mapping=mapping)

    trainer = RayGRPOTrainer(
        config=config,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        role_worker_mapping=role_worker_mapping,
        resource_pool_manager=resource_pool_manager,
        ray_worker_group_cls=ray_worker_group_cls,
        max_output_length=config.data.max_response_length,
    )
    trainer.init_workers()
    trainer.fit()


@hydra.main(version_base=None)
def main(config):
    if config.get("precheck", False):
        main_task(config)
        return

    import ray

    if not ray.is_initialized():
        # this is for local ray cluster
        ray.init(runtime_env={"env_vars": {"TOKENIZERS_PARALLELISM": "true", "NCCL_DEBUG": "WARN"}})
    ray.get(ray.remote(main_task).remote(config))


if __name__ == "__main__":
    main()
