"""Generate MathVista responses through the chosen model and prompt format."""

import argparse
import io
import logging
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from rich.logging import RichHandler
from tqdm import tqdm

from mathvista.dataset.dataset import load_split, open_image
from mathvista.generation.build_query import create_query_data
from mathvista.precheck.task import check_sample
from mathvista.records import run_record
from mathvista.runtime import configuration, data_root, prepared_context, result_directory, standard_file
from models.build import generation_model, generation_model_name, qwen_weights
from utilities import read_json, save_json


def verify_response(response):
    if isinstance(response, str):
        response = response.strip()
    if response == "" or response is None:
        return False
    if "Response Error" in response:
        return False
    return True


def evaluate_code(code_string):
    # execute_code_and_capture_output
    # Backup the original stdout
    old_stdout = sys.stdout

    # Redirect stdout to capture the output
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    # Try executing the code and capture any exception
    error = None
    try:
        exec(code_string)
    except Exception as e:
        error = e

    # Restore the original stdout
    sys.stdout = old_stdout

    # Get the captured output
    captured_output = new_stdout.getvalue()
    if isinstance(captured_output, str):
        captured_output = captured_output.strip()

    # Return the captured output or error
    return captured_output, error


def parse_args(argv=None):
    config = configuration()
    parser = argparse.ArgumentParser()
    # input
    parser.add_argument('--dataset_name', type=str, default=config['dataset']['source'])
    parser.add_argument('--test_split_name', type=str, default=config['dataset']['split'])
    parser.add_argument('--data_dir', type=str, default=data_root())
    parser.add_argument('--input_file', type=str, default='testmini.json')
    # output
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--output_file', type=str, default=config["generation"]["output_file"])
    parser.add_argument('--max_num_problems', type=int, default=-1, help='The number of problems to run')
    parser.add_argument('--save_every', type=int, default=100, help='save every n problems')
    # Local Model
    parser.add_argument('--model_path', help='Select local Qwen2.5-VL weights from this directory.')
    parser.add_argument('--device', default=config["catalogs"]["model"]["qwen_vision"]["device"])
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--conv-mode", type=str, default="vicuna_v1")
    parser.add_argument("--sep", type=str, default=",")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--num_beams", type=int, default=1)
    parser.add_argument("--max_new_tokens", type=int, default=512)
    # Remote model
    parser.add_argument(
        '--model',
        type=str,
        default=config["generation"]["model"],
        help='llm engine',
        choices=['gpt-3.5-turbo', 'claude-2', 'gpt4', 'gpt-4-0613', 'bard', 'qwen_vision'],
    )
    parser.add_argument('--key', type=str, default='', help='key for llm api')
    # query
    parser.add_argument('--query_file', type=str, default=None)
    parser.add_argument('--caption_file', type=str, default=prepared_context() / "captions_bard.json")
    parser.add_argument('--ocr_file', type=str, default=prepared_context() / "ocrs_easyocr.json")
    parser.add_argument('--shot_type', type=str, default='solution', help='shot type', choices=['solution', 'code'])
    parser.add_argument('--shot_num', type=int, default=0, help='number of shot examples')
    parser.add_argument('--use_caption', action='store_true', help='use caption data')
    parser.add_argument('--use_ocr', action='store_true', help='use ocr data')
    # other settings
    parser.add_argument('--rerun', action='store_true', help='rerun answer extraction for all problems')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('--azure_openai_api_endpoint', type=str, default=os.getenv("AZURE_OPENAI_API_ENDPOINT"))
    parser.add_argument('--azure_openai_api_key', type=str, default=os.getenv("AZURE_OPENAI_API_KEY"))
    parser.add_argument('--azure_openai_api_version', type=str, default=os.getenv("AZURE_OPENAI_API_VERSION"))
    parser.add_argument('--azure_openai_model', type=str, default=os.getenv("AZURE_OPENAI_MODEL"))
    parser.add_argument('--local-split', help='Read the supplied official JSON and local images.')
    parser.add_argument('--run-purpose', default="benchmark")
    parser.add_argument('--precheck-only', action='store_true')
    args = parser.parse_args(argv)
    return args


def main(argv=None):
    args = parse_args(argv)
    name = generation_model_name(args)
    if name == "qwen_vision" and args.shot_type == "code":
        raise SystemExit("Use --shot_type solution with the local Qwen model.")
    purpose = ("qwen_precheck" if name == "qwen_vision" else "precheck") if args.precheck_only else args.run_purpose
    standard = args.output_dir is None
    directory = (result_directory(args.test_split_name, "generation", purpose)
                 if standard else Path(args.output_dir))
    if standard:
        standard_file(args.output_file)
    effective = {
        "source": args.dataset_name, "split": args.test_split_name,
        "local_file": args.local_split, "model_deployment": name,
        "query_file": args.query_file, "shot_type": args.shot_type, "shot_num": args.shot_num,
        "use_caption": args.use_caption, "caption_file": str(args.caption_file),
        "use_ocr": args.use_ocr, "ocr_file": str(args.ocr_file),
        "max_num_problems": args.max_num_problems, "precheck_only": args.precheck_only,
    }
    if name == "qwen_vision":
        weights = qwen_weights(args)
        effective["local_model"] = {
            "weights": str(weights) if weights else None,
            "device": args.device, "max_new_tokens": args.max_new_tokens,
            "max_pixels": configuration()["catalogs"]["model"]["qwen_vision"]["max_pixels"],
        }
    with run_record(directory, "generation", args.test_split_name, purpose, effective, standard=standard) as record:
        run(args, directory, record)


