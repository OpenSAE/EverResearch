"""Normalize extracted answers and compute MathVista accuracy by group."""

import argparse
import json
import logging
import os
from pathlib import Path
import re

import pandas as pd

from Levenshtein import distance
from rich.logging import RichHandler
from tqdm import tqdm

from mathvista.dataset.dataset import load_split
from mathvista.precheck.task import check_sample
from mathvista.records import run_record
from mathvista.runtime import configuration, result_directory, standard_file
from utilities import read_json, save_json

# Extractions that state there is no answer, e.g. "N/A", "Cannot be determined",
# or "The question does not provide enough information to determine the answer."
NON_ANSWER_PATTERN = re.compile(
    r"^(n/?a|none|null|nan|unknown|no answer|undetermined|indeterminate"
    r"|not (provided|given|applicable|available|determinable)"
    r"|can(not|'t| not) (be )?(determined?|answered)"
    r"|(insufficient|not enough) (information|data))$"
    r"|^(the )?(question|text|image|figure|problem|information|data|context|graph|chart|diagram)\b"
    r".*\b(not|no|insufficient|cannot|can't|unable)\b"
    r".*\b(provide|enough|sufficient|given|determin|answer|information|clear|visible)",
    re.IGNORECASE,
)


def is_non_answer(extraction, choices):
    """
    Check if the extraction is empty or states that there is no answer.
    An option whose text is such a phrase (e.g. "None") still counts as an answer.
    """
    text = extraction.strip().strip('."\'').strip()
    if not text:
        return True
    if any(text.lower() == str(choice).strip().lower() for choice in choices):
        return False
    return bool(NON_ANSWER_PATTERN.search(text))


def get_most_similar(prediction, choices):
    """
    Use the Levenshtein distance (or edit distance) to determine which of the choices is most similar to the given prediction
    """
    distances = [distance(prediction, choice) for choice in choices]
    ind = distances.index(min(distances))
    return choices[ind]
    # return min(choices, key=lambda choice: distance(prediction, choice))


def normalize_extracted_answer(
    extraction, choices, question_type, answer_type, precision, ignore_empty_extractions=False
):
    """
    Normalize the extracted answer to match the answer type
    """
    if question_type == 'multi_choice':
        # make sure the extraction is a string
        if isinstance(extraction, str):
            extraction = extraction.strip()
        else:
            try:
                extraction = str(extraction)
            except Exception:
                extraction = ""

        # if the extraction is empty or states that there is no answer, return None
        if ignore_empty_extractions and is_non_answer(extraction, choices):
            return None

        # extract "A" from "(A) text"
        letter = re.findall(r'\(([a-zA-Z])\)', extraction)
        if len(letter) > 0:
            extraction = letter[0].upper()

        sequential_characters = [chr(ord('A') + i) for i in range(len(choices))]

        # if model output a character, use it as index of available choices
        if extraction in sequential_characters:
            option_index = sequential_characters.index(extraction)
            normalized_extraction = choices[option_index]
        elif (
            ignore_empty_extractions
            and len(extraction) == 1
            and extraction.isalpha()
            and extraction.upper() not in sequential_characters
            and extraction not in choices
        ):
            # an option letter beyond the available choices, e.g. "C" for a yes/no question
            return None
        else:
            # select the most similar option
            normalized_extraction = get_most_similar(extraction, choices)
        assert normalized_extraction in choices

    elif answer_type == 'integer':
        try:
            normalized_extraction = str(int(float(extraction)))
        except Exception:
            normalized_extraction = None

    elif answer_type == 'float':
        try:
            normalized_extraction = str(round(float(extraction), int(precision)))
        except Exception:
            normalized_extraction = None

    elif answer_type == 'list':
        try:
            normalized_extraction = str(extraction)
        except Exception:
            normalized_extraction = None

    return normalized_extraction


def safe_equal(prediction, answer):
    """
    Check if the prediction is equal to the answer, even if they are of different types
    """
    try:
        if prediction == answer:
            return True
        return False
    except Exception as e:
        logging.info(e)
        return False


def get_acc_with_contion(res_pd, key, value):
    if key == 'skills':
        # if value in res_pd[key]:
        total_pd = res_pd[res_pd[key].apply(lambda x: value in x)]
    else:
        total_pd = res_pd[res_pd[key] == value]

    correct_pd = total_pd[total_pd['true_false'] == True]
    acc = len(correct_pd) / len(total_pd) if len(total_pd) else 0

    return len(correct_pd), len(total_pd), acc


