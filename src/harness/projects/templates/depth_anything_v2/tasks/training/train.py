"""Train and validate the upstream distributed metric-depth model."""

import argparse
import json
import logging
import os
import pprint
import random
from shutil import make_archive
from tempfile import TemporaryDirectory

from pathlib import Path
import torch
import torch.backends.cudnn as cudnn
import torch.distributed as dist
from torch.utils.data import DataLoader
from torch.optim import AdamW
import torch.nn.functional as F

from ...datasets.hypersim_images.dataset import Hypersim
from ...datasets.kitti_images.dataset import KITTI
from ...datasets.virtual_kitti.dataset import VKITTI2
from depth_anything_v2.weights import ENCODERS, build_model
from ...dist_helper import setup_distributed
from .loss import SiLogLoss
from .metric import eval_depth
from ...logging_setup import init_log
from ...records import RunRecord, effective_options
from ..precheck.check import training_inputs, training_precheck


def main(argv, workspace, inference, training, encoders):
    parser = argparse.ArgumentParser(prog="depth-anything train", description="Distributed metric depth training")
    parser.add_argument("--encoder", default=inference["encoder"], choices=ENCODERS)
    parser.add_argument("--dataset", default=training["dataset"], choices=["hypersim", "vkitti"])
    parser.add_argument("--img-size", default=inference["input_size"], type=int)
    parser.add_argument("--min-depth", default=training["min_depth"], type=float)
    parser.add_argument("--max-depth", default=inference["max_depth"], type=float)
    parser.add_argument("--epochs", "--epoch", default=training["epochs"], type=int)
    parser.add_argument("--bs", default=training["batch_size"], type=int)
    parser.add_argument("--lr", default=training["learning_rate"], type=float)
    parser.add_argument("--pretrained-from", type=Path)
    parser.add_argument("--save-path", type=Path, help="Export the original checkpoint and TensorBoard event files")
    parser.add_argument("--study", default="metric_finetuning")
    parser.add_argument("--train-split", type=Path)
    parser.add_argument("--validation-split", type=Path)
    parser.add_argument("--local-rank", "--local_rank", type=int, default=0)
    parser.add_argument("--port", type=int)
    parser.add_argument("--precheck", action="store_true", help="Run one isolated training step and one validation sample")
    args = parser.parse_args(argv)

    splits = workspace / "assets" / "splits"
    train_set, val_set = ("hypersim_images", "hypersim_images") if args.dataset == "hypersim" else ("virtual_kitti", "kitti_images")
    args.train_split = args.train_split or splits / train_set / "files/train.txt"
    args.validation_split = args.validation_split or splits / val_set / "files/val.txt"
    training_inputs(args)
    distributed = "RANK" in os.environ or "SLURM_JOB_ID" in os.environ
    if args.precheck and not distributed:
        report = training_precheck(args, torch.device("cuda", 0))
        print(json.dumps({**effective_options(args), "precheck_report": report}, indent=2))
        return 0
    if not distributed:
        parser.error("Launch training through torchrun or Slurm. See scripts/distributed_training.sh.")

    from torch.utils.tensorboard import SummaryWriter

    logger = init_log("global", logging.INFO)
    logger.propagate = 0
    rank, world_size = setup_distributed(port=args.port)
    record = None
    try:
        args.workspace, args.outdir = workspace, args.save_path
        config = effective_options(args)
        config.update(dataset=train_set, model=encoders[args.encoder], task="training", ngpus=world_size)
        gate_error = None
        try:
            if rank == 0 and not args.precheck:
                record = RunRecord(args, config, [args.train_split, args.validation_split])
            report = training_precheck(args, torch.device("cuda", torch.cuda.current_device()), world_size)
        except Exception as error:
            gate_error = f"{type(error).__name__}: {error}"
        errors = [None] * world_size
        dist.all_gather_object(errors, gate_error)
        for failed_rank, error in enumerate(errors):
            if error is not None:
                raise ValueError(f"Training precheck failed on rank {failed_rank}: {error}")
        if args.precheck:
            if rank == 0:
                print(json.dumps({**config, "precheck_report": report}, indent=2))
            return 0
        if rank != 0:
            train(args, rank, logger)
            return 0
        record.start_work(report)
        checkpoint = record.artifact("model_checkpoint", ".pth") if record.manifest else record.directory / "latest.pth"
        logger.info("%s", pprint.pformat(config))
        with TemporaryDirectory() as scratch:
            with SummaryWriter(args.save_path or scratch) as writer:
                train(args, rank, logger, writer=writer, checkpoint_file=checkpoint)
            if record.manifest:
                event_archive = record.artifact("training_events", ".zip")
                make_archive(str(event_archive.with_suffix("")), "zip", root_dir=scratch)
        record.finish("succeeded")
        print(record.directory)
    except KeyboardInterrupt as error:
        if record is not None:
            record.finish("interrupted", error)
        raise
    except Exception as error:
        if record is not None:
            record.finish("failed", error)
        raise
    finally:
        dist.destroy_process_group()
    return 0


