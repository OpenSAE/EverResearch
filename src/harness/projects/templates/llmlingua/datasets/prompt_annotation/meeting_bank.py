# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

"""Format the MeetingBank training split for the GPT-4 distillation pipeline."""

import argparse
import json
from pathlib import Path

from llmlingua.runtime.config import source_checkout


def main(checkout=None):
    checkout = checkout or source_checkout()
    default_output = (
        checkout / "data/meetingbank/meetingbank_train_formated.json"
        if checkout
        else None
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--save_path",
        type=Path,
        default=default_output,
        required=default_output is None,
    )
    args = parser.parse_args()

    from datasets import load_dataset

    dataset = load_dataset("huuuyeah/meetingbank", split="train")
    data = [
        {"idx": index, "prompt": item["transcript"], "summary": item["summary"]}
        for index, item in enumerate(dataset)
    ]
    args.save_path.parent.mkdir(parents=True, exist_ok=True)
    with args.save_path.open("w", encoding="utf-8") as output:
        json.dump(data, output, indent=4)


if __name__ == "__main__":
    main()
