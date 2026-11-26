"""Evaluate Meta's released linear classifier or dino.txt on ImageNet images.

Uses the project's ImageNet validation reader and 224-pixel evaluation transform.
The dino.txt recipe uses one fixed natural-language prompt for each label.
"""

import argparse
import ast
import json
from pathlib import Path
import time

START = time.perf_counter()

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset

from dinov2.data.datasets import ImageNet
from dinov2.data.transforms import make_classification_eval_transform
from dinov2.hub.classifiers import dinov2_vits14_lc
from dinov2.hub.dinotxt import dinov2_vitl14_reg4_dinotxt_tet1280d20h24l


def class_names():
    notebook = Path(__file__).resolve().parent / "notebooks/image_text.ipynb"
    for cell in json.loads(notebook.read_text())["cells"]:
        source = "".join(cell["source"])
        if "imagenet_clip_class_names=" not in source:
            continue
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "imagenet_clip_class_names"
                for target in node.targets
            ):
                names = ast.literal_eval(node.value)
                if len(names) != 1000:
                    raise ValueError("Expected 1,000 ImageNet class names")
                return names
    raise ValueError(f"Missing ImageNet class names in {notebook}")


@torch.inference_mode()
def evaluate(args):
    torch.set_num_threads(4)
    torch.hub.set_dir(str(args.weights.parent))
    dataset = ImageNet(split=ImageNet.Split.VAL, root=str(args.root), extra=str(args.extra),
                       transform=make_classification_eval_transform())
    count = len(np.load(args.extra / "entries-VAL.npy", mmap_mode="r", allow_pickle=False))
    if args.sample:
        indices = np.linspace(0, count - 1, min(count, args.sample), dtype=int)
        dataset = Subset(dataset, indices)
    loader = DataLoader(dataset, batch_size=args.batch_size, num_workers=args.workers,
                        pin_memory=True)
    if args.method == "linear":
        model = dinov2_vits14_lc().eval().cuda()
        predict = model
    else:
        from dinov2.hub.text.tokenizer import Tokenizer

        model = dinov2_vitl14_reg4_dinotxt_tet1280d20h24l().eval().cuda()
        tokenizer = Tokenizer(str(args.weights / "bpe_simple_vocab_16e6.txt.gz"))
        prompts = [f"a photo of a {name}." for name in class_names()]
        names = []
        for offset in range(0, len(prompts), args.batch_size):
            tokens = tokenizer.tokenize(prompts[offset:offset + args.batch_size]).cuda()
            names.append(F.normalize(model.encode_text(tokens), dim=-1))
        weights = torch.cat(names)
        def predict(pixels):
            return F.normalize(model.encode_image(pixels), dim=-1) @ weights.T

    (args.output / "artifacts").mkdir(parents=True, exist_ok=False)
    (args.output / "reports").mkdir()
    torch.cuda.synchronize()
    startup = time.perf_counter() - START
    batches = []
    correct1 = correct5 = samples = 0
    before = time.perf_counter()
    with (args.output / "artifacts" / "predictions.jsonl").open("w") as records:
        for pixels, labels in loader:
            scores, classes = predict(pixels.cuda(non_blocking=True)).topk(5)
            for actual, predicted, values in zip(labels.tolist(), classes.tolist(), scores.tolist()):
                correct1 += actual == predicted[0]
                correct5 += actual in predicted
                samples += 1
                records.write(json.dumps({"label": actual, "classes": predicted, "scores": values}) + "\n")
            batches.append({"samples": len(labels), "seconds": time.perf_counter() - before})
            before = time.perf_counter()
    metrics = {"top1": correct1 / samples, "top5": correct5 / samples}
    (args.output / "artifacts" / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    runtime = {"sample_count": samples, "batch_size": args.batch_size, "loader_workers": args.workers,
               "startup_seconds": startup, "elapsed_seconds": time.perf_counter() - START,
               "batches": batches, "torch": torch.__version__, "cuda": torch.version.cuda,
               "gpu": torch.cuda.get_device_name()}
    (args.output / "reports" / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
    print(json.dumps({**metrics, "sample_count": samples, "seconds": runtime["elapsed_seconds"]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=("linear", "text"))
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--extra", required=True, type=Path)
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--sample", type=int)
    args = parser.parse_args()
    if args.batch_size < 1 or args.workers < 0 or (args.sample is not None and args.sample < 1):
        parser.error("batch and sample sizes must be positive, and workers must be nonnegative")
    evaluate(args)


if __name__ == "__main__":
    main()
