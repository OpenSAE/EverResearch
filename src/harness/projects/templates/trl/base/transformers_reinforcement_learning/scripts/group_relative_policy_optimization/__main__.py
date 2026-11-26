from trl.scripts.grpo import main, make_parser


if __name__ == "__main__":
    parser = make_parser()
    script_args, training_args, model_args, dataset_args = parser.parse_args_and_config(fail_with_unknown_args=False)
    main(script_args, training_args, model_args, dataset_args)
