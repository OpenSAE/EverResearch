"""Extract short answers from the MathVista model response records."""

import argparse
import logging
import os
import re
from pathlib import Path
from functools import cached_property

from rich.logging import RichHandler
from tqdm import tqdm

from mathvista.extraction.prompt import demo_prompt
from mathvista.precheck.task import check_sample
from mathvista.records import run_record
from mathvista.runtime import configuration, result_directory, standard_file
from models.build import azure_model, qwen_model, qwen_weights
from utilities import read_json, save_json


def verify_extraction(extraction):
    extraction = extraction.strip()
    if extraction == "" or extraction == None:
        return False
    return True


def create_test_prompt(demo_prompt, query, response):
    demo_prompt = demo_prompt.strip()
    test_prompt = f"{query}\n\n{response}"
    full_prompt = f"{demo_prompt}\n\n{test_prompt}\n\nExtracted answer: "
    return full_prompt


def extract_answer(model, response, problem, quick_extract=False):
    question_type = problem['question_type']
    answer_type = problem['answer_type']
    choices = problem['choices']
    query = problem['query']
    pid = problem['pid']

    if response == "":
        return ""

    if question_type == 'multi_choice' and response in choices:
        return response

    if answer_type == "integer":
        try:
            extraction = int(response)
            return str(extraction)
        except Exception as e:
            pass

    if answer_type == "float":
        try:
            extraction = str(float(response))
            return extraction
        except Exception as e:
            pass

    # quick extraction
    if quick_extract:
        logging.info("Quickly extracting answer...")
        # The answer is "text". -> "text"
        try:
            result = re.search(r'The answer is "(.*)"\.', response)
            if result:
                extraction = result.group(1)
                return extraction
        except Exception as e:
            pass

    # general extraction
    try:
        full_prompt = create_test_prompt(demo_prompt, query, response)
        extraction = model.get_response(user_prompt=full_prompt)
        return extraction
    except ValueError:
        raise
    except Exception as e:
        logging.info(f"Error in extracting answer for problem: {pid} with response: {response}")
        logging.info(e)

    return ""


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    # input
    parser.add_argument('--results_file_path', help='Update this legacy result file in place.')
    parser.add_argument('--input', help='Read responses from this file and write an extracted copy.')
    parser.add_argument('--output_dir', help='Legacy result directory.')
    parser.add_argument('--output_file', help='Legacy results filename.')
    parser.add_argument('--test_split_name', default=configuration()['dataset']['split'])
    parser.add_argument('--run-purpose', default='benchmark')
    parser.add_argument('--precheck-only', action='store_true')
    parser.add_argument('--extractor', choices=['azure', 'qwen_vision'], default='azure')
    parser.add_argument('--model_path', help='Select local Qwen2.5-VL weights from this directory.')
    parser.add_argument('--device', default=configuration()["catalogs"]["model"]["qwen_vision"]["device"])
    parser.add_argument('--max_new_tokens', type=int, default=32)
    parser.add_argument('--response_label', type=str, default='response', help='response label for the input file')
    parser.add_argument('--max_num_problems', type=int, default=-1, help='The max number of problems to run')
    parser.add_argument('--quick_extract', action='store_true', help='use rules to extract answer for some problems')
    parser.add_argument('--rerun', action='store_true', help='rerun the answer extraction')
    # output
    parser.add_argument('--save_every', type=int, default=100, help='save every n problems')

    parser.add_argument('--azure_openai_api_endpoint', type=str, default=os.getenv("AZURE_OPENAI_API_ENDPOINT"))
    parser.add_argument('--azure_openai_api_key', type=str, default=os.getenv("AZURE_OPENAI_API_KEY"))
    parser.add_argument('--azure_openai_api_version', type=str, default=os.getenv("AZURE_OPENAI_API_VERSION"))
    parser.add_argument('--azure_openai_model', type=str, default=os.getenv("AZURE_OPENAI_MODEL"))

    args = parser.parse_args(argv)
    return args


