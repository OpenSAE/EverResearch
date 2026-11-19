"""目的：执行分类训练和评估并计算 Top-1 准确率、平均交叉熵。

适用范围：共享给正式训练、Precheck 和性能比较。
"""

import math
from time import perf_counter

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset

from ...runtime.config import synchronize


def loader(dataset, config, workers, *, training=False):
    return DataLoader(
        dataset,
        batch_size=config["training"]["batch_size"],
        num_workers=workers,
        shuffle=training,
        drop_last=False,
        generator=torch.Generator().manual_seed(config["training"]["seed"]),
    )


def step(model, batch, device, optimizer=None):
    images, labels = (value.to(device) for value in batch)
    with torch.set_grad_enabled(optimizer is not None):
        if optimizer is not None:
            optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = nn.functional.cross_entropy(logits, labels)
        if optimizer is not None:
            loss.backward()
            optimizer.step()
    return logits.detach(), loss.detach(), labels


def epoch(model, batches, device, optimizer=None):
    model.train(optimizer is not None)
    total = 0
    correct = torch.zeros((), device=device, dtype=torch.int64)
    loss_sum = torch.zeros((), device=device)
    for batch in batches:
        logits, loss, labels = step(model, batch, device, optimizer)
        total += len(labels)
        correct += (logits.argmax(dim=1) == labels).sum()
        loss_sum += loss * len(labels)
    if not total:
        raise ValueError("分类阶段没有样本")
    mean_loss = loss_sum.item() / total
    if not torch.isfinite(loss_sum).item():
        raise ValueError("分类阶段出现非有限损失")
    return {"samples": total, "top1_accuracy": correct.item() / total, "loss": mean_loss}


def precheck(model, train, fixed_train, device, cfg):
    synchronize(device)
    start = perf_counter()
    batch_size = cfg["training"]["batch_size"]
    samples = min(cfg["precheck"]["samples"], batch_size, len(train))
    workers = cfg["runtime"]["workers"]
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["training"]["learning_rate"])
    train_batch = loader(Subset(train, range(samples)), cfg, workers, training=True)
    evaluation_batch = loader(Subset(fixed_train, range(samples)), cfg, workers)
    training = epoch(model, train_batch, device, optimizer)
    tail = len(train) % batch_size
    if tail == 1 and samples != 1:
        tail_batch = loader(Subset(train, [len(train) - 1]), cfg, workers, training=True)
        try:
            epoch(model, tail_batch, device, optimizer)
        except (RuntimeError, ValueError) as exc:
            raise ValueError(
                f"训练最后一批只有一张图，当前模型无法完成该批次。"
                f"请更换批大小或图像尺寸后重新预检。原始错误：{exc}"
            ) from exc
    evaluation = epoch(model, evaluation_batch, device)
    synchronize(device)
    return {
        "train_step": training,
        "evaluation_step": evaluation,
        "workers": workers,
        "singleton_tail_checked": tail == 1,
        "seconds": perf_counter() - start,
    }


def train_model(run, model, train, test, device, cfg):
    settings = cfg["training"]
    optimizer = torch.optim.AdamW(model.parameters(), lr=settings["learning_rate"])
    workers = cfg["runtime"]["workers"]
    batches = loader(train, cfg, workers, training=True)
    history = []
    for index in range(settings["epochs"]):
        synchronize(device)
        started = perf_counter()
        metrics = epoch(model, batches, device, optimizer)
        synchronize(device)
        history.append({"epoch": index + 1, **metrics, "seconds": perf_counter() - started})
        run.report("training", history)
    started = perf_counter()
    evaluation = epoch(model, loader(test, cfg, workers), device)
    synchronize(device)
    run.report("evaluation", {**evaluation, "seconds": perf_counter() - started})
    relative = "artifacts/model.pt"
    path = run.root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)
    run.manifest["outputs"]["model"] = relative
    return evaluation


def validate_config(cfg, operation):
    limits = [("training", "batch_size", 2)]
    if operation == "train":
        limits.append(("training", "epochs", 1))
    elif operation == "precheck":
        limits.append(("precheck", "samples", 2))
    for section, key, minimum in limits:
        value = cfg[section][key]
        if type(value) is not int or value < minimum:
            raise ValueError(f"{section}.{key} 必须是至少 {minimum} 的整数")
    if operation in {"train", "precheck"}:
        rate = cfg["training"]["learning_rate"]
        if type(rate) not in {int, float} or not math.isfinite(rate) or rate <= 0:
            raise ValueError("training.learning_rate 必须是有限正数")


def validate_components(dataset, model):
    if dataset.CLASSES != model.CLASSES:
        raise ValueError(f"数据包含 {dataset.CLASSES} 类，模型输出 {model.CLASSES} 类")
