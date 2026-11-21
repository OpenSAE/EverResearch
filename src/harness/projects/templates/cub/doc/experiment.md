# Experimental report

## Purpose

A fixed entry is used to record experimental problems, actual conditions, results and actions that can be taken accordingly.

## Scope

The following example is used to understand the actual experiment of this template, to read the run product and to fill out the follow-up report. The running directory is kept locally by the implementer.

## Offline precheck `offline_check`

1. **Purpose and sentence**. Confirms that small ResNet18 variants complete the training and assessment steps for classification in synthetic samples and write readable precheckbacks.
2. Run **run**. Run `20261119T022754Z-3c5d6f67`, using `synthetic` (8 training, 4 test inputs, random seeds 42), randomly initialized `resnet18_mlp_small`, target mission `classification`. The inventory records CPU, Python 312.15, PyTorch 2.1.0+c128, 0 loading processes and 4 PyTorch lines. The records are `config.yaml` and `metadata/manifest.json` under local `experiment/synthetic/resnet18_mlp_small/precheck/offline_check/20261119T022754Z-3c5d6f67/`.
3. **Status and products**.Inventory records were successful,`reports/precheck.json` Report on training and evaluation of the collection of processing training 2 For each sample, the average crossbow is about... 4.675 and 5.090,Two steps. Top-1 The ratio is both 0.Use it. `python -m cub_template inspect <Run Directory>` Positioning Original Reply.
4. **Conclusions and uses**. The combination delivers a classification chain callback in a recorded CPU environment, which can be used as a basis for offline access.
5. **Limitations and follow-up**.Based on the synthesizing input and boundary steps of the cover. The panorama of a real bird image, GPU Performance and complete training requires evidence of each other's operations.

## CUB-200 from random weight training

1. **Purpose and sentence**. A random initialization baseline for the official bird image classification is measured by the Top-1 accuracy and cross-breathing of the official test set.
2. Run **Runs**. Run `20261119T013844Z-e174778f`. Use 5,994 training, 5,794 test charts, ResNet18 with 256 width headers. Seed 42, training configuration is 30 wheel, batch size 32, study rate 0.001. Environment is CUDA, Python 3.12.15, PyTorch 2.11.0+cu128.
3. **Status and products**.Training and evaluation completed. 5,794 It's a test diagram. Top-1 Yes. 20.76%,Crossing entropy as 3.2604.Configure, list and result location locally `experiment/cub200/resnet18_mlp/classification/scratch_baseline/20261119T013844Z-e174778f/`.
4. **Conclusions and uses**.
5. **Limitations and follow-up**.The result comes from one seed. Compare other training budgets or initializations should record the choice of weights separately.

## CUB-200 ImageNet weight finely

1. **Purpose and judgement**.See if it can be used under the historical micro-alignment. CUB Bird identification weight and higher test accuracy.
2. **Runs**. Runs `20261119T014957Z-b25d7218`. Initializes ResNet18 with ImageNet weights, with a maximum of 24 wheels, 48 batch sizes, 0.0002 for bone study, 0.001 for head learning, with 3 validation maps for each category. Environment is CUDA, Python 3.12.15, PyTorch 2.11.0 + C128.
3. **Status and product**. Done. 79.62% Top-1 for 5,794 official test maps and 1.0764 for cross-mergers. Local configuration, authentication options and weights are stored at `experiment/cub200/resnet18_mlp/classification/imagenet_finetune/20261119T014957Z-b25d7218/`.
4. **Conclusions and uses**.Reviewable final performance of historical fine-tuning and validation options.
5. **Limitations and follow-up**.Changes with the initialization of the random baseline, the training budget and the validation selection. The current template 's default source path uses random initialization, and this historical record needs a source version of the record.
