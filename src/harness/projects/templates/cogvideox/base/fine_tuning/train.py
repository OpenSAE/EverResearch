"""Parse the Diffusers fine-tuning options and dispatch to the registered trainer."""

from finetune.options import Args


def main():
    args = Args.parse_args()
    from finetune.models.registry import get_model_cls

    trainer_cls = get_model_cls(args.model_name, args.training_type)
    trainer = trainer_cls(args)
    trainer.fit()


if __name__ == "__main__":
    main()
