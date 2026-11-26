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

- **Original project** [CogVideoX](https://github.com/THUDM/CogVideo)
- **Source revision** [`7a1af7154511`](https://github.com/THUDM/CogVideo/tree/7a1af7154511e0ce4e4be8d62faa8c5e5a3532d2)
- **Paper** [CogVideoX: Text-to-Video Diffusion Models with an Expert Transformer](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ce31378e9f41d8907e97dab172b6c559-Abstract-Conference.html) · ICLR 2025 Poster
- **Authors** Zhuoyi Yang, Jiayan Teng, Wendi Zheng, Ming Ding, Shiyu Huang, Jiazheng Xu, Yuanming Yang, Wenyi Hong, Xiaohan Zhang, Guanyu Feng, Da Yin, Yuxuan Zhang, Weihan Wang, Yean Cheng, Bin Xu, Xiaotao Gu, Yuxiao Dong, Jie Tang
- **Original source archive** [`cogvideox.zip`](third_party/upstream/cogvideox.zip)
- **Archive SHA-256** `109b478b83229ca2b2b16584b1d392caa524bdcc35561bb5b16b8f4605529b82`

### Before organization

```text
CogVideo/
├── .github/
│   └── ISSUE_TEMPLATE/
├── finetune/
│   ├── configs/
│   ├── datasets/
│   ├── models/
│   ├── schemas/
│   ├── scripts/
│   ├── utils/
│   ├── accelerate_config.yaml
│   ├── constants.py
│   ├── README.md
│   ├── README_ja.md
│   ├── README_zh.md
│   ├── train.py
│   ├── train_ddp_i2v.sh
│   ├── train_ddp_t2v.sh
│   └── … (3 more entries)
├── inference/
│   ├── gradio_composite_demo/
│   ├── cli_demo.py
│   ├── cli_demo_quantization.py
│   ├── cli_vae_demo.py
│   ├── convert_demo.py
│   ├── ddim_inversion.py
│   ├── encoded.pt
│   └── gradio_web_demo.py
├── resources/
│   ├── videos/
│   ├── galary_prompt.md
│   ├── hf_lora_weights.png
│   ├── logo.svg
│   ├── web_demo.png
│   ├── wechat.jpg
│   └── WECHAT.md
├── sat/
│   ├── configs/
│   ├── sgm/
│   ├── vae_modules/
│   ├── arguments.py
│   ├── data_video.py
│   ├── diffusion_video.py
│   ├── dit_video_concat.py
│   ├── finetune_multi_gpus.sh
│   ├── finetune_single_gpu.sh
│   ├── inference.sh
│   ├── README.md
│   ├── README_ja.md
│   ├── README_zh.md
│   ├── requirements.txt
│   └── … (2 more entries)
├── tools/
│   ├── caption/
│   ├── llm_flux_cogvideox/
│   ├── parallel_inference/
│   ├── replicate/
│   ├── venhancer/
│   ├── convert_weight_deepspeed2hf.py
│   ├── convert_weight_sat2hf.py
│   ├── export_sat_lora_weight.py
│   └── load_cogvideox_lora.py
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── MODEL_LICENSE
├── pyproject.toml
├── README.md
├── README_ja.md
├── README_zh.md
└── requirements.txt
```

### After organization

```text
cogvideox/
├── .everresearch/
│   ├── offline/
│   ├── maintain.py
│   └── mode.toml
├── assets/
│   ├── history_experiment/
│   ├── licenses/
│   ├── media/
│   ├── prompts/
│   └── splits/
├── base/
│   ├── cogvideo_runtime/
│   ├── fine_tuning/
│   └── sat_runtime/
├── conf/
│   └── config.json
├── datasets/
│   ├── finetune_video/
│   ├── sat_video/
│   └── video_input/
├── doc/
│   ├── code/
│   ├── environment/
│   ├── experiment/
│   ├── knowledge/
│   ├── conf.md
│   ├── maintenance.md
│   └── README.md
├── models/
│   ├── cogvideo_generation/
│   ├── finetune_video/
│   └── sat_video/
├── scripts/
│   ├── caption/
│   ├── composite_demo/
│   ├── fine_tuning/
│   ├── inference/
│   ├── llm_flux_cogvideox/
│   ├── parallel_inference/
│   ├── replicate/
│   ├── sat_workflows/
│   └── weights/
├── tasks/
│   ├── precheck/
│   ├── sat_video/
│   ├── video_finetuning/
│   └── video_generation/
├── third_party/
│   ├── rife/
│   ├── stability_ai/
│   ├── upstream/
│   └── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements_caption.txt
├── requirements_composite.txt
├── requirements_sat.txt
└── setup.py
```