def training_datasets(args):
    size = (args.img_size, args.img_size)
    training_dataset, validation_dataset = {"hypersim": (Hypersim, Hypersim), "vkitti": (VKITTI2, KITTI)}[args.dataset]
    return training_dataset(args.train_split, "train", size=size), validation_dataset(
        args.validation_split, "val", size=size
    )


def training_model(args):
    model = build_model(args.encoder, args.max_depth)
    if args.pretrained_from:
        checkpoint = torch.load(args.pretrained_from, map_location="cpu", weights_only=True)
        backbone = {key: value for key, value in checkpoint.items() if key.startswith("pretrained.")}
        if not backbone.keys() & model.state_dict().keys():
            raise ValueError(f"Training weights have no matching backbone parameters: {args.pretrained_from}")
        model.load_state_dict(backbone, strict=False)
    return model


def training_optimizer(model, learning_rate):
    return AdamW(
        [
            {"params": [value for name, value in model.named_parameters() if "pretrained" in name], "lr": learning_rate},
            {"params": [value for name, value in model.named_parameters() if "pretrained" not in name], "lr": learning_rate * 10.0},
        ],
        lr=learning_rate,
        betas=(0.9, 0.999),
        weight_decay=0.01,
    )


def train_step(args, sample, model, criterion, optimizer, device):
    optimizer.zero_grad()
    image, depth, valid = (sample[field].to(device) for field in ("image", "depth", "valid_mask"))
    if random.random() < 0.5:
        image, depth, valid = (value.flip(-1) for value in (image, depth, valid))
    prediction = model(image)
    loss = criterion(prediction, depth, (valid == 1) & (depth >= args.min_depth) & (depth <= args.max_depth))
    loss.backward()
    optimizer.step()
    return loss.item()


@torch.no_grad()
def validation_step(args, sample, model, device):
    image, depth, valid = (sample[field].to(device) for field in ("image", "depth", "valid_mask"))
    depth, valid = depth[0], valid[0]
    prediction = model(image.float())
    prediction = F.interpolate(prediction[:, None], depth.shape[-2:], mode="bilinear", align_corners=True)[0, 0]
    valid = (valid == 1) & (depth >= args.min_depth) & (depth <= args.max_depth)
    if valid.sum() < 10:
        return None
    return eval_depth(prediction[valid], depth[valid])


