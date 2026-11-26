<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.everresearch/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.everresearch/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .everresearch/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .everresearch/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [MathVista](https://github.com/lupantech/MathVista)
- **Source revision** [`24b1478132e9`](https://github.com/lupantech/MathVista/tree/24b1478132e9bb6d32880ebf68ce57b7a0df92b5)
- **Paper** [MathVista: Evaluating Mathematical Reasoning of Foundation Models in Visual Contexts](https://proceedings.iclr.cc/paper_files/paper/2024/hash/663bce02a0050c4a11f1eb8a7f1429d3-Abstract-Conference.html) · [ICLR 2024 Oral](https://iclr.cc/media/iclr-2024/Slides/18900.pdf)
- **Authors** Pan Lu, Hritik Bansal, Tony Xia, Jiacheng Liu, Chunyuan Li, Hannaneh Hajishirzi, Hao Cheng, Kai-Wei Chang, Michel Galley, Jianfeng Gao
- **Original source archive** [math_vista.zip](third_party/upstream/math_vista.zip)
- **Archive SHA-256** `8038f10667205633cc6e14333171af67c915288ea29eb328964f1295c2fc653f`

### Before organization

```text
MathVista/
├── .devcontainer/
│   ├── Dockerfile
│   ├── devcontainer.env
│   ├── devcontainer.json
│   └── postCreateCommand.sh
├── .editorconfig
├── .flake8
├── .gitattributes
├── .github/
│   └── dependabot.yml
├── .gitignore
├── .vscode/
│   └── launch.json
├── LICENSE
├── README.md
├── assets/
│   ├── DALL·E 2023-10-25 14.09.24 - Photo-based logo with a delicate gradient transitioning from soft blue to a lighter hue. The word 'MathVista' is written across the gradient in a mode copy.png
│   ├── contexts/
│   ├── data-composition.png
│   ├── data_visualizer.png
│   ├── logo_v1.png
│   ├── mathvista.png
│   ├── our_new_3_datasets.png
│   ├── result-scores.png
│   ├── results_examples/
│   ├── results_figures/
│   ├── score_leaderboard_gpt4v.png
│   ├── skills/
│   ├── source_dataset.png
│   ├── statistics/
│   ├── statistics.png
│   ├── tease_scores_gpt4v.png
│   └── tease_scores_version4_gemini.png
├── data/
│   ├── annot_testmini.json
│   ├── query.json
│   ├── source.json
│   ├── test.json
│   ├── testmini.json
│   └── texts/
├── data_prepro/
│   ├── generate_caption_bard.py
│   ├── generate_caption_vitgpt2.py
│   ├── generate_text_easyocr.py
│   └── run_bard.sh
├── evaluation/
│   ├── build_query.py
│   ├── calculate_score.py
│   ├── extract_answer.py
│   ├── generate_response.py
│   └── prompts/
├── jupyter_notebook_demos/
│   ├── bard_local_demo.ipynb
│   └── hugging_face_dataset_demo.ipynb
├── models/
│   ├── bard.py
│   ├── claude.py
│   └── gpt.py
├── pyproject.toml
├── requirements.txt
├── results/
│   ├── bard/
│   ├── chatgpt/
│   ├── claude/
│   ├── gpt4/
│   ├── gpt4v/
│   ├── idefics/
│   ├── instruct_blip2/
│   ├── leaderboad_submission_template/
│   ├── llama_adapter_v2/
│   ├── llava/
│   ├── llavar/
│   ├── minigpt4/
│   ├── mplugowl/
│   ├── random/
│   └── test_random/
├── scripts/
│   ├── run_bard.sh
│   ├── run_chatgpt.sh
│   ├── run_chatgpt_2shot_code.sh
│   ├── run_chatgpt_2shot_code_use_caption_ocr.sh
│   ├── run_chatgpt_2shot_solution.sh
│   ├── run_chatgpt_2shot_solution_use_caption_ocr.sh
│   ├── run_claude.sh
│   ├── run_claude_2shot_solution.sh
│   ├── run_claude_2shot_solution_use_caption_ocr.sh
│   ├── run_gpt4.sh
│   ├── run_gpt4_2shot_code.sh
│   ├── run_gpt4_2shot_code_use_caption_ocr.sh
│   ├── run_gpt4_2shot_solution.sh
│   ├── run_gpt4_2shot_solution_use_caption_ocr.sh
│   ├── run_idefics.sh
│   ├── run_instruct_blip2.sh
│   ├── run_llama_adapter_v2.sh
│   ├── run_llava.sh
│   ├── run_llavar.sh
│   ├── run_minigpt4.sh
│   ├── run_mplugowl.sh
│   ├── run_test_gpt4_2shot_code_use_caption_ocr.sh
│   ├── run_test_gpt4_2shot_solution_use_caption_ocr.sh
│   └── run_test_llava.sh
├── tests/
│   └── test_compatibility.py
└── utilities.py
```

### After organization

```text
math_vista/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── LICENSE
├── README.md
├── assets/
│   ├── figures/
│   ├── history_experiment/
│   └── prepared_data/
├── base/
│   ├── evaluation/
│   ├── math_vista/
│   └── utilities.py
├── conf/
│   └── config.toml
├── datasets/
│   └── math_vista/
├── doc/
│   ├── README.md
│   ├── environment/
│   ├── experiment.md
│   ├── maintenance.md
│   └── tasks.md
├── main.py
├── models/
│   ├── __init__.py
│   ├── anthropic_client/
│   ├── bard/
│   ├── build.py
│   ├── openai_client/
│   └── qwen_vision/
├── pyproject.toml
├── requirements.txt
├── scripts/
│   ├── generation/
│   ├── notebooks/
│   └── published/
├── setup.py
├── tasks/
│   ├── extraction/
│   ├── generation/
│   ├── precheck/
│   └── scoring/
├── tests/
│   └── test_compatibility.py
└── third_party/
    └── upstream/
        └── math_vista.zip
```