def parse_args(argv=None):
    config = configuration()
    parser = argparse.ArgumentParser()
    # input
    parser.add_argument('--dataset_name', type=str, default=config['dataset']['source'])
    parser.add_argument('--test_split_name', type=str, default=config['dataset']['split'])
    parser.add_argument('--ground_truth_file_path', '--gt_file', help='Use an official local split JSON instead of loading Hugging Face.')
    # options
    parser.add_argument('--max_num_problems', type=int, default=-1, help='The maximum number of problems to run')
    parser.add_argument('--rerun', action='store_true', help='rerun the evaluation')
    parser.add_argument('--caculate_gain', action='store_true', help='caculate the socre gains over random guess')
    parser.add_argument(
        '--ignore_empty_extractions',
        action='store_true',
        help='Score multiple-choice extractions that give no answer (empty, "N/A", "Cannot be determined", ...) '
        'or an option letter outside the choices as wrong, instead of mapping them to the most similar option',
    )
    parser.add_argument('--random_file', type=str, default='score_random_guess.json')
    # output
    parser.add_argument('--output_dir', type=str, help='Explicit output directory for existing workflows.')
    parser.add_argument('--output_file', type=str, default=config["scoring"]["output_file"])
    parser.add_argument('--score_file', type=str, default=config["scoring"]["score_file"])
    parser.add_argument('--input', help='Read extracted answers from this file and write a scored copy.')
    parser.add_argument('--precheck-only', action='store_true', help='Check one prediction and stop.')
    parser.add_argument('--run-purpose', default='benchmark', help='Descriptive result folder name.')
    args = parser.parse_args(argv)
    return args


def score_problem(problem, answer, ignore_empty_extractions):
    prediction = normalize_extracted_answer(
        problem["extraction"], problem["choices"], problem["question_type"],
        problem["answer_type"], problem["precision"], ignore_empty_extractions,
    )
    return prediction, safe_equal(prediction, answer)


def main(argv=None):
    args = parse_args(argv)
    standard = args.output_dir is None
    if args.output_file == args.score_file:
        raise SystemExit("Use different filenames for predictions and scores.")
    if standard:
        standard_file(args.output_file)
        standard_file(args.score_file)
    effective = {
        "source": args.dataset_name, "split": args.test_split_name,
        "local_file": args.ground_truth_file_path, "input": args.input,
        "max_num_problems": args.max_num_problems,
        "ignore_empty_extractions": args.ignore_empty_extractions,
        "precheck_only": args.precheck_only,
    }
    purpose = "precheck" if args.precheck_only else args.run_purpose
    directory = (result_directory(args.test_split_name, "scoring", purpose)
                 if standard else Path(args.output_dir))
    with run_record(directory, "scoring", args.test_split_name, purpose, effective, standard=standard) as record:
        run(args, directory, record)