def train(args, rank, logger, writer=None, checkpoint_file=None):
    cudnn.enabled = True
    cudnn.benchmark = True
    trainset, valset = training_datasets(args)
    trainsampler = torch.utils.data.distributed.DistributedSampler(trainset)
    trainloader = DataLoader(trainset, batch_size=args.bs, pin_memory=True, num_workers=4, drop_last=True, sampler=trainsampler)
    valsampler = torch.utils.data.distributed.DistributedSampler(valset)
    valloader = DataLoader(valset, batch_size=1, pin_memory=True, num_workers=4, drop_last=True, sampler=valsampler)

    local_rank = int(os.environ["LOCAL_RANK"])
    device = torch.device("cuda", local_rank)
    model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(training_model(args))
    model.cuda(local_rank)
    model = torch.nn.parallel.DistributedDataParallel(
        model, device_ids=[local_rank], broadcast_buffers=False, output_device=local_rank, find_unused_parameters=True,
    )
    criterion = SiLogLoss().to(device)
    optimizer = training_optimizer(model, args.lr)

    total_iters = args.epochs * len(trainloader)
    
    previous_best = {'d1': 0, 'd2': 0, 'd3': 0, 'abs_rel': 100, 'sq_rel': 100, 'rmse': 100, 'rmse_log': 100, 'log10': 100, 'silog': 100}
    
    for epoch in range(args.epochs):
        if rank == 0:
            logger.info('===========> Epoch: {:}/{:}, d1: {:.3f}, d2: {:.3f}, d3: {:.3f}'.format(epoch, args.epochs, previous_best['d1'], previous_best['d2'], previous_best['d3']))
            logger.info('===========> Epoch: {:}/{:}, abs_rel: {:.3f}, sq_rel: {:.3f}, rmse: {:.3f}, rmse_log: {:.3f}, '
                        'log10: {:.3f}, silog: {:.3f}'.format(
                            epoch, args.epochs, previous_best['abs_rel'], previous_best['sq_rel'], previous_best['rmse'], 
                            previous_best['rmse_log'], previous_best['log10'], previous_best['silog']))
        
        trainloader.sampler.set_epoch(epoch + 1)
        
        model.train()
        total_loss = 0
        
        for i, sample in enumerate(trainloader):
            loss = train_step(args, sample, model, criterion, optimizer, device)
            total_loss += loss
            iters = epoch * len(trainloader) + i
            
            lr = args.lr * (1 - iters / total_iters) ** 0.9
            
            optimizer.param_groups[0]["lr"] = lr
            optimizer.param_groups[1]["lr"] = lr * 10.0
            
            if rank == 0:
                writer.add_scalar('train/loss', loss, iters)
            
            if rank == 0 and i % 100 == 0:
                logger.info('Iter: {}/{}, LR: {:.7f}, Loss: {:.3f}'.format(i, len(trainloader), optimizer.param_groups[0]['lr'], loss))
        
        model.eval()
        
        results = {'d1': torch.tensor([0.0]).cuda(), 'd2': torch.tensor([0.0]).cuda(), 'd3': torch.tensor([0.0]).cuda(), 
                   'abs_rel': torch.tensor([0.0]).cuda(), 'sq_rel': torch.tensor([0.0]).cuda(), 'rmse': torch.tensor([0.0]).cuda(), 
                   'rmse_log': torch.tensor([0.0]).cuda(), 'log10': torch.tensor([0.0]).cuda(), 'silog': torch.tensor([0.0]).cuda()}
        nsamples = torch.tensor([0.0]).cuda()
        
        for sample in valloader:
            cur_results = validation_step(args, sample, model, device)
            if cur_results is None:
                continue
            for k in results.keys():
                results[k] += cur_results[k]
            nsamples += 1
        
        torch.distributed.barrier()
        
        for k in results.keys():
            dist.reduce(results[k], dst=0)
        dist.reduce(nsamples, dst=0)
        
        if rank == 0:
            logger.info('==========================================================================================')
            logger.info('{:>8}, {:>8}, {:>8}, {:>8}, {:>8}, {:>8}, {:>8}, {:>8}, {:>8}'.format(*tuple(results.keys())))
            logger.info('{:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}, {:8.3f}'.format(*tuple([(v / nsamples).item() for v in results.values()])))
            logger.info('==========================================================================================')
            print()
            
            for name, metric in results.items():
                writer.add_scalar(f'eval/{name}', (metric / nsamples).item(), epoch)
        
        for k in results.keys():
            if k in ['d1', 'd2', 'd3']:
                previous_best[k] = max(previous_best[k], (results[k] / nsamples).item())
            else:
                previous_best[k] = min(previous_best[k], (results[k] / nsamples).item())
        
        if rank == 0:
            checkpoint = {
                'model': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'epoch': epoch,
                'previous_best': previous_best,
            }
            torch.save(checkpoint, checkpoint_file)
