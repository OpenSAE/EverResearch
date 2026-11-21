"""Apply a conversation template and generate an answer for one RGB image."""


def generate_answer(image, tokenizer, model, image_processor, config):
    import torch
    from transformers import GenerationConfig
    from llava.constants import (
        DEFAULT_IMAGE_TOKEN,
        DEFAULT_IM_END_TOKEN,
        DEFAULT_IM_START_TOKEN,
        IMAGE_TOKEN_INDEX,
    )
    from llava.conversation import conv_templates
    from llava.mm_utils import process_images, tokenizer_image_token

    image_token = DEFAULT_IMAGE_TOKEN
    if getattr(model.config, "mm_use_im_start_end", False):
        image_token = DEFAULT_IM_START_TOKEN + image_token + DEFAULT_IM_END_TOKEN

    conversation = conv_templates[config["conv_mode"]].copy()
    conversation.append_message(conversation.roles[0], f'{image_token}\n{config["prompt"]}')
    conversation.append_message(conversation.roles[1], None)
    prompt = conversation.get_prompt()

    input_ids = tokenizer_image_token(
        prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt"
    ).unsqueeze(0).to(model.device)
    image_tensor = process_images([image], image_processor, model.config)[0]
    image_tensor = image_tensor.unsqueeze(0).to(device=model.device, dtype=model.dtype)

    # Use the model defaults plus CLI options without moving or editing any
    # generation_config.json in the checkpoint.
    generation_config = GenerationConfig.from_model_config(model.config)
    generation_config.pad_token_id = tokenizer.pad_token_id
    do_sample = config["temperature"] > 0
    sampling = {"temperature": config["temperature"], "top_p": config["top_p"]} if do_sample else {}

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor,
            image_sizes=[image.size],
            generation_config=generation_config,
            do_sample=do_sample,
            num_beams=config["num_beams"],
            max_new_tokens=config["max_new_tokens"],
            use_cache=True,
            **sampling,
        )

    return tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
