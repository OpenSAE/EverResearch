"""Choose the CogVideoX model, scheduler, resolution and inference memory settings."""

import logging


RESOLUTION_MAP = {
    # cogvideox1.5-*
    "cogvideox1.5-5b-i2v": (768, 1360),
    "cogvideox1.5-5b": (768, 1360),
    # cogvideox-*
    "cogvideox-5b-i2v": (480, 720),
    "cogvideox-5b": (480, 720),
    "cogvideox-2b": (480, 720),
}


def resolve_resolution(model_path, generate_type, width, height, *, log=True):
    model_name = model_path.rstrip("/").split("/")[-1].lower()
    try:
        desired_resolution = RESOLUTION_MAP[model_name]
    except KeyError:
        raise ValueError(f"Unknown CogVideoX model basename: {model_name}") from None
    if width is None or height is None:
        height, width = desired_resolution
        if log:
            logging.info(
                f"Using default resolution {desired_resolution} for {model_name}"
            )
    elif (height, width) != desired_resolution:
        if generate_type == "i2v":
            # For i2v models, use user-defined width and height
            if log:
                logging.warning(
                    f"The width({width}) and height({height}) are not recommended for {model_name}. The best resolution is {desired_resolution}."
                )
        else:
            # Otherwise, use the recommended width and height
            if log:
                logging.warning(
                    f"{model_name} uses the default resolution {desired_resolution}."
                )
            height, width = desired_resolution
    return height, width


def load_pipeline(model_path, generate_type, dtype, lora_path):
    """Load the original Diffusers pipeline for the chosen input type."""
    from diffusers import (
        CogVideoXDPMScheduler,
        CogVideoXImageToVideoPipeline,
        CogVideoXPipeline,
        CogVideoXVideoToVideoPipeline,
    )

    if generate_type == "i2v":
        pipe = CogVideoXImageToVideoPipeline.from_pretrained(model_path, torch_dtype=dtype)
    elif generate_type == "t2v":
        pipe = CogVideoXPipeline.from_pretrained(model_path, torch_dtype=dtype)
    else:
        pipe = CogVideoXVideoToVideoPipeline.from_pretrained(model_path, torch_dtype=dtype)

    # If you're using with lora, add this code
    if lora_path:
        pipe.load_lora_weights(
            lora_path, weight_name="pytorch_lora_weights.safetensors", adapter_name="test_1"
        )
        pipe.fuse_lora(components=["transformer"], lora_scale=1.0)

    # 2. Set Scheduler.
    # Can be changed to `CogVideoXDPMScheduler` or `CogVideoXDDIMScheduler`.
    # We recommend using `CogVideoXDDIMScheduler` for CogVideoX-2B.
    # using `CogVideoXDPMScheduler` for CogVideoX-5B / CogVideoX-5B-I2V.

    # pipe.scheduler = CogVideoXDDIMScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    pipe.scheduler = CogVideoXDPMScheduler.from_config(
        pipe.scheduler.config, timestep_spacing="trailing"
    )

    # 3. Enable CPU offload for the model.
    # turn off if you have multiple GPUs or enough GPU memory(such as H100) and it will cost less time in inference
    # and enable to("cuda")
    # pipe.to("cuda")

    # pipe.enable_model_cpu_offload()
    pipe.enable_sequential_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()

    return pipe
