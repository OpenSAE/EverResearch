"""Read publisher DA-2K images and closer-point annotations for evaluation.

Use with an extracted dataset or an explicit list of its annotated image files.
"""

import json
from pathlib import Path

import cv2


class DepthOrderDataset:
    def __init__(self, dataset_root, sample_list=None):
        self.root = dataset_root.resolve()
        self.annotation_file = self.root / "annotations.json"
        self.annotations = json.loads(self.annotation_file.read_text(encoding="utf-8"))
        if sample_list is None:
            self.names = sorted(self.annotations)
        else:
            self.names = [
                Path(line).resolve().relative_to(self.root).as_posix()
                for line in sample_list.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        if (
            not self.names
            or len(set(self.names)) != len(self.names)
            or any(name not in self.annotations for name in self.names)
        ):
            raise ValueError("Supply a nonempty list of distinct annotated benchmark images.")

    def path(self, name):
        return self.root / name

    def read(self, name):
        path = self.path(name)
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Cannot decode benchmark image {path}")
        return image, self.annotations[name]
