# DINOv2 project guide

## Purpose and main function

Find the local commands, scientific source, and configuration for the DINOv2 checkout.

## Scope of application

Use this page for the installed package, source checkout, and EverResearch maintenance.

- [Installation, hardware and verification](environment/README.md)
- [Formal run choices and timing evidence](maintenance.md)
- [DINOv2 configuration and preset names](conf.md)
- [Original project workflows and weight sources](../README.md)
- [Model card](knowledge/model_card.md)
- [Cell-DINO](knowledge/cell_dino.md) and [Channel-Adaptive DINO](knowledge/channel_adaptive_dino.md)
- [Notebooks](../scripts/notebooks) and [Cell-DINO launch scripts](../scripts/cell_dino)
- [Upstream model and code licenses](../assets/licenses/upstream/README.md)

The application launchers and shared runtime live in [base](../base). [Datasets](../datasets)
contains ImageNet and microscopy readers and transforms. [Models](../models) contains network
architecture and backbone entry points. [Tasks](../tasks) owns training, classification,
dense tasks, and the precheck. The installed package keeps the public `dinov2.*` names.