def run(args, directory, record):
    logging.info("MathVista: Calculating Scores - Start")
    output_file_path = directory / args.output_file
    results = read_json(args.input or output_file_path)
    test_pids = list(results)
    if args.max_num_problems > 0:
        test_pids = test_pids[:args.max_num_problems]
    if not test_pids:
        raise ValueError("Scoring requires at least one extracted answer.")

    ground_truth_problems = load_split(
        args.dataset_name, args.test_split_name, local_file=args.ground_truth_file_path,
    )

    def answer_for(pid):
        answer = results[pid].get("answer")
        if answer in (None, ""):
            answer = ground_truth_problems[pid].get("answer")
        if answer in (None, ""):
            raise ValueError(f"No answer label is available for problem {pid}.")
        return answer

    def probe():
        pid = test_pids[0]
        prediction, correct = score_problem(results[pid], answer_for(pid), args.ignore_empty_extractions)
        return {"pid": pid, "prediction": prediction, "correct": correct}

    report = check_sample(probe)
    logging.info("Scoring precheck passed for problem %s", report["sample"]["pid"])
    record(report, formal_started=not args.precheck_only)
    if args.precheck_only:
        return

    directory.mkdir(parents=True, exist_ok=True)
    logging.info("Scoring %s problems", len(test_pids))
    update_json_flag = False
    for pid in tqdm(test_pids):
        problem = results[pid]

        if args.rerun:
            if 'prediction' in problem:
                del problem['prediction']
            if 'true_false' in problem:
                del problem['true_false']

        answer = answer_for(pid)
        problem["answer"] = answer
        prediction, true_false = score_problem(problem, answer, args.ignore_empty_extractions)

        # update the problem
        if "true_false" not in problem:
            update_json_flag = True

        elif true_false != problem['true_false']:
            update_json_flag = True

        if "prediction" not in problem:
            update_json_flag = True

        elif prediction != problem['prediction']:
            update_json_flag = True

        problem['prediction'] = prediction
        problem['true_false'] = true_false

    # save the updated json
    if update_json_flag or args.input:
        logging.info("Updating input file with predictions and true_false...")
        save_json(results, output_file_path)
        logging.info(f"Saved {output_file_path}")

    logging.info("Calculate the average accuracy")
    total = len(test_pids)
    correct = 0
    for pid in tqdm(test_pids):
        if results[pid]['true_false']:
            correct += 1

    accuracy = correct / total
    scores = {"average": {"accuracy": accuracy, "correct": correct, "total": total}}

    # [3] Calculate the fine-grained accuracy scores
    # merge the 'metadata' attribute into the data
    rows = [{**results[pid], **results[pid]['metadata']} for pid in test_pids]
    results_df = pd.DataFrame(rows)

    # asign the target keys for evaluation
    target_keys = [
        'question_type',
        'answer_type',
        'language',
        'source',
        'category',
        'task',
        'context',
        'grade',
        'skills',
    ]

    for key in target_keys:
        # get the unique values of the key
        if key == 'skills':
            # the value is a list
            values = sorted({skill for skills in results_df[key] for skill in skills})
        else:
            values = results_df[key].unique()

        # calculate the accuracy for each value
        scores[key] = {}
        for value in values:
            correct, total, acc = get_acc_with_contion(results_df, key, value)
            if total > 0:
                scores[key][value] = {"accuracy": acc, "correct": correct, "total": total}

        # sort the scores by accuracy
        scores[key] = dict(sorted(scores[key].items(), key=lambda item: float(item[1]['accuracy']), reverse=True))

    # [4] Calculate the score gains over random guess
    if args.caculate_gain:
        random_file = directory / args.random_file
        random_scores = json.load(open(random_file))

        logging.info("Calculating the score gains...")
        for key in scores:
            if key == 'average':
                gain = round(float(scores[key]['accuracy']) - float(random_scores[key]['accuracy']), 2)
                scores[key]['acc_gain'] = gain
            else:
                for sub_key in scores[key]:
                    gain = round(
                        float(scores[key][sub_key]['accuracy']) - float(random_scores[key][sub_key]['accuracy']), 2
                    )
                    scores[key][sub_key]['acc_gain'] = str(gain)

    metrics_str = get_full_metrics_str(scores)
    logging.info(metrics_str)

    scores_file_path = directory / args.score_file
    save_json(scores, scores_file_path)

    logging.info(f"Saved scores to: {scores_file_path}")
    logging.info("MathVista: Calculating Scores - Finish")


def get_full_metrics_str(metrics_dict) -> str:
    divider = "=" * 40

    avg_accuracy = metrics_dict["average"]["accuracy"]
    avg_correct = metrics_dict["average"]["correct"]
    avg_total = metrics_dict["average"]["total"]

    metrics_str = f"""
{f"Correct: {avg_correct}/{avg_total} - Accuracy: {avg_accuracy * 100:.2f}%"}
{divider}
""".lstrip()

    for key, item in metrics_dict.items():
        if key == "average":
            continue

        formatted_item_dict = {}
        for sub_key, sub_item in item.items():
            acc = sub_item["accuracy"]
            correct = sub_item["correct"]
            total = sub_item["total"]
            values = [f"{acc * 100:.2f}%", f"({correct}/{total})"]

            formatted_item_dict[sub_key] = values

        category_df = pd.DataFrame(formatted_item_dict, index=["Accuracy", "Correct/Total"])

        metrics_str += f"""
{key}
{divider}
{category_df.T}
"""

    return metrics_str


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
        "filelock",
        "fsspec",
        "msal",
        "msrest",
        "PIL",
        "urllib3",
    ]
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)

    main()
