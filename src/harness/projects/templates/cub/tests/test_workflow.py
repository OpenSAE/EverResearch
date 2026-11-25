"""Purpose: Examination of precheck, training and result reading access assurance for downstream.

Scope of application: Offline engineering inspection, test data kept in the temporary directory.
"""

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[1]


def offline_overrides(*extra):
    return (
        "--set", "dataset=synthetic",
        "--set", "runtime.device=cpu",
        "--set", "runtime.workers=0",
        "--set", "runtime.cpu_threads=2",
        "--set", "training.batch_size=2",
        "--set", "training.epochs=1",
        "--set", "benchmark.samples=4",
        *extra,
    )


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.checkout = Path(temporary.name) / "project"
        self.checkout.mkdir()
        self.environment = {**os.environ, "PYTHONPATH": str(self.checkout / "base")}
        shutil.copy2(ROOT / "pyproject.toml", self.checkout)
        for name in ("conf", "base", "datasets", "models", "tasks"):
            shutil.copytree(
                ROOT / name, self.checkout / name, ignore=shutil.ignore_patterns("__pycache__")
            )

    def run_operation(self, operation, *, config=None, subname="offline_check", extra=()):
        if config is not None:
            extra = ("--config", str(config), *extra)
        command = [
            sys.executable,
            "-m",
            "cub_template",
            operation,
            "--subname",
            subname,
            *extra,
        ]
        result = subprocess.run(
            command, cwd=self.checkout, env=self.environment, capture_output=True, text=True, timeout=60
        )
        self.assertTrue(result.stdout.strip(), result.stderr)
        path = Path(result.stdout.splitlines()[0])
        self.assertTrue(path.is_relative_to(self.checkout / "experiment"))
        manifest = json.loads((path / "metadata/manifest.json").read_text())
        self.assertEqual(path.parent.name, manifest["subname"])
        if manifest.get("effective_config"):
            saved = OmegaConf.to_container(OmegaConf.load(path / manifest["effective_config"]))
            self.assertEqual(saved, manifest["configuration"])
        return result, path, manifest

    def test_output_root_is_not_a_command_option(self):
        outside = self.checkout.parent / "alternate"
        result = subprocess.run(
            [
                sys.executable, "-m", "cub_template", "precheck",
                "--subname", "offline_check", "--output", str(outside),
            ],
            cwd=self.checkout, env=self.environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--output", result.stderr)
        self.assertFalse(outside.exists())

    def test_experiment_name_has_at_most_three_words(self):
        for name in ("four separate descriptive words", "../outside"):
            result = subprocess.run(
                [sys.executable, "-m", "cub_template", "run", "--subname", name],
                cwd=self.checkout, env=self.environment, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("One to three.", result.stderr)
        self.assertFalse((self.checkout / "experiment").exists())

    def test_training_produces_readable_report_and_weights(self):
        result, path, manifest = self.run_operation(
            "train", extra=offline_overrides("--set", "model=resnet18_mlp_small")
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertTrue(manifest["formal_started"])
        self.assertGreater(manifest["precheck_seconds"], 0)
        self.assertIn("precheck", manifest["outputs"])
        precheck = json.loads((path / manifest["outputs"]["precheck"]).read_text())
        self.assertEqual(precheck["samples_checked"], 4)
        self.assertEqual(manifest["inputs"]["dataset"], "synthetic")
        evaluation = json.loads((path / manifest["outputs"]["evaluation"]).read_text())
        self.assertEqual(evaluation["samples"], 4)
        self.assertTrue(0 <= evaluation["top1_accuracy"] <= 1)
        self.assertTrue((path / manifest["outputs"]["model"]).is_file())
        inspected = subprocess.check_output(
            [sys.executable, "-m", "cub_template", "inspect", str(path)],
            cwd=self.checkout, env=self.environment,
            text=True,
            timeout=30,
        )
        self.assertEqual(json.loads(inspected), manifest)
        repeat, repeated_path, repeated = self.run_operation("train", config=path / "config.yaml")
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertEqual(repeated_path.parent, path.parent)
        self.assertNotEqual(repeated_path, path)
        self.assertEqual(repeated["configuration"], manifest["configuration"])

    def test_series_variant_uses_same_precheck_and_training_entries(self):
        for operation in ("precheck", "train"):
            with self.subTest(operation=operation):
                overrides = offline_overrides("--set", "model=resnet18_mlp_small")
                if operation == "precheck":
                    overrides += ("--set", "task=precheck")
                result, path, manifest = self.run_operation(
                    "run", extra=overrides
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    manifest["configuration"]["model"]["name"], "resnet18_mlp_small"
                )
                self.assertEqual(manifest["configuration"]["model"]["hidden_dim"], 16)
                self.assertEqual(
                    manifest["task"],
                    "precheck" if operation == "precheck" else "classification",
                )
                self.assertEqual(path.parents[2].name, "residual_classifier_small")
                role = "precheck" if operation == "precheck" else "evaluation"
                report = json.loads((path / manifest["outputs"][role]).read_text())
                metrics = report["evaluation_step"] if operation == "precheck" else report
                self.assertGreater(metrics["samples"], 0)

    def test_performance_precheck_reports_bottleneck_and_usable_candidate(self):
        result, path, manifest = self.run_operation(
            "benchmark",
            extra=offline_overrides("--set", "model=resnet18_mlp_small", "--candidate-workers", "1"),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((path / manifest["outputs"]["performance"]).read_text())
        baseline = report["baseline"]["median_stages_seconds"]
        self.assertEqual(report["bottleneck"]["stage"], max(baseline, key=baseline.get))
        self.assertEqual(report["baseline"]["workers"], 0)
        self.assertEqual(report["candidate"]["workers"], 1)
        self.assertTrue(report["candidate"]["output_matches"])
        expected = 1 if report["decision"] == "candidate_faster" else 0
        self.assertEqual(report["recommended_workers"], expected)

    def test_precheck_rejects_training_with_unsupported_singleton_tail(self):
        result, _, manifest = self.run_operation(
            "run", extra=offline_overrides("--set", "training.batch_size=7")
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(manifest["diagnostics"][0]["stage"], "automatic_precheck")
        self.assertFalse(manifest["formal_started"])
        self.assertIn("There’s only one picture in the last batch.", manifest["diagnostics"][0]["message"])
        self.assertNotIn("training", manifest["outputs"])

    def test_missing_cub_inputs_leave_a_blocked_manifest(self):
        result, _, manifest = self.run_operation(
            "precheck",
            extra=("--data-root", str(self.checkout / "missing_cub")),
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["result_state"], "blocked")
        self.assertEqual(manifest["diagnostics"][0]["stage"], "inputs")
        self.assertIn("next_action", manifest["diagnostics"][0])
        self.assertFalse(manifest["outputs"])
