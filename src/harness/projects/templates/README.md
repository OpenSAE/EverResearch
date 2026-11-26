# Research project templates

## Purpose and main function

Browse reusable project source, configuration, and commands. CUB-200 is the default template for ResearchHarness maintenance and central regression tests.

## Scope of application

Explore a template in this repository or copy its directory to a separate workspace. Follow the project's instructions for installing dependencies and configuring inputs and model weights. Templates include source code, small examples, and experiment configurations. Runs write results to the copied project.

Keep research data and its corresponding preprocessing caches in the shared workspace's `data/`, alongside the research project. When running a template from within ResearchHarness, use the `data/` directory in the parent workspace.

Each template's `AGENTS.md` identifies the original source, credits the authors,
and shows the top two levels before and after organization. The [template
acceptance standard](../../../../.agents/skills/maintain-skill/references/template-acceptance.md)
describes this section, the archived original source, and the checks for a copied template.

| Template | What it demonstrates | Maintenance |
| --- | --- | --- |
| [CUB-200](cub/README.md) | Bird image classification, configuration, prechecks, and run records | [Maintenance](cub/doc/maintenance.md) |
| [Depth Anything 3](depth_anything_3/README.md) | Depth prediction, camera estimation, and multi-view export | [Maintenance](depth_anything_3/doc/maintenance.md) |
| [FastVLM](fastvlm/README.md) | Image captioning and visual question answering | [Maintenance](fastvlm/doc/maintenance.md) |
| [FlagEmbedding](flag_embedding/README.md) | Text retrieval and reranking | [Maintenance](flag_embedding/doc/maintenance.md) |
| [LightEval](light_eval/README.md) | Language model evaluation and replay of individual scores | [Maintenance](light_eval/doc/maintenance.md) |
| [LLMLingua](llmlingua/README.md) | Prompt and meeting transcript compression | [Maintenance](llmlingua/doc/maintenance.md) |
| [RF-DETR](rf_detr/README.md) | Object detection and instance segmentation | [Maintenance](rf_detr/doc/maintenance.md) |
| [SAM2](sam2/README.md) | Prompted segmentation and video tracking | [Maintenance](sam2/doc/maintenance.md) |
| [VGGT](vggt/README.md) | Depth, camera estimation, and 3D reconstruction | [Maintenance](vggt/doc/maintenance.md) |
| [CogVideoX](cogvideox/README.md) | Text-, image-, and video-conditioned generation | [Maintenance](cogvideox/doc/maintenance.md) |
| [CoTracker3](cotracker/README.md) | Point tracking and video benchmarks | [Maintenance](cotracker/doc/maintenance.md) |
| [Depth Anything V2](depth_anything_v2/README.md) | Relative and metric depth, point clouds, and benchmark scoring | [Maintenance](depth_anything_v2/doc/maintenance.md) |
| [DINOv2](dinov2/README.md) | Self-supervised visual features and dense prediction | [Maintenance](dinov2/doc/maintenance.md) |
| [LeRobot](lerobot/README.md) | Robot imitation learning, simulation, and policy serving | [Maintenance](lerobot/doc/maintenance.md) |
| [Whisper](whisper/README.md) | Speech recognition, translation, and timestamps | [Maintenance](whisper/doc/maintenance.md) |
| [NanoChat](nanochat/README.md) | Tokenizer training and language model pretraining | [Maintenance](nanochat/doc/maintenance.md) |
| [AgentFlow](agentflow/README.md) | Tool-assisted inference, benchmark response replay, and Flow-GRPO training prechecks | [Maintenance](agentflow/doc/maintenance.md) |
| [TRL](trl/README.md) | Language model fine-tuning, preference optimization, and reinforcement learning | [Maintenance](trl/doc/maintenance.md) |
| [Reasoning Gym](reasoning_gym/README.md) | Verifiable reasoning tasks and language model evaluation | [Maintenance](reasoning_gym/doc/maintenance.md) |
| [Ai2 Safety Eval](ai2_safety_eval/README.md) | Model safety classification and refusal evaluation | [Maintenance](ai2_safety_eval/doc/maintenance.md) |
| [MathVista](math_vista/README.md) | Visual mathematical reasoning with local generation and scoring | [Maintenance](math_vista/doc/maintenance.md) |

Each maintenance page records component ownership, verified behavior and the inputs needed for formal runs. Copy the chosen template before installing project dependencies or writing experiment results. Download checkpoints and research data through the project’s documented sources.
