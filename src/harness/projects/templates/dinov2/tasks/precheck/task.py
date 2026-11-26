"""Check a DINOv2 configuration and a small image-to-feature invocation.

The Submitit launchers use the configuration check before submitting jobs.
The standalone precheck exercises the image decoder, transform and Hub backbone.
"""

from dinov2.configs import load_user_config


def require_configuration(reference):
    return load_user_config(reference)


def check_backbone(reference, image_path=None):
    import torch
    from PIL import Image

    from dinov2.configs import dinov2_default_config
    from dinov2.data.datasets.decoders import ImageDataDecoder
    from dinov2.data.transforms import make_classification_eval_transform
    from dinov2.hub.backbones import dinov2_vits14
    from omegaconf import OmegaConf

    config = OmegaConf.merge(dinov2_default_config, require_configuration(reference))
    if image_path:
        image_bytes = image_path.read_bytes()
    else:
        from io import BytesIO

        buffer = BytesIO()
        Image.new("RGB", (32, 32), color=(17, 127, 240)).save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
    image = ImageDataDecoder(image_bytes).decode()
    transform = make_classification_eval_transform(resize_size=32, crop_size=28)
    sample = transform(image).unsqueeze(0)
    with torch.inference_mode():
        features = dinov2_vits14(pretrained=False).eval()(sample)
    if features.shape != (1, 384) or not torch.isfinite(features).all():
        raise RuntimeError("ViT-S/14 did not produce one finite 384-dimensional embedding.")
    return {
        "configuration": reference,
        "configured_student": config.student.arch,
        "precheck_backbone": "dinov2_vits14",
        "pretrained": False,
        "sample": str(image_path) if image_path else "generated RGB image",
        "input_shape": list(sample.shape),
        "embedding_shape": list(features.shape),
    }
