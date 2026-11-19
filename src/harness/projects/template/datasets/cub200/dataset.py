"""目的：读取 CUB-200-2011 官方图像、标签和训练测试划分。

适用范围：本地已完整解压的 CUB-200-2011 数据。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from ...contracts import ClassificationInputs, validate_rgb_config as validate_config

__all__ = ["CLASSES", "REQUIRES_ROOT", "load", "validate_config"]

REQUIRES_ROOT = True
CLASSES = 200

COUNTS = {1: 5994, 0: 5794}
NORMALIZE = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))


def read_rows(path: Path):
    rows = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        key, value = line.split(maxsplit=1)
        key = int(key)
        if key in rows:
            raise ValueError(f"{path}:{number}: 图像编号重复 {key}")
        rows[key] = value
    return rows


class CubImages(Dataset):
    def __init__(self, rows, size, *, training):
        self.rows = rows
        steps = (
            [transforms.RandomResizedCrop(size), transforms.RandomHorizontalFlip()]
            if training
            else [transforms.Resize(round(size * 256 / 224)), transforms.CenterCrop(size)]
        )
        self.transform = transforms.Compose([*steps, transforms.ToTensor(), NORMALIZE])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        path, label = self.rows[index]
        with Image.open(path) as image:
            return self.transform(image.convert("RGB")), label


def load(config, _seed):
    """Return train, test, deterministic train views and input identity."""
    size = config["image_size"]
    root = Path(config["root"])
    files = [
        root / name for name in ("images.txt", "image_class_labels.txt", "train_test_split.txt")
    ]
    images, labels, splits = map(read_rows, files)
    if not images.keys() == labels.keys() == splits.keys():
        raise ValueError("官方图像、标签和划分文件的编号集合必须一致")
    image_root = (root / "images").resolve()
    rows = {0: [], 1: []}
    seen_images = {}
    for key in sorted(images):
        path = (image_root / images[key]).resolve()
        label, split = int(labels[key]), int(splits[key])
        if not path.is_relative_to(image_root):
            raise ValueError(f"编号 {key} 的图像路径超出 images 目录：{path}")
        if not path.is_file():
            raise FileNotFoundError(f"编号 {key} 的图像缺失：{path}")
        info = path.stat()
        identity = (info.st_dev, info.st_ino)
        if identity in seen_images:
            raise ValueError(f"图像记录 {seen_images[identity]} 与 {key} 引用了同一文件：{path}")
        seen_images[identity] = key
        if not 1 <= label <= 200 or split not in rows:
            raise ValueError(f"编号 {key} 的标签或划分无效")
        rows[split].append((path, label - 1))
    if {flag: len(items) for flag, items in rows.items()} != COUNTS:
        raise ValueError("CUB-200-2011 官方划分应包含 5994 张训练图和 5794 张测试图")
    if any({label for _, label in items} != set(range(200)) for items in rows.values()):
        raise ValueError("训练集和测试集均应覆盖 200 类")
    return ClassificationInputs(
        CubImages(rows[1], size, training=True),
        CubImages(rows[0], size, training=False),
        CubImages(rows[1], size, training=False),
        {
            "dataset": "CUB-200-2011",
            "root": str(root),
            "train": 5994,
            "test": 5794,
            "metadata_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        },
        CLASSES,
    )
