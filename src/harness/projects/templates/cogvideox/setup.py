"""Map installable packages to their EverResearch component directories."""

from setuptools import find_namespace_packages, setup


packages = {
    "cogvideo_runtime": "base/cogvideo_runtime",
    "cogvideo_defaults": "conf",
    "cogvideo_inputs": "datasets/video_input",
    "cogvideo_generation": "models/cogvideo_generation",
    "cogvideo_tasks": "tasks/video_generation",
    "cogvideo_precheck": "tasks/precheck",
    "cogvideo_training": "tasks/video_finetuning",
    "finetune": "base/fine_tuning",
    "finetune.schemas": "base/fine_tuning/schemas",
    "finetune.utils": "base/fine_tuning/utilities",
    "finetune.datasets": "datasets/finetune_video",
    "finetune.models": "models/finetune_video",
    "sat_runtime": "base/sat_runtime",
    "cogvideo_sat_data": "datasets/sat_video",
    "cogvideo_sat_model": "models/sat_video",
    "cogvideo_sat_model.vae_modules": "models/sat_video/vae_modules",
    "cogvideo_sat_task": "tasks/sat_video",
}
for name in ("cogvideox_text", "cogvideox_image", "cogvideox1_5_text", "cogvideox1_5_image"):
    packages[f"finetune.models.{name}"] = f"models/finetune_video/{name}"

for name in find_namespace_packages("third_party/stability_ai", include=["sgm", "sgm.*"]):
    packages[name] = "third_party/stability_ai/" + name.replace(".", "/")

setup(
    packages=list(packages),
    package_dir=packages,
    package_data={"cogvideo_defaults": ["config.json"], "sgm": ["**/LICENSE"]},
)
