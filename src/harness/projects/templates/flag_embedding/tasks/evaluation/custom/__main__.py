from transformers import HfArgumentParser

from FlagEmbedding.evaluation.custom import (
    CustomEvalArgs, CustomEvalModelArgs,
    CustomEvalRunner
)


def main():
    parser = HfArgumentParser((
        CustomEvalArgs,
        CustomEvalModelArgs
    ))
    parser.set_defaults(eval_name="custom")

    eval_args, model_args = parser.parse_args_into_dataclasses()
    eval_args: CustomEvalArgs
    model_args: CustomEvalModelArgs

    runner = CustomEvalRunner(
        eval_args=eval_args,
        model_args=model_args
    )

    runner.run()
    if eval_args.precheck_only:
        print("Local retrieval precheck passed.")


if __name__ == "__main__":
    main()
