"""Run and record a speech workload on a local publisher test split."""

import argparse
import csv
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
from zipfile import ZIP_DEFLATED, ZipFile

STARTED = perf_counter()

import jiwer
import soundfile
import torch
import whisper
from sacrebleu.metrics import BLEU
from whisper._precheck import check_sample, read_sample, require_audio_decoder
from whisper.experiments import Experiment, experiment_directory, write_json
from whisper.normalizers import EnglishTextNormalizer
from whisper.utils import get_writer


def corpus_rows(root, corpus):
    if corpus == "librispeech":
        return [
            (labels.parent / f"{item}.flac", reference)
            for labels in sorted(root.glob("*/*/*.trans.txt"))
            for item, reference in (
                line.split(maxsplit=1) for line in labels.read_text().splitlines()
            )
        ]
    return [
        (root / "audio" / "test" / row[1], row[3])
        for row in read_fleurs_labels(root / "test.tsv")
    ]


def read_fleurs_labels(path):
    with path.open(encoding="utf-8", newline="") as labels:
        return list(csv.reader(labels, delimiter="\t"))


def translation_references(source, target):
    english = {row[0]: row[2] for row in read_fleurs_labels(target)}
    return {row[1]: (row[0], english[row[0]]) for row in read_fleurs_labels(source)}


def audio_info(path, reference):
    info = soundfile.info(path)
    if info.samplerate != whisper.audio.SAMPLE_RATE or info.channels != 1:
        raise ValueError(f"Expected mono 16 kHz audio in {path}")
    return path, reference, info.frames / info.samplerate


def short_form_mel(path, device):
    audio, _ = soundfile.read(path, dtype="float32")
    audio = whisper.pad_or_trim(torch.from_numpy(audio)).to(device)
    return whisper.log_mel_spectrogram(audio)


def recognize(batch, model, options):
    mels = torch.stack([short_form_mel(path, model.device) for path, _, _ in batch])
    return [{"text": result.text} for result in model.decode(mels, options)]


def identify(path, model, fp16):
    audio = whisper.pad_or_trim(whisper.load_audio(path))
    dtype = torch.float16 if fp16 else torch.float32
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(
        model.device, dtype=dtype
    )
    _, probabilities = model.detect_language(mel)
    return {
        "language": max(probabilities, key=probabilities.get),
        "probabilities": probabilities,
    }


def collect_metrics(args, records):
    if args.mode == "evaluate":
        comparison = jiwer.process_words(
            [record["normalized_reference"] for record in records],
            [record["normalized_text"] for record in records],
        )
        return {
            name: getattr(comparison, name)
            for name in ("wer", "hits", "substitutions", "insertions", "deletions")
        }
    if args.mode == "identify":
        correct = sum(record["language"] == args.language for record in records)
        return {
            "expected_language": args.language,
            "correct": correct,
            "accuracy": correct / len(records),
        }
    if args.english_references:
        metric = BLEU()
        score = metric.corpus_score(
            [record["text"].strip() for record in records],
            [[record["english_reference"] for record in records]],
        )
        return {"bleu": score.score, "signature": str(metric.get_signature())}
    return {}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=("transcribe", "translate", "timestamps", "evaluate", "identify"),
    )
    parser.add_argument("--corpus", choices=("librispeech", "fleurs"), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--model", choices=whisper.available_models(), required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument(
        "--language", choices=whisper.tokenizer.LANGUAGES, required=True
    )
    parser.add_argument("--purpose", required=True)
    parser.add_argument(
        "--samples",
        type=int,
        help="Evenly spaced rows of the ordered split, rounded up to a full batch",
    )
    parser.add_argument(
        "--english-references",
        type=Path,
        help="FLEURS en_us test.tsv for translation scoring",
    )
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    if args.mode == "evaluate" and (args.corpus, args.language, args.model) != (
        "librispeech",
        "en",
        "base.en",
    ):
        parser.error(
            "English WER follows the LibriSpeech notebook with the en language and base.en weights"
        )
    if args.mode == "translate" and (
        args.model.endswith(".en") or args.model in {"turbo", "large-v3-turbo"}
    ):
        parser.error(
            "Speech translation requires translation-capable multilingual weights"
        )
    if args.english_references and (args.mode, args.corpus) != ("translate", "fleurs"):
        parser.error("--english-references requires FLEURS translation")
    if args.samples is not None and args.samples < 1:
        parser.error("--samples must be positive")
    return args


