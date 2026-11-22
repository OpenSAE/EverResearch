# Research project templates

## Purpose

Browse reusable project source, configuration, and commands. CUB-200 is the default template for ResearchHarness maintenance and central regression tests.

## Scope

Explore a template in this repository or copy its directory to a separate workspace. Follow the project's instructions for installing dependencies and configuring inputs and model weights. Templates include source code, small examples, and experiment configurations. Runs write results to the copied project.

Keep research data and its corresponding preprocessing caches in the shared workspace's `data/`, alongside the research project. When running a template from within ResearchHarness, use the `data/` directory in the parent workspace.

| Template | What it demonstrates |
| --- | --- |
| [CUB-200](cub/README.md) | Bird image classification, configuration, prechecks, and run records |
| [Depth Anything 3](depth_anything_3/README.md) | Depth prediction, camera estimation, and multi-view export |
| [FastVLM](fastvlm/README.md) | Image captioning and visual question answering |
| [FlagEmbedding](flag_embedding/README.md) | Text retrieval and reranking |
| [LightEval](light_eval/README.md) | Language model evaluation and replay of individual scores |
| [LLMLingua](llmlingua/README.md) | Prompt and meeting transcript compression |
| [RF-DETR](rf_detr/README.md) | Object detection and instance segmentation |
| [SAM2](sam2/README.md) | Prompted segmentation and video tracking |
| [VGGT](vggt/README.md) | Depth, camera estimation, and 3D reconstruction |

Each template's `doc/experiment.md` explains where to find run results and how to read them. When connecting a project, select a representative example from its source and documentation and validate it with bounded inputs and available resources.
