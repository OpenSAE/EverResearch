"""Purpose: Validation of configuration isolation, data disaggregation independence and ability to read the baseline after rejection.

Scope of application: Local directories and small samples generated without the need for a network or GPU.
"""

import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset, get_worker_info

from cub_template.contracts import PerformanceWorkload
from cub_template.datasets.cub200 import load as load_cub
from cub_template.runtime.config import load
from cub_template.tasks.precheck.performance import compare

CONF = Path(__file__).resolve().parents[1] / "conf"


class SerialDataset(Dataset):
    def __len__(self):
        return 2

    def __getitem__(self, index):
        if get_worker_info() is not None:
            raise RuntimeError("Sample reading cannot run in subprocess")
        return torch.tensor([index, index + 1], dtype=torch.float32)


class BoundariesTest(unittest.TestCase):
    def test_a_later_configuration_cannot_borrow_an_earlier_preset(self):
        with tempfile.TemporaryDirectory() as temporary:
            other = Path(temporary) / "config.yaml"
            default = CONF / "config.yaml"
            other.write_text(default.read_text().replace(
                "    resnet18_mlp:\n      name: resnet18_mlp\n", ""
            ))
            self.assertEqual(load(default)["model"]["name"], "resnet18_mlp")
            with self.assertRaisesRegex(ValueError, "resnet18_mlp"):
                load(other)
            self.assertEqual(load(default)["model"]["name"], "resnet18_mlp")

    def test_a_file_cannot_enter_both_splits_even_with_different_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "images").mkdir()
            train = root / "images/train.jpg"
            Image.new("RGB", (4, 4)).save(train)
            (root / "images/test.jpg").hardlink_to(train)
            (root / "images.txt").write_text("1 train.jpg\n2 test.jpg\n")
            (root / "image_class_labels.txt").write_text("1 1\n2 1\n")
            (root / "train_test_split.txt").write_text("1 1\n2 0\n")
            with self.assertRaisesRegex(ValueError, "Quote the same document"):
                load_cub({"root": str(root), "image_size": 32}, 42)

    def test_a_failing_candidate_preserves_the_measured_baseline(self):
        target = SimpleNamespace(
            performance_workload=lambda request: PerformanceWorkload(
                2,
                "offline workers check",
                lambda workers: DataLoader(SerialDataset(), batch_size=2, num_workers=workers),
                lambda batch: batch,
            )
        )
        request = SimpleNamespace(
            target=target,
            device=torch.device("cpu"),
            candidate_workers=1,
            config={"benchmark": {"warmup": 0, "repeats": 2}, "runtime": {"workers": 0}},
        )
        report = compare(request)
        self.assertEqual(report["decision"], "candidate_failed")
        self.assertIn("Could not run in subprocess", report["candidate"]["error"]["message"])
        self.assertEqual(len(report["baseline"]["runs"]), 2)
        self.assertEqual(report["recommended_workers"], 0)
