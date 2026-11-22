"""Exercise supported command behavior with local input and stand-in model components."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from PIL import Image

from fastvlm import cli, runtime
from fastvlm.models import fastvithd
from fastvlm.tasks import image_prompt

ROOT = Path(__file__).resolve().parent.parent
PREDICT = ROOT / "main.py"


def invoke(workdir, *arguments):
    return subprocess.run(
        [sys.executable, str(PREDICT), *arguments],
        cwd=workdir,
        capture_output=True,
        text=True,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )


def test_preview_uses_packaged_defaults_and_cli_overrides_from_another_directory(tmp_path):
    result = invoke(tmp_path, "--show-config", "--top_p", "0.8", "--num_beams", "3", "--device", "cpu")
    assert result.returncode == 0, result.stderr
    config = json.loads(result.stdout)
    assert config == {
        **runtime.defaults(),
        "model_path": str(runtime.checkpoint_root() / runtime.defaults()["model_path"]),
        "top_p": 0.8,
        "num_beams": 3,
        "device": "cpu",
    }
    assert not list(tmp_path.iterdir())


def test_parameter_doc_matches_the_loaded_recipe():
    conf_path = ROOT / "conf/config.json"
    doc = (ROOT / "doc/conf.md").read_text(encoding="utf-8")
    assert "### config.json" in doc and "(../conf/config.json)" in doc
    documented = dict(re.findall(r'^\| `([^\x60]+)` \| `([^\x60]+)` \|', doc, re.MULTILINE))
    assert {key: json.loads(value) for key, value in documented.items()} == runtime.defaults()
    assert runtime.defaults() == {key: val for key, val in json.loads(conf_path.read_text()).items() if key != "catalogs"}


@pytest.mark.parametrize("subname", ["20261120", "123", "run", "run_1", "two/parts"])
def test_invalid_experiment_name_fails_before_accessing_input(tmp_path, subname):
    result = invoke(tmp_path, "--image-file", "missing.png", "--subname", subname)
    assert result.returncode == 2
    assert "--subname" in result.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ((), "--image-file is required"),
        (("--image-file", "missing.png"), "Image file does not exist"),
        (("--temperature", "nan", "--show-config"), "--temperature must be"),
        (("--dataset", "../coco", "--show-config"), "--dataset must use"),
        (("--top_p", "2", "--show-config"), "--top-p must be"),
        (("--num_beams", "0", "--show-config"), "--num-beams and --max-new-tokens"),
    ],
)
def test_invalid_invocations_are_reported_without_model_loading(tmp_path, arguments, message):
    result = invoke(tmp_path, *arguments)
    assert result.returncode == 2
    assert message in result.stderr
    assert not list(tmp_path.iterdir())


def test_wheel_requires_workspace_for_results_but_can_precheck(tmp_path, monkeypatch, capsys):
    recipe = runtime.defaults()
    monkeypatch.setattr(runtime, "defaults", lambda: recipe.copy())
    monkeypatch.setattr(runtime, "SOURCE_ROOT", None)
    monkeypatch.delenv("FASTVLM_WORKSPACE", raising=False)
    monkeypatch.chdir(tmp_path)
    photo = tmp_path / "sample.png"
    Image.new("RGB", (2, 2)).save(photo)
    arguments = ["--image-file", str(photo), "--model-path", str(tmp_path / "missing")]

    with pytest.raises(SystemExit) as rejected:
        cli.main(arguments)
    assert rejected.value.code == 2
    assert "FASTVLM_WORKSPACE" in capsys.readouterr().err

    with pytest.raises(SystemExit) as rejected_precheck:
        cli.main([*arguments, "--precheck"])
    assert rejected_precheck.value.code == 2
    assert "Checkpoint directory does not exist" in capsys.readouterr().err
    assert not (tmp_path / "experiment").exists()


def test_regular_command_archives_readable_results_and_preserves_checkpoint(tmp_path, monkeypatch, capsys):
    sandbox = tmp_path / "checkout"
    sandbox.mkdir()
    checkpoint_directory = tmp_path / "model"
    checkpoint_directory.mkdir()
    (checkpoint_directory / "generation_config.json").write_text('{"temperature": 0.65}')
    photo = tmp_path / "sample.png"
    Image.new("L", (8, 5), 64).save(photo)
    monkeypatch.setattr(runtime, "project_root", lambda: sandbox)

    conversation = ModuleType("llava.conversation")
    conversation.conv_templates = {"qwen_2": object()}
    monkeypatch.setitem(sys.modules, "llava.conversation", conversation)

    def fake_checkpoint(model_path, model_base, device):
        assert model_path == str(checkpoint_directory)
        assert model_base is None
        assert device == "auto"
        return "tokenizer", "model", "processor", "cpu"

    def fake_answer(image, tokenizer, model, processor, config):
        assert image.mode == "RGB" and image.size == (8, 5)
        assert (tokenizer, model, processor) == ("tokenizer", "model", "processor")
        assert config["prompt"] == "What shape?"
        if config["max_new_tokens"] == 1:
            assert config["num_beams"] == 1
            return "A"
        assert config["num_beams"] == 2
        return "A rectangle."

    monkeypatch.setattr(fastvithd, "load_checkpoint", fake_checkpoint)
    monkeypatch.setattr(image_prompt, "generate_answer", fake_answer)
    arguments = [
        "--model-path", str(checkpoint_directory), "--image-file", str(photo),
        "--prompt", "What shape?", "--num_beams", "2", "--subname", "inspect_shapes",
    ]
    for _ in range(2):
        cli.main(arguments)
        stdout, stderr = capsys.readouterr()
        assert stdout == "A rectangle.\n"
        assert stderr.startswith("Run manifest: ")
        manifest_path = Path(stderr.partition("Run manifest: ")[2].strip())
        manifest = json.loads(manifest_path.read_text())
        assert manifest["inputs"]["checkpoint"] == str(checkpoint_directory)
        assert manifest["environment"]["device"] == "cpu"
        assert manifest["formal_started"] is True
        precheck = json.loads((manifest_path.parents[1] / manifest["outputs"]["precheck"]).read_text())
        assert precheck["samples_checked"] == precheck["new_token_limit"] == 1
        config = json.loads((manifest_path.parents[1] / manifest["effective_config"]).read_text())
        assert config["prompt"] == "What shape?" and config["device"] == "cpu"

        readback = invoke(tmp_path, "--read-result", str(manifest_path))
        assert readback.returncode == 0, readback.stderr
        prediction = json.loads(readback.stdout)
        assert prediction["input"]["path"] == str(photo)
        assert prediction["input"]["size"] == [8, 5]
        assert prediction["input"]["sha256"] == hashlib.sha256(photo.read_bytes()).hexdigest()
        assert prediction["answer"] == "A rectangle."

    run_group = sandbox / "experiment/user_image/fast_vision/image_prompt/inspect_shapes/executions"
    assert len(list(run_group.glob("*/metadata/manifest.json"))) == 2
    assert not list(run_group.glob(".pending-*"))
    assert (checkpoint_directory / "generation_config.json").read_text() == '{"temperature": 0.65}'
    assert sorted(path.name for path in checkpoint_directory.iterdir()) == ["generation_config.json"]


@pytest.mark.parametrize(
    ("checkpoint", "variant"),
    [("llava-fastvithd_0.5b_stage3", "fast_vision_small_stage3"), ("llava-fastvithd_1.5b_stage2", "fast_vision_medium_stage2")],
)
def test_named_dataset_and_published_checkpoint_use_component_directories(tmp_path, checkpoint, variant):
    from fastvlm.datasets.user_image import read_image
    from fastvlm.records import save_result

    photo = tmp_path / "sample.png"
    Image.new("RGB", (8, 5)).save(photo)
    preview = invoke(tmp_path, "--show-config", "--dataset", "coco_val")
    assert preview.returncode == 0, preview.stderr
    config = {**json.loads(preview.stdout), "model_path": str(tmp_path / checkpoint), "device": "cpu"}
    _, input_info = read_image(photo, config["dataset"])
    manifest = save_result(tmp_path, config, input_info, "A rectangle.")

    expected = tmp_path / "experiment/coco_val" / variant / "image_prompt/describe_image/executions"
    assert manifest.parents[2] == expected
    result = invoke(tmp_path, "--read-result", str(manifest))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"input": input_info, "answer": "A rectangle."}