def run(args, directory, record):
    logging.info("MathVista: Generating Responses - Start")
    model = generation_model(args)
    logging.info("Loading dataset %s, split %s", args.dataset_name, args.test_split_name)
    data = load_split(
        args.dataset_name, args.test_split_name, images=True, local_file=args.local_split,
        limit=1 if args.precheck_only else None,
    )

    # load or create query data
    if args.query_file:
        query_file = os.path.join(args.data_dir, args.query_file)
        logging.info("Loading %s", query_file)
        query_data = read_json(query_file)
    else:
        logging.info("Creating new query...")

        caption_data = {}
        if args.use_caption:
            caption_file = args.caption_file
            if os.path.exists(caption_file):
                logging.info(f"Reading {caption_file}...")
                try:
                    caption_data = read_json(caption_file)["texts"]
                    logging.info("Caption data loaded.")
                except Exception as e:
                    logging.info("Caption data not found!! Please Check.")

        ocr_data = {}
        if args.use_ocr:
            ocr_file = args.ocr_file
            if os.path.exists(ocr_file):
                logging.info(f"Reading {ocr_file}...")
                try:
                    ocr_data = read_json(ocr_file)["texts"]
                    logging.info("OCR data loaded.")
                except Exception as e:
                    logging.info("OCR data not found!! Please Check.")

        query_data = create_query_data(data, caption_data, ocr_data, args)

    name = generation_model_name(args)

    def predict(problem_id):
        query = query_data[problem_id]
        if "claude" in name:
            return model.get_response(data[problem_id]["image"], query)
        with open_image(data[problem_id]) as image:
            if name == "bard":
                with TemporaryDirectory(prefix="mathvista-image-") as scratch:
                    path = Path(scratch) / "problem.png"
                    image.save(path)
                    return model.get_response(path, query)
            return model.get_response(user_prompt=query, decoded_image=image)

    full_pids = list(data)
    if not full_pids:
        raise ValueError("Generation requires at least one problem.")
    output_file_path = directory / args.output_file

    # load results
    if os.path.exists(output_file_path):
        logging.info("Results already exist.")
        logging.info(f"Reading {output_file_path}...")
        results = read_json(output_file_path)
    else:
        results = {}

    skip_pids = []
    if not args.rerun:
        for problem_id in full_pids:
            # logging.info(f"Checking {pid}...")
            if problem_id in results and 'response' in results[problem_id]:
                response = results[problem_id]['response']
                if verify_response(response):
                    # logging.info(f"Valid response found for {pid}.")
                    skip_pids.append(problem_id)

    if len(skip_pids) > 0:
        logging.info(
            f"Found existing results file with {len(skip_pids)} problems with valid responses. Skipping these problems..."
        )

    test_pids = [pid for pid in full_pids if pid not in skip_pids]

    if args.max_num_problems > 0:
        test_pids = test_pids[: min(args.max_num_problems, len(test_pids))]
        logging.warning(f'Limiting number of problems to {args.max_num_problems}.')

    logging.info(f"Number of test problems to run: {len(test_pids)}")

    sample_pid = test_pids[0] if test_pids else full_pids[0]

    def probe():
        response = predict(sample_pid) if test_pids else results[sample_pid]["response"]
        if not verify_response(response):
            raise ValueError(f"No valid response for precheck problem {sample_pid}.")
        return {"pid": sample_pid, "response": response}

    report = check_sample(probe)
    logging.info("Generation precheck passed for problem %s", sample_pid)
    record(report, formal_started=not args.precheck_only)
    if args.precheck_only:
        return

    directory.mkdir(parents=True, exist_ok=True)
    for i, problem_id in enumerate(tqdm(test_pids)):
        problem = data[problem_id].copy()
        problem.pop("decoded_image", None)

        query = query_data[problem_id]

        logging.debug("--------------------------------------------------------------")
        logging.debug(f"Generating response for problem: {problem_id}...")
        try:
            response = report["sample"]["response"] if problem_id == sample_pid else predict(problem_id)
            results[problem_id] = problem
            results[problem_id]['query'] = query
            if args.shot_type == 'solution':
                results[problem_id]['response'] = response
            else:
                output, error = evaluate_code(response)
                results[problem_id]['response'] = response
                results[problem_id]['execution'] = output
                results[problem_id]['error'] = str(error)
            logging.debug(f"Query: \n{query}")
            logging.debug(f"Response: \n{response}")
        except Exception as e:
            logging.error(f"Error in extracting answer for {problem_id}")
            logging.error(e)
            results[problem_id] = problem
            results[problem_id]['error'] = str(e)

        if (i % args.save_every == 0 and i > 0) or i == len(test_pids) - 1:
            try:
                save_json(results, output_file_path)
                logging.info(f"Saved results to {output_file_path}")
            except Exception as e:
                logging.info(f"Error in saving {output_file_path}")
                logging.info(e)

    logging.info("MathVista: Generating Responses - Finish")


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
