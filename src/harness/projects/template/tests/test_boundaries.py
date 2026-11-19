"""目的：验证配置隔离、数据划分独立性和性能候选拒绝后仍能读取基线。

适用范围：本地目录和生成的小样本，无需网络或 GPU。
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
            raise RuntimeError("样本读取无法在子进程运行")
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
            with self.assertRaisesRegex(ValueError, "引用了同一文件"):
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
        self.assertIn("无法在子进程运行", report["candidate"]["error"]["message"])
        self.assertEqual(len(report["baseline"]["runs"]), 2)
        self.assertEqual(report["recommended_workers"], 0)
