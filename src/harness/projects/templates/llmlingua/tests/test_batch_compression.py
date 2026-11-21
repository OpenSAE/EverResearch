"""Check the project CLI and legacy output contract with local prompts."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from llmlingua.__main__ import main
from llmlingua.datasets.token_classification import TokenClfDataset
from llmlingua.runtime import compression
from llmlingua.text_helpers import get_pure_token, is_begin_of_new_word


@pytest.fixture
def samples(tmp_path):
    path = tmp_path / "prompts.json"
    path.write_text(
        json.dumps(
            [
                {"idx": 2, "prompt_list": ["first", "second"], "answer": "reference"},
                {"idx": 3, "prompt_list": ["third"]},
                {"idx": 4, "prompt_list": None},
            ]
        ),
        encoding="utf-8",
    )
    return path


def managed_args(samples, root):
    return [
        "compress",
        "--dataset",
        "meetingbank",
        "--load_origin_from",
        str(samples),
        "--load_key",
        "prompt_list",
        "--experiment-root",
        str(root),
    ]


def test_inspect_and_read_batch_results(samples, tmp_path, capsys, monkeypatch):
    calls = []

    def compress(prompt, **options):
        calls.append((prompt, options))
        return {"compressed_prompt": prompt[0], "compressed_prompt_list": prompt[:1]}

    monkeypatch.setattr(
        compression,
        "build_compressor",
        lambda config: SimpleNamespace(compress_prompt_llmlingua2=compress),
    )
    root = tmp_path / "experiment"
    args = managed_args(samples, root)
    main([*args, "--model_revision", "checkpoint-commit", "--show-config"])
    preview = json.loads(capsys.readouterr().out)
    assert preview["compression"]["rate"] == 0.5
    assert preview["input"] == str(samples)
    assert preview["model_revision"] == "checkpoint-commit"
    assert not root.exists()

    main(
        [*args, "--limit", "1", "--compression_rate", "0.33", "--force_tokens", r"?,\n"]
    )
    run = Path(capsys.readouterr().out.strip())
    assert run.parent == root.joinpath(
        "meeting_bank",
        "llmlingua_2_xlm_roberta_large_meetingbank",
        "compression",
        "prompt_compression",
        "executions",
    )
    assert json.loads((run / "reports" / "precheck.json").read_text()) == {
        "sample_id": "2",
        "samples_checked": 1,
    }
    assert json.loads((run / "metadata" / "manifest.json").read_text())["status"] == "succeeded"
    main(["show", str(run)])
    record = json.loads(capsys.readouterr().out)
    assert record["manifest"]["status"] == "completed"
    assert record["manifest"]["formal_started"]
    assert record["manifest"]["outputs"]["precheck"] == "reports/precheck.json"
    assert record["manifest"]["sample_count"] == 1
    assert record["config"]["compression"]["rate"] == 0.33
    assert record["artifact"] == {
        "2": {
            "idx": 2,
            "prompt_list": ["first", "second"],
            "answer": "reference",
            "compressed_prompt": "first",
            "compressed_prompt_list": ["first"],
        },
    }
    assert calls == [
        (["first", "second"], record["config"]["compression"]),
    ]

    main([*args, "--limit", "1"])
    repeated = Path(capsys.readouterr().out.strip())
    assert repeated != run
    assert repeated.parent == run.parent

    main([*args, "--precheck"])
    checked_run = Path(capsys.readouterr().out.strip())
    assert checked_run.parent.parent.name == "compression_precheck"
    checked = compression.read_run(checked_run)
    assert checked["config"]["precheck_only"]
    assert not checked["manifest"]["formal_started"]
    assert checked["manifest"]["sample_count"] == 1

    main(
        [
            *args,
            "--limit",
            "1",
            "--model_name",
            "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        ]
    )
    bert_run = Path(capsys.readouterr().out.strip())
    assert bert_run.parent == root.joinpath(
        "meeting_bank",
        "llmlingua_2_bert_base_multilingual_cased_meetingbank",
        "compression",
        "prompt_compression",
        "executions",
    )
    main(["show", str(bert_run)])
    assert json.loads(capsys.readouterr().out)["manifest"]["status"] == "completed"

    historical = root.joinpath(
        "meetingbank",
        "microsoft",
        "llmlingua_2_xlm_roberta_large_meetingbank",
        "compression",
        "prompt_compression",
        run.name,
    )
    historical.parent.mkdir(parents=True)
    run.rename(historical)
    main(["show", str(historical)])
    assert json.loads(capsys.readouterr().out) == record


@pytest.mark.parametrize("name", ["1", "2026_11_20", "run", "folder/name", "../out"])
def test_reject_uninformative_or_nested_run_name(samples, tmp_path, name):
    root = tmp_path / "experiment"
    with pytest.raises(SystemExit, match="2"):
        main([*managed_args(samples, root), "--name", name])
    assert not root.exists()


def test_failed_run_records_status(samples, tmp_path, monkeypatch):
    def missing_model(config):
        raise RuntimeError("unavailable checkpoint")

    monkeypatch.setattr(compression, "build_compressor", missing_model)
    root = tmp_path / "experiment"
    with pytest.raises(RuntimeError, match="unavailable checkpoint"):
        main(managed_args(samples, root))
    [manifest] = root.rglob("manifest.json")
    record = compression.read_run(manifest.parent.parent)
    assert record["manifest"]["status"] == "failed"
    assert record["manifest"]["error"] == "unavailable checkpoint"
    assert not record["manifest"]["formal_started"]
    assert record["manifest"]["diagnostics"] == [
        {"stage": "automatic_precheck", "message": "unavailable checkpoint"}
    ]
    assert "artifact" not in record


def test_continue_legacy_output(samples, tmp_path, monkeypatch):
    output = tmp_path / "compressed.json"
    previous = {"idx": 2, "compressed_prompt": "saved earlier"}
    output.write_text(json.dumps({"2": previous}), encoding="utf-8")
    prompts = []

    def compress(prompt, **options):
        prompts.append(prompt)
        assert not options["use_token_level_filter"]
        return {"compressed_prompt": prompt[0], "compressed_prompt_list": prompt}

    monkeypatch.setattr(
        compression,
        "build_compressor",
        lambda config: SimpleNamespace(compress_prompt_llmlingua2=compress),
    )
    compression.legacy_main(
        [
            "--load_origin_from",
            str(samples),
            "--load_key",
            "prompt_list",
            "--no-use_token_level_filter",
            "--save_path",
            str(output),
        ]
    )
    assert prompts == [["third"]]
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "2": previous,
        "3": {
            "idx": 3,
            "prompt_list": ["third"],
            "compressed_prompt": "third",
            "compressed_prompt_list": ["third"],
        },
    }


def test_securitylingua_input_uses_xlm_roberta_tokens():
    class Tokenizer:
        def tokenize(self, text):
            return [text]

        def convert_tokens_to_ids(self, tokens):
            vocabulary = {"<s>": 0, "<pad>": 1, "</s>": 2, "text": 3}
            return [vocabulary[token] for token in tokens]

    dataset = TokenClfDataset(
        ["text"], 5, Tokenizer(), "SecurityLingua/securitylingua-xlm-s2s"
    )
    assert dataset[0]["ids"].tolist() == [0, 3, 2, 1, 1]
    assert dataset[0]["mask"].tolist() == [1, 1, 1, 0, 0]


def test_local_bert_checkpoint_uses_tokenizer_word_boundaries(tmp_path):
    tokenizer = SimpleNamespace(cls_token="[CLS]", sep_token="[SEP]")
    checkpoint = str(tmp_path / "custom_checkpoint")
    assert not is_begin_of_new_word("##ing", checkpoint, [], {}, tokenizer)
    assert get_pure_token("##ing", checkpoint, tokenizer) == "ing"


def test_model_loader_keeps_caller_options_and_padding(monkeypatch):
    import torch

    from llmlingua import PromptCompressor
    from llmlingua.models import transformers

    config = SimpleNamespace(
        pad_token_id=0,
        architectures=["XLMRobertaForTokenClassification"],
        max_position_embeddings=512,
    )
    tokenizer = SimpleNamespace(eos_token_id=2)
    model = object()
    kwargs_seen = []

    def load_model(name, **options):
        kwargs_seen.append((name, options))
        return model

    monkeypatch.setattr(
        transformers.AutoConfig, "from_pretrained", lambda *a, **k: config
    )
    monkeypatch.setattr(
        transformers.AutoTokenizer, "from_pretrained", lambda *a, **k: tokenizer
    )
    monkeypatch.setattr(
        transformers.AutoModelForTokenClassification, "from_pretrained", load_model
    )
    options = {"torch_dtype": torch.bfloat16, "revision": "pinned"}
    compressor = PromptCompressor.__new__(PromptCompressor)
    compressor.load_model("classifier", "cpu", options)
    assert options == {"torch_dtype": torch.bfloat16, "revision": "pinned"}
    assert tokenizer.pad_token_id == 0
    assert compressor.model is model
    assert compressor.device == "cpu"
    assert kwargs_seen == [
        (
            "classifier",
            {
                **options,
                "device_map": "cpu",
                "config": config,
                "ignore_mismatched_sizes": True,
                "trust_remote_code": True,
            },
        )
    ]
