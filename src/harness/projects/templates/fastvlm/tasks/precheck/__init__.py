"""Check the inputs to image inference, supervised training, serving and export."""
from pathlib import Path
from tempfile import TemporaryDirectory


def check_checkpoint_paths(*sources):
    for source in sources:
        if source is None:
            continue
        path = Path(source).expanduser()
        if (path.is_absolute() or str(source).startswith(("./", "../", "~/"))) and not path.is_dir():
            raise ValueError(f"Checkpoint directory does not exist: {path}")


def check_training_paths(data_paths):
    if not data_paths:
        raise ValueError("Training requires at least one --data_path JSON file.")
    for path in data_paths:
        if not Path(path).is_file():
            raise ValueError(f"Training data file does not exist: {path}")


def check_training_sample(data_module, model):
    from llava.constants import IGNORE_INDEX

    dataset = data_module["train_dataset"]
    if not len(dataset):
        raise ValueError("Training data must contain at least one conversation.")

    row = dataset.list_data_dict[0]
    if "image" in row and not dataset.data_args.is_multimodal:
        raise ValueError("The first training sample contains an image. Select a vision tower.")
    sample = dataset[0]
    batch = data_module["data_collator"]([sample])
    if batch["input_ids"].shape[-1] == 0:
        raise ValueError("The first training sample has no input tokens.")
    if not (batch["labels"][..., 1:] != IGNORE_INDEX).any():
        raise ValueError("The first training sample has no target tokens after preprocessing.")
    if "images" in batch and model.get_vision_tower() is None:
        raise ValueError("The first training sample requires a model with a vision tower.")


def check_vision_request(prompt, images):
    from llava.constants import DEFAULT_IMAGE_TOKEN
    from llava.mm_utils import load_image_from_base64

    if len(images) != prompt.count(DEFAULT_IMAGE_TOKEN):
        raise ValueError("Number of images does not match number of <image> tokens in prompt")
    decoded = [load_image_from_base64(image) for image in images]
    for image in decoded:
        image.load()
    return decoded


def check_export_checkpoint(model_path, model_base):
    check_checkpoint_paths(model_path, model_base)
    for filename in ("config.json", "tokenizer_config.json"):
        path = Path(model_path).expanduser() / filename
        if not path.is_file():
            raise ValueError(f"Apple Silicon export requires a local checkpoint with {filename}: {path}")
    import torch

    if not torch.backends.mps.is_available():
        raise ValueError("Apple Silicon export requires an available PyTorch MPS device.")


def prepare_inference(config):
    from ...datasets.user_image import read_image
    from ...models.fast_vision import load_checkpoint
    from ...records import read_result, save_result
    from ..image_prompt import generate_answer

    check_checkpoint_paths(config["model_path"], config["model_base"])

    image, input_info = read_image(Path(config["image_file"]), config["dataset"])
    from llava.conversation import conv_templates

    if config["conv_mode"] not in conv_templates:
        options = ", ".join(sorted(conv_templates))
        raise ValueError(f'Unknown conversation mode {config["conv_mode"]!r}. Choose from {options}.')

    resources = load_checkpoint(config["model_path"], config["model_base"], config["device"])
    tokenizer, model, processor, device = resources
    probe = {**config, "device": device, "temperature": 0, "num_beams": 1, "max_new_tokens": 1}
    answer = generate_answer(image, tokenizer, model, processor, probe)
    with TemporaryDirectory(prefix="fastvlm-precheck-") as temporary:
        result = save_result(Path(temporary), probe, input_info, answer)
        relative = result.relative_to(temporary).as_posix()
        if read_result(result) != {"input": input_info, "answer": answer}:
            raise ValueError("The generated precheck prediction could not be read back.")
    report = {"samples_checked": 1, "new_token_limit": 1, "example_manifest": relative}
    return image, input_info, resources, report