def run(args):
    root = Path(__file__).resolve().parents[1]
    data_root = args.data_root.resolve(strict=True)
    batch_size = 16 if args.mode == "evaluate" else 1
    fp16 = torch.device(args.device).type == "cuda"
    task = "translate" if args.mode == "translate" else "transcribe"
    decoding = {
        "task": task,
        "language": args.language,
        "fp16": fp16,
        "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        "beam_size": 5,
        "best_of": 5,
        "word_timestamps": args.mode == "timestamps",
        "verbose": None,
    }
    options = whisper.DecodingOptions(language="en", without_timestamps=True, fp16=fp16)
    settings = {
        "evaluate": vars(options),
        "identify": {"fp16": fp16, "window_seconds": 30},
    }
    rows = [
        audio_info(path, reference)
        for path, reference in corpus_rows(data_root, args.corpus)
    ]
    if not rows:
        raise ValueError(f"No publisher test rows in {data_root}")
    english_references = args.english_references and args.english_references.resolve(
        strict=True
    )
    translations = (
        translation_references(data_root / "test.tsv", english_references)
        if english_references
        else {}
    )
    count = len(rows)
    if args.samples is not None:
        sample_batches = (args.samples + batch_size - 1) // batch_size
        count = min(sample_batches * batch_size, count)
    selected = [
        rows[(2 * index + 1) * len(rows) // (2 * count)] for index in range(count)
    ]
    run_dir = experiment_directory(root, args.purpose)
    experiment = Experiment(
        run_dir,
        {
            "dataset": "audio",
            "model": "whisper",
            "task": "speech",
            "workload": args.mode,
            "corpus": args.corpus,
            "split": "test-clean" if args.corpus == "librispeech" else "test",
            "data_root": str(data_root),
            "model_name": args.model,
            "model_dir": str(args.model_dir.resolve()),
            "device": args.device,
            "batch_size": batch_size,
            "loader_workers": 0,
            "language": args.language,
            "english_references": (
                str(english_references) if english_references else None
            ),
            "requested_samples": args.samples,
            "decoding": settings.get(args.mode, decoding),
        },
    )
    try:
        require_audio_decoder()
        model = whisper.load_model(
            args.model, device=args.device, download_root=args.model_dir
        )
        if args.mode == "identify" and not model.is_multilingual:
            raise ValueError("Language identification requires multilingual weights")
        first_path = selected[0][0]
        report = check_sample(
            read_sample(str(first_path)),
            model,
            task=task,
            language=args.language,
            fp16=fp16,
        )
        if args.mode == "evaluate":
            recognize(selected[:1], model, options)
        if args.mode == "identify":
            identify(str(first_path), model, fp16)
        startup_seconds = perf_counter() - STARTED
        experiment.save_precheck(startup_seconds, report)
        experiment.start()
        if args.samples is not None:
            print(f"Startup and precheck: {startup_seconds:.3f} s", flush=True)
        artifacts = run_dir / "artifacts"
        artifacts.mkdir()
        samples = []
        batches = []
        normalize = EnglishTextNormalizer() if args.mode == "evaluate" else None
        subtitle_dir = run_dir / "tmp"
        if args.mode == "timestamps":
            subtitle_dir.mkdir()
        with (artifacts / "utterance_results.jsonl").open(
            "w", encoding="utf-8"
        ) as output:
            experiment.manifest["outputs"][
                "utterance_results"
            ] = "artifacts/utterance_results.jsonl"
            for start in range(0, len(selected), batch_size):
                batch = selected[start : start + batch_size]
                tick = perf_counter()
                if args.mode == "evaluate":
                    predictions = recognize(batch, model, options)
                elif args.mode == "identify":
                    predictions = [
                        identify(str(path), model, fp16) for path, _, _ in batch
                    ]
                else:
                    predictions = [
                        model.transcribe(str(path), **decoding) for path, _, _ in batch
                    ]
                for (path, reference, duration), prediction in zip(
                    batch, predictions, strict=True
                ):
                    sample = dict(
                        audio=str(path.relative_to(data_root)),
                        duration_seconds=duration,
                        reference=reference,
                        **prediction,
                    )
                    if normalize is not None:
                        sample["normalized_reference"] = normalize(reference)
                        sample["normalized_text"] = normalize(prediction["text"])
                    if translations:
                        sample["utterance_id"], sample["english_reference"] = (
                            translations[path.name]
                        )
                    if args.mode in {"evaluate", "identify"} or translations:
                        samples.append(sample)
                    if args.mode == "timestamps":
                        for kind in ("srt", "vtt"):
                            get_writer(kind, str(subtitle_dir))(
                                prediction, path.name, highlight_words=True
                            )
                    output.write(json.dumps(sample, ensure_ascii=False) + "\n")
                batches.append(
                    {
                        "count": len(batch),
                        "audio_seconds": sum(row[2] for row in batch),
                        "elapsed_seconds": perf_counter() - tick,
                    }
                )
                if args.samples is not None:
                    output.flush()
                    print(
                        json.dumps(dict(completed=start + len(batch), **batches[-1])),
                        flush=True,
                    )
        if args.mode == "timestamps":
            with ZipFile(
                artifacts / "subtitles.zip", "w", compression=ZIP_DEFLATED
            ) as archive:
                for path in sorted(subtitle_dir.iterdir()):
                    archive.write(path, path.name)
                    path.unlink()
            subtitle_dir.rmdir()
            experiment.manifest["outputs"]["subtitles"] = "artifacts/subtitles.zip"
        metrics = collect_metrics(args, samples)
        if metrics:
            write_json(artifacts / "metrics.json", metrics)
            experiment.manifest["outputs"]["metrics"] = "artifacts/metrics.json"
        runtime = {
            "python": platform.python_version(),
            "interpreter": sys.executable,
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "torch_cpu_threads": torch.get_num_threads(),
            "gpu": torch.cuda.get_device_name(model.device) if fp16 else None,
            "peak_reserved_gpu_bytes": (
                torch.cuda.max_memory_reserved(model.device) if fp16 else None
            ),
            "model_sha256": whisper._MODELS[args.model].split("/")[-2],
            "sample_count": count,
            "sample_audio_seconds": sum(row[2] for row in selected),
            "split_count": len(rows),
            "split_audio_seconds": sum(row[2] for row in rows),
            "sample_duration_range_seconds": [
                min(row[2] for row in selected),
                max(row[2] for row in selected),
            ],
            "split_duration_range_seconds": [
                min(row[2] for row in rows),
                max(row[2] for row in rows),
            ],
            "split_longer_than_thirty_seconds": sum(row[2] > 30 for row in rows),
            "startup_seconds": startup_seconds,
            "batches": batches,
            "elapsed_before_record_seconds": perf_counter() - STARTED,
        }
        write_json(run_dir / "reports" / "runtime.json", runtime)
        experiment.manifest["outputs"]["runtime"] = "reports/runtime.json"
    except KeyboardInterrupt:
        experiment.finish("interrupted")
        raise
    except Exception as error:
        experiment.finish("failed", error)
        raise
    experiment.finish("succeeded")
    print(run_dir)
    print(f"Workload time through publication: {perf_counter() - STARTED:.3f} s")


if __name__ == "__main__":
    run(parse_args())
