# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

"""Launch the packaged meeting bank implementation."""

from pathlib import Path

from llmlingua.datasets.annotation.meeting_bank import main


if __name__ == "__main__":
    main(checkout=Path(__file__).resolve().parents[3])
