# SAM 2 maintenance and local verification

## Purpose and main function

Record how image and video segmentation, prechecks and evaluation were verified.

## Scope of application

Use when preparing SAM 2 weights and images or videos and checking the results.

The reference checkout retained the notebook images, and the moved truck image matched the original SHA-256. The [archived experiment](../assets/history_experiment/point_prompt/README.md) describes the original run.

| Responsibility | Source and verification |
| --- | --- |
| Runtime | [Checkout commands](../main.py) load configurations through [the compatibility mapping](../base/segment_anything/imports.py). Tested source invocation and legacy package imports from outside the checkout. |
| Datasets | [RGB reader](../datasets/notebook_images/source.py) decoded a synthetic image. [Video and annotation readers](datasets.md) preserve the published formats. A three-frame synthetic clip passed the prediction and scoring chain. |
| Models | [Builder](../models/segment_anything/build.py) and [packaged recipes](../conf/models/segment_anything/config.yaml) preserve released model and configuration names. A SAM 2.1 Hiera Tiny model with zero-valued synthetic weights ran on CPU for images and CUDA for VOS. |
| Tasks | Image, video, evaluation, training and benchmarking implementations live in [tasks](tasks.md). An out-of-bounds click was rejected before image model construction. Video, evaluation and training launchers check their input paths. |
| Configuration | [Configuration guide](conf.md) documents defaults and Hydra keys. Tests cover all eight inference recipes, historical names and resolved MOSE launcher overrides. |
| Experiments | The image command wrote and read its prediction, effective settings and precheck reports. Central experiment and precheck checks covered the run records. Video and evaluation commands used explicit legacy output locations. |
| Supporting materials | [Environment](environment/README.md), [examples](tasks.md) and [Docker demo instructions](../third_party/meta_web_demo/README.md) use the new paths. The CUDA-disabled wheel built from local sources and retained the old Python imports and recipes. |

The current machine lacks the official Hiera Large checkpoint that the old checkout links to, and the MOSE image and annotation roots are unset. The synthetic runs establish runtime, I/O and task integration. The previous Hiera Large runs are available in the archive as historical evidence. Docker was unavailable for the demo check.

## Local installation and commands

The editable SAM-2 package was refreshed from the local checkout in an isolated interpreter with existing build tools and dependencies. From `/tmp`, its original image and training module commands both resolved to the maintained checkout. A CUDA test on the GeForce RTX 5090 used the original connected-components binary byte for byte and returned area four for a four-pixel connected region. [Local installation backup](../tmp/editable_restore/README.md)

The official checkout image command used the registered input path and returned the expected 16 × 12 synthetic mask through the normal result reader. A previous prediction was also opened through the installed command, returning three masks at 1800 × 1200. The current regression suite passed all 11 tests. The central project check reported zero layout violations and the experiment check reported zero violations across four runs. The central precheck check confirmed one sampled image on the successful execution and confirmed that the invalid prompt blocked formal computation.

## Verify a copied template

Follow the [environment and resource guide](environment/README.md). Run `python -IS .everresearch/maintain.py check` in the project root. Then use the documented entry point with a small representative input and read back its output. The evidence above describes the reference checks. Measure throughput on the intended model, inputs and hardware before estimating a complete run.
