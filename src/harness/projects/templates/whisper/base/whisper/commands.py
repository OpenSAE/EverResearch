"""Parse Whisper commands and coordinate input, checkpoints, and transcript outputs."""

import argparse
import json
import os
import traceback
import warnings
from pathlib import Path
from time import perf_counter

import numpy as np
import torch

from ._precheck import check_sample, read_sample, require_audio_decoder
from .experiments import Experiment, experiment_directory, read_experiment
from .resources import resource_path
from .tokenizer import LANGUAGES, TO_LANGUAGE_CODE
from .transcribe import transcribe
from .utils import get_writer, optional_float, optional_int, str2bool


def cli():
    started = perf_counter()
    from . import available_models, load_model

    formats = ["txt", "vtt", "srt", "tsv", "json", "jsonl"]

    def valid_model_name(name):
        if name in available_models() or os.path.exists(name):
            return name
        raise ValueError(
            f"model should be one of {available_models()} or path to a model checkpoint"
        )

    with resource_path("_configuration", "config.json").open(
        encoding="utf-8"
    ) as source:
        defaults = json.load(source)["cli"]

    # fmt: off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("audio", nargs="*", type=str, help="audio file(s) to transcribe")
    parser.add_argument("--model", default=defaults["model"], type=valid_model_name, help="name of the Whisper model to use")
    parser.add_argument("--model_dir", type=str, default=None, help="the path to save model files; uses ~/.cache/whisper by default")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="device to use for PyTorch inference")
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--output_dir", "-o", type=str, default=".", help="directory to save the outputs")
    destination.add_argument("--experiment", metavar="PURPOSE", help="record one input as a named experiment")
    parser.add_argument("--project-root", default=".", help="WhisperResearch checkout for named experiments")
    parser.add_argument("--precheck", action="store_true", help="check one second of the first input with the chosen model")
    parser.add_argument("--inspect-run", metavar="DIRECTORY", help="display a recorded experiment's configuration and manifest")
    parser.add_argument("--output_format", "-f", type=str, default=defaults["output_format"], choices=[*formats, "all"], help="format of the output file; if not specified, all available formats will be produced")
    parser.add_argument("--verbose", type=str2bool, default=True, help="whether to print out the progress and debug messages")

    parser.add_argument("--task", type=str, default=defaults["task"], choices=["transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--language", type=str, default=None, choices=sorted(LANGUAGES.keys()) + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]), help="language spoken in the audio, specify None to perform language detection")

    parser.add_argument("--temperature", type=float, default=0, help="temperature to use for sampling")
    parser.add_argument("--best_of", type=optional_int, default=5, help="number of candidates when sampling with non-zero temperature")
    parser.add_argument("--beam_size", type=optional_int, default=5, help="number of beams in beam search, only applicable when temperature is zero")
    parser.add_argument("--patience", type=float, default=None, help="optional patience value to use in beam decoding, as in https://arxiv.org/abs/2204.05424, the default (1.0) is equivalent to conventional beam search")
    parser.add_argument("--length_penalty", type=float, default=None, help="optional token length penalty coefficient (alpha) as in https://arxiv.org/abs/1609.08144, uses simple length normalization by default")

    parser.add_argument("--suppress_tokens", type=str, default="-1", help="comma-separated list of token ids to suppress during sampling; '-1' will suppress most special characters except common punctuations")
    parser.add_argument("--initial_prompt", type=str, default=None, help="optional text to provide as a prompt for the first window.")
    parser.add_argument("--carry_initial_prompt", type=str2bool, default=False, help="if True, prepend initial_prompt to every internal decode() call. May reduce the effectiveness of condition_on_previous_text")

    parser.add_argument("--condition_on_previous_text", type=str2bool, default=True, help="if True, provide the previous output of the model as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop")
    parser.add_argument("--fp16", type=str2bool, default=True, help="whether to perform inference in fp16; True by default")

    parser.add_argument("--temperature_increment_on_fallback", type=optional_float, default=0.2, help="temperature to increase when falling back when the decoding fails to meet either of the thresholds below")
    parser.add_argument("--compression_ratio_threshold", type=optional_float, default=2.4, help="if the gzip compression ratio is higher than this value, treat the decoding as failed")
    parser.add_argument("--logprob_threshold", type=optional_float, default=-1.0, help="if the average log probability is lower than this value, treat the decoding as failed")
    parser.add_argument("--no_speech_threshold", type=optional_float, default=0.6, help="if the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence")
    parser.add_argument("--word_timestamps", type=str2bool, default=False, help="(experimental) extract word-level timestamps and refine the results based on them")
    parser.add_argument("--prepend_punctuations", type=str, default="\"\'“¿([{-", help="if word_timestamps is True, merge these punctuation symbols with the next word")
    parser.add_argument("--append_punctuations", type=str, default="\"\'.。,，!！?？:：”)]}、", help="if word_timestamps is True, merge these punctuation symbols with the previous word")
    parser.add_argument("--highlight_words", type=str2bool, default=False, help="(requires --word_timestamps True) underline each word as it is spoken in srt and vtt")
    parser.add_argument("--max_line_width", type=optional_int, default=None, help="(requires --word_timestamps True) the maximum number of characters in a line before breaking the line")
    parser.add_argument("--max_line_count", type=optional_int, default=None, help="(requires --word_timestamps True) the maximum number of lines in a segment")
    parser.add_argument("--max_words_per_line", type=optional_int, default=None, help="(requires --word_timestamps True, no effect with --max_line_width) the maximum number of words in a segment")
    parser.add_argument("--threads", type=optional_int, default=0, help="number of threads used by torch for CPU inference; supercedes MKL_NUM_THREADS/OMP_NUM_THREADS")
    parser.add_argument("--clip_timestamps", type=str, default="0", help="comma-separated list start,end,start,end,... timestamps (in seconds) of clips to process, where the last end timestamp defaults to the end of the file")
    parser.add_argument("--hallucination_silence_threshold", type=optional_float, help="(requires --word_timestamps True) skip silent periods longer than this threshold (in seconds) when a possible hallucination is detected")
    # fmt: on

    args = parser.parse_args().__dict__
    audio_paths = args.pop("audio")
    precheck_only = args.pop("precheck")
    purpose = args.pop("experiment")
    project_root = args.pop("project_root")
    inspection = args.pop("inspect_run")
    if inspection:
        if audio_paths or purpose or precheck_only:
            parser.error(
                "--inspect-run takes a run directory without audio or run options"
            )
        try:
            print(json.dumps(read_experiment(inspection), indent=2, ensure_ascii=False))
        except (OSError, KeyError, ValueError) as error:
            parser.error(str(error))
        return
    if not audio_paths:
        parser.error("an audio input is required")
    if purpose and (len(audio_paths) != 1 or precheck_only):
        parser.error("--experiment requires exactly one audio input and a full run")

    model_name: str = args.pop("model")
    model_dir: str = args.pop("model_dir")
    output_dir: str = args.pop("output_dir")
    output_format: str = args.pop("output_format")
    device: str = args.pop("device")

    if model_name.endswith(".en") and args["language"] not in {"en", "English"}:
        if args["language"] is not None:
            warnings.warn(
                f"{model_name} is an English-only model but receipted '{args['language']}'; using English instead."
            )
        args["language"] = "en"

    temperature = args.pop("temperature")
    if (increment := args.pop("temperature_increment_on_fallback")) is not None:
        temperature = tuple(np.arange(temperature, 1.0 + 1e-6, increment))
    else:
        temperature = [temperature]

    threads = args.pop("threads")
    if threads > 0:
        torch.set_num_threads(threads)

    word_options = [
        "highlight_words",
        "max_line_count",
        "max_line_width",
        "max_words_per_line",
    ]
    if not args["word_timestamps"]:
        for option in word_options:
            if args[option]:
                parser.error(f"--{option} requires --word_timestamps True")
    if args["max_line_count"] and not args["max_line_width"]:
        warnings.warn("--max_line_count has no effect without --max_line_width")
    if args["max_words_per_line"] and args["max_line_width"]:
        warnings.warn("--max_words_per_line has no effect with --max_line_width")
    writer_args = {arg: args.pop(arg) for arg in word_options}
    audio_path = audio_paths[0]
    options = dict(args, temperature=temperature)
    if purpose or precheck_only:
        experiment = None
        if purpose:
            configuration = {
                "dataset": "audio",
                "model": "whisper",
                "task": "speech",
                "audio": audio_path,
                "working_directory": str(Path.cwd()),
                "model_name": model_name,
                "model_dir": model_dir,
                "device": device,
                "threads": threads,
                "output_format": output_format,
                "decoding": options,
                "writer": writer_args,
            }
            try:
                directory = experiment_directory(project_root, purpose)
                experiment = Experiment(directory, configuration)
            except FileExistsError:
                parser.error(f"Experiment already exists: {directory}")
            except (OSError, ValueError) as error:
                parser.error(str(error))

        try:
            require_audio_decoder()
            sample = read_sample(audio_path)
            model = load_model(model_name, device=device, download_root=model_dir)
            report = check_sample(
                sample,
                model,
                task=options["task"],
                language=options["language"],
                fp16=options["fp16"],
            )
            if precheck_only:
                print(json.dumps(report, ensure_ascii=False))
                return
            experiment.save_precheck(perf_counter() - started, report)
            experiment.start()
            result = transcribe(model, audio_path, **options)
            output_formats = formats if output_format == "all" else [output_format]
            experiment.write_transcript(result, output_formats, writer_args)
        except KeyboardInterrupt:
            if experiment is not None:
                experiment.finish("interrupted")
            raise
        except Exception as error:
            if experiment is not None:
                if not experiment.manifest["formal_started"]:
                    experiment.save_precheck(perf_counter() - started)
                experiment.finish("failed", error)
            parser.exit(1, f"whisper: {error}\n")
        experiment.finish("succeeded")
        print(str(experiment.directory))
        return

    require_audio_decoder()
    os.makedirs(output_dir, exist_ok=True)
    model = load_model(model_name, device=device, download_root=model_dir)
    writer = get_writer(output_format, output_dir)
    for audio_path in audio_paths:
        try:
            result = transcribe(model, audio_path, **options)
            writer(result, audio_path, **writer_args)
        except Exception as e:
            traceback.print_exc()
            print(f"Skipping {audio_path} due to {type(e).__name__}: {str(e)}")
