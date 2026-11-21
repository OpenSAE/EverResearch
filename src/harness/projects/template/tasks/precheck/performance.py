"""Purpose: Time-consuming baseline analysis and comparison of accelerated candidates with consistent results.

Scope of application: Fixed input and forward steps provided through a formal mission to assess the data loading process.
"""

from statistics import median

import torch

from .timing import timed

PHASES = ("loader_startup", "input_wait", "forward_and_transfer", "loader_shutdown")
ATOL = 1e-6


def _measure(request, workload, workers):
    timings = dict.fromkeys(PHASES, 0.0)
    outputs = []
    device = request.device
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    with timed(timings, "total", device):
        with timed(timings, "loader_startup", device):
            batches = iter(workload.make_batches(workers))
        while True:
            wait = {}
            with timed(wait, "next_batch", device):
                batch = next(batches, None)
            if batch is None:
                timings["loader_shutdown"] += wait["next_batch"]
                break
            timings["input_wait"] += wait["next_batch"]
            with timed(timings, "forward_and_transfer", device):
                outputs.append(workload.forward(batch).cpu())
        with timed(timings, "loader_shutdown", device):
            del batches
    return torch.cat(outputs), {
        "seconds": timings.pop("total"),
        "stages_seconds": timings,
        "peak_cuda_reserved_bytes": (
            torch.cuda.max_memory_reserved(device) if device.type == "cuda" else None
        ),
    }


def compare(request):
    budget = request.config["benchmark"]
    baseline_workers = request.config["runtime"]["workers"]
    workers = request.candidate_workers
    workers = (2 if baseline_workers == 0 else 0) if workers is None else workers
    if workers < 0 or workers == baseline_workers:
        raise ValueError("The number of job candidates must be non-negative and different from the current configuration")

    setup = {}
    with timed(setup, "workload_setup", request.device):
        workload = request.target.performance_workload(request)
    reference = None
    results = {}
    for name, count_workers in (("baseline", baseline_workers), ("candidate", workers)):
        runs = []
        error = 0.0
        matches = True
        try:
            for repeat in range(budget["warmup"] + budget["repeats"]):
                output, run = _measure(request, workload, count_workers)
                if not torch.isfinite(output).all().item():
                    raise ValueError(f"{name} Unlimited occurrence logits")
                if reference is None:
                    reference = output
                error = max(error, (output - reference).abs().max().item())
                matches &= torch.allclose(output, reference, atol=ATOL, rtol=0) and torch.equal(
                    output.argmax(1), reference.argmax(1)
                )
                if repeat >= budget["warmup"]:
                    runs.append(run)
        except (OSError, RuntimeError, ValueError) as exc:
            if name == "baseline":
                raise
            results[name] = {
                "workers": count_workers,
                "runs": runs,
                "output_matches": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
            break
        seconds = median(run["seconds"] for run in runs)
        results[name] = {
            "workers": count_workers,
            "median_seconds": seconds,
            "images_per_second": workload.samples / seconds,
            "median_stages_seconds": {
                stage: median(run["stages_seconds"][stage] for run in runs) for stage in PHASES
            },
            "runs": runs,
            "output_matches": matches,
            "max_absolute_error": error,
        }

    baseline, candidate = results["baseline"], results["candidate"]
    phases = baseline["median_stages_seconds"]
    bottleneck = max(phases, key=phases.get)
    diagnostics = {
        "stage": bottleneck,
        "median_seconds": phases[bottleneck],
        "basis": "largest measured baseline phase by median",
        "scope": workload.scope,
    }
    cuda_limit = None
    if request.device.type == "cuda":
        total_bytes = torch.cuda.get_device_properties(request.device).total_memory
        cuda_limit = int(total_bytes * budget.get("max_cuda_memory_fraction", 0.9))
    exceeds_memory = cuda_limit is not None and any(
        run["peak_cuda_reserved_bytes"] > cuda_limit for run in candidate["runs"]
    )
    if "error" in candidate:
        decision = "candidate_failed"
    elif not baseline["output_matches"]:
        decision = "unstable_baseline"
    elif not candidate["output_matches"]:
        decision = "output_mismatch"
    elif exceeds_memory:
        decision = "candidate_exceeds_cuda_memory_budget"
    elif candidate["median_seconds"] >= baseline["median_seconds"]:
        decision = "candidate_not_faster"
    else:
        decision = "candidate_faster"
    return {
        **results,
        "samples": workload.samples,
        "scope": workload.scope,
        "setup_seconds": setup["workload_setup"],
        "bottleneck": diagnostics,
        "warmup": budget["warmup"],
        "repeats": budget["repeats"],
        "criteria": {
            "logits_atol": ATOL,
            "logits_rtol": 0,
            "same_predictions": True,
            "max_cuda_reserved_bytes": cuda_limit,
        },
        "speedup": (
            baseline["median_seconds"] / candidate["median_seconds"]
            if "median_seconds" in candidate
            else None
        ),
        "recommended_workers": workers if decision == "candidate_faster" else baseline_workers,
        "decision": decision,
    }