class LazyExtractor:
    """Construct the remote extractor only when the answer requires it."""

    def __init__(self, args):
        self.args = args

    @cached_property
    def model(self):
        return qwen_model(self.args) if self.args.extractor == "qwen_vision" else azure_model(self.args)

    def get_response(self, **kwargs):
        return self.model.get_response(**kwargs)


def main(argv=None):
    args = parse_args(argv)
    if args.model_path:
        args.extractor = "qwen_vision"
    purpose = ("qwen_precheck" if args.extractor == "qwen_vision" else "precheck") if args.precheck_only else args.run_purpose
    standard = not (args.results_file_path or args.output_dir or (args.output_file and not args.input))
    if standard:
        directory = result_directory(args.test_split_name, "extraction", purpose)
        filename = standard_file(args.output_file or "predictions.json")
        output = directory / filename
    else:
        output = Path(args.results_file_path or Path(args.output_dir or ".") / (args.output_file or "answer.json"))
        directory = output.parent
    effective = {
        "input": str(args.input or output), "response_label": args.response_label,
        "model_deployment": "qwen_vision" if args.extractor == "qwen_vision" else args.azure_openai_model,
        "quick_extract": args.quick_extract,
        "max_num_problems": args.max_num_problems, "precheck_only": args.precheck_only,
    }
    if args.extractor == "qwen_vision":
        weights = qwen_weights(args)
        effective["local_model"] = {
            "weights": str(weights) if weights else None,
            "device": args.device, "max_new_tokens": args.max_new_tokens,
        }
    with run_record(directory, "extraction", args.test_split_name, purpose, effective, standard=standard) as record:
        run(args, output, record)


def run(args, output, record):
    label = args.response_label
    model = LazyExtractor(args)
    results = read_json(args.input or output)

    full_pids = list(results.keys())

    skip_pids = []
    for pid, problem in results.items():
        extraction = problem.get('extraction')
        if extraction is not None and verify_extraction(extraction):
            skip_pids.append(problem['pid'])

    if args.rerun:
        test_pids = full_pids
    else:
        if len(skip_pids) > 0:
            logging.info(
                f"Found existing results file with {len(skip_pids)} problems with valid responses. Skipping these problems..."
            )
        test_pids = [pid for pid in full_pids if pid not in skip_pids]

    if args.max_num_problems > 0:
        test_pids = test_pids[: min(args.max_num_problems, len(test_pids))]
        logging.info(f'Limiting number of problems to {args.max_num_problems}.')

    if not full_pids:
        raise ValueError("Extraction requires at least one response.")

    def extract(pid):
        problem = results[pid]
        return extract_answer(model, problem[label], problem, args.quick_extract)

    sample_pid = test_pids[0] if test_pids else full_pids[0]

    def probe():
        extraction = extract(sample_pid) if test_pids else results[sample_pid]["extraction"]
        if not extraction:
            raise ValueError(f"No answer was extracted for problem {sample_pid}. Check the response and extractor settings.")
        return {"pid": sample_pid, "extraction": extraction}

    report = check_sample(probe)
    logging.info("Extraction precheck passed for problem %s", sample_pid)
    record(report, formal_started=not args.precheck_only)
    if args.precheck_only:
        return

    logging.info("Extracting %s responses", len(test_pids))
    if args.input:
        output.parent.mkdir(parents=True, exist_ok=True)
    for i, pid in enumerate(tqdm(test_pids)):
        value = report["sample"]["extraction"] if pid == sample_pid else extract(pid)
        results[pid]["extraction"] = value
        if (i % args.save_every == 0 and i > 0) or i == len(test_pids) - 1:
            save_json(results, output)
    if args.input and not test_pids:
        save_json(results, output)

    logging.info("MathVista: Extract Answers - Finish")


if __name__ == '__main__':
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format="[%(name)s] %(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=False,
                show_path=False,
                omit_repeated_times=False,
            )
        ],
    )
    logger_blocklist = [
        "asyncio",
        "azure",
        "azureml",
        "datasets",
        "httpx",
        "httpcore",
        "filelock",
        "fsspec",
        "msal",
        "msrest",
        "openai",
        "PIL",
        "urllib3",
    ]
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)

    main()
