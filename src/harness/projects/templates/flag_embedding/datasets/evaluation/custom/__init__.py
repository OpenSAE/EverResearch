from pathlib import Path
from typing import List, Optional

from FlagEmbedding.abc.evaluation import AbsEvalDataLoader


class CustomEvalDataLoader(AbsEvalDataLoader):
    """Discover a local JSONL corpus and its query and relevance splits."""

    def _dataset_root(self) -> Path:
        if self.dataset_dir is None:
            raise ValueError("Custom evaluation requires --dataset_dir with local JSONL files.")
        if self.force_redownload:
            raise ValueError("Custom evaluation reads local data. Omit --force_redownload.")
        root = Path(self.dataset_dir)
        if not root.is_dir():
            raise FileNotFoundError(f"Custom dataset directory does not exist: {root}")
        return root

    def available_dataset_names(self) -> List[str]:
        root = self._dataset_root()
        if (root / "corpus.jsonl").is_file():
            return []
        names = sorted(path.name for path in root.iterdir() if (path / "corpus.jsonl").is_file())
        if not names:
            raise FileNotFoundError(f"No corpus.jsonl in {root} or any of its immediate subdirectories.")
        return names

    def available_splits(self, dataset_name: Optional[str] = None) -> List[str]:
        root = self._dataset_root()
        if dataset_name is not None:
            root = root / dataset_name
        splits = []
        for query_file in root.glob("*_queries.jsonl"):
            split = query_file.name[:-len("_queries.jsonl")]
            if split and query_file.is_file() and (root / f"{split}_qrels.jsonl").is_file():
                splits.append(split)
        return sorted(splits)
