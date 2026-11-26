# DINOv2 maintenance and formal run choices

## Purpose and main function

Select a complete DINOv2 training, evaluation, or inference workload and read the timings, inputs, and expected outputs for that choice.

## Scope of application

Use this page before allocating GPUs or staging a full dataset for the local DINOv2 checkout. The current calibrations stop at about ten real items or one full configured batch. Each calibration has a five-minute hard limit from process startup through precheck and output, with GPU queue time and data preparation outside the limit. The full workloads below await selection.

Source: [facebookresearch/dinov2@7764ea0f91](https://github.com/facebookresearch/dinov2/tree/7764ea0f912e53c92e82eb78a2a1631e92725fc8). Use the [environment guide](environment/README.md) to choose a local interpreter and acquire the weights and datasets.

## Formal run choices

Reference timings were measured during adoption. Reproduce them with the data, weights, and commands below; run artifacts belong to your copied project.
The local samples use one NVIDIA GeForce RTX 5090 with 32 GB, Python 3.12, PyTorch 2.10.0 with CUDA 12.8, and local storage. Wall times include process startup and the indicated output writes. Dataset and checkpoint transfers are separate. The official cluster timings come from Meta's project documentation. [Environment](environment/README.md) · [Official DINOv2 recipes](../README.md#training)

### ImageNet training and evaluation

| Run | Dataset, weights, and full workload | Evidence and full wall time |
| --- | --- | --- |
| ViT-L/16 self-supervised training | ImageNet-1k TRAIN, 1,281,167 images. Initialize from scratch. 100 scheduled epochs × 1,250 steps, batch 64 per GPU, 10 workers per rank, 32 A100-80GB GPUs over four Slurm nodes. There are 256 million image visits through the infinite sampler, 10 teacher exports, and training state every three epochs plus final. Outputs are loss logs, restart checkpoints, and teacher weights. | Meta reports approximately **1 day** on the specified cluster. The local calibration ran one batch of eight real training records and read back one held-out batch of 25 images. It took **16.7 s** end to end, including both checkpoint writes. The local recipe uses a PyTorch FSDP compatibility guard and a lower initial FP16 loss scale. Short training and validation timing |
| ViT-L/14 self-supervised training | ImageNet-22k TRAIN, approximately 14.2 million images for the full Fall 2011 ImageNet release. Confirm the exact local archive inventory against the dataset reader. Initialize from scratch. 500 scheduled epochs × 1,250 steps, batch 32 per GPU, 10 workers per rank, 96 A100-80GB GPUs over 12 Slurm nodes. The 625,000 steps use 1.92 billion image visits, with 50 teacher exports and regular restart checkpoints. | Meta reports approximately **3.3 days** on the stated cluster. This machine has one GPU, lacks Slurm, and has no compatible staged ImageNet-22k TAR inventory. The measured ViT-L/16 steps provide a separate local reference. Calibrate one global batch at 32 per rank on the assigned cluster with this reader, teacher export, and held-out readback within the five-minute cap. Record partial progress if the first unit exceeds the cap. [ImageNet release information](https://image-net.org/download.php) |
| Frozen-feature k-NN | Official ViT-S/14 distilled backbone, ImageNet-1k TRAIN and VAL, 1,281,167 reference features and 50,000 queries. One feature pass per split at 224 pixels, batch 25, five loader workers. Reports top-1 and top-5 at 10, 20, and 100 neighbours. | **4.1 s** for one full batch per split (25 training and 25 validation images), including 3.2 s outside the two loops. **55 min–8 h** as a provisional planning range.  |
| Train linear classifiers | Official ViT-S/14 distilled backbone, same train and validation populations. Frozen backbone, random spatial training augmentations, four feature and pooling variants and 13 requested learning rates, 10 epochs of 1,250 steps, batch 25 and four workers. 312,500 training visits and 10 validation passes of 50,000 images. Writes validation scores, winner, and classifier checkpoints. | **5.2 s** for one 25-image training batch and one 25-image validation batch using 1,000-output heads. Includes a 387 MiB checkpoint. **40 min–4 h** as a provisional planning range.  |
| Fit logistic classifiers | Official ViT-S/14 distilled backbone, same train and validation populations. Extract 224-pixel features once per split, batch 256 with zero loader workers. Use 45 strengths on 90% of training features for model selection on the other 10%, followed by one refit on all train features and a final validation pass. The cuML solver runs up to 1,000 iterations per fit. Writes top-1/top-5 and selected regularization to the run log. | The original environment lists cuML for CUDA 11. The available CUDA 12 distribution requires replacement versions of the pinned CUDA and scientific packages, so use an isolated RAPIDS runtime for the official fitter. The matching ViT-S/14 feature pipeline and the 45-candidate workflow used a scikit-learn CPU fitter on ten training and ten validation images in **5.5 s**. Each split supplied one partial batch because the formal size is 256. A formal cuML end-to-end estimate requires that environment and measurements at larger row and class counts. Short diagnostic |
| Evaluate the released linear head | Official ViT-S/14 and four-layer ImageNet classifier, all 50,000 validation images once, 224 pixels, batch 25, four workers. Writes top-1/top-5 and prediction scores per image. | **2.5 s** for one full batch of 25 original ImageNet validation images. Startup took 1.65 s and the first batch took 0.39 s with worker startup and writes. **2–14 min** as a provisional planning range.  |
| dino.txt zero-shot classification | Official ViT-L/14 with registers, vision head, and text encoder. Build 1,000 text embeddings with the fixed prompt `a photo of a {class}.`, then score all 50,000 ImageNet-1k validation images at 224 pixels, batch 25 and four workers. Writes class rankings and top-1/top-5. The single-prompt recipe has a different cost from the notebook's prompt ensemble. | **13.7 s** for one full 25-image batch and all 1,000 text prompts. Model initialization and prompt encoding took 12.8 s, followed by the 0.41 s first image batch. **3–15 min** as a provisional planning range.  |

The prescribed self-supervised loops export teacher weights during training. Quality evaluation runs separately using a teacher export and the matching configuration. The one-GPU profile includes a held-out teacher readback. Use the released ViT-S/14 for the frozen-feature rows unless the goal is to evaluate a newly trained teacher.

The one-GPU calibration reached the training batch after 6.65 s and completed its optimizer update at 7.82 s. The two 6.1 GiB total checkpoint writes took 2.79 s. The held-out pass took 5.05 s including the teacher load. A local batch-8 run of 125,000 steps would visit 1,000,000 images. Allow **8–42 hours** provisionally, assuming about 0.23 s per step in the lower planning scenario or 1.17 s per step at the measured cold compute cost, plus periodic checkpoint I/O. This leaves the sustained optimizer rate to calibrate. The short run used an initial loss scale of 1,024 after the default scale skipped the optimizer update on the cold batch. The official cluster recipe and its runtime reference use Meta's configuration.

The full ImageNet files need to be staged with their official split and metadata. The CPU metadata writer processed samples of ten train and ten validation records in 1.0 and 0.8 ms respectively, after process startup and sample copying. The measured command took 1.7 s including preparation. It reads the filenames and labels and produces six NumPy index files for those splits. Allow approximately 1–4 minutes for the full 1,331,167 indexed records on local storage, with storage traversal and class-name widths as the main variables. The index writer uses no model. [Metadata generation](../README.md#imagenet-1k) The Hugging Face publisher file endpoint returned HTTP 401 and the original ImageNet HTTPS archive route did not connect. The local samples use ImageNet source records from Imagenette and a public 100-row ImageNet training sample. Only original `ILSVRC2012_val_*.JPEG` records from the Imagenette validation folder count as validation images because its folder also includes images originating from the ImageNet training set. [ImageNet publisher split](https://huggingface.co/datasets/ILSVRC/imagenet-1k) · [Imagenette publisher](https://github.com/fastai/imagenette)

### Dense prediction

| Run | Dataset, weights, and full workload | Evidence and full wall time |
| --- | --- | --- |
| Indoor metric depth | 654 NYU Depth V2 test RGB/depth pairs, 640 × 480. Official ViT-S/14 plus NYU four-layer head. Batch one, zero loader workers, original and horizontal-flip inference per image, 0.001–10 m. Writes 654 float32 depth maps, about 0.8 GB, and mean per-image RMSE on the Eigen crop. | **2.7 s** for ten evenly spaced pairs, including 1.78 s setup and all depth-array writes. Images two through ten averaged 0.027 s each. **18–30 s** for the full split.  · [Dataset release](https://cs.nyu.edu/~fergus/datasets/nyu_depth_v2.html) · [Prepared split mirror](https://huggingface.co/datasets/vikhyatk/nyu_depth_v2) |
| Semantic segmentation | 2,000 ADE20K validation image/annotation pairs, official ViT-S/14 and ADE20K linear head, one image at a time. Resize the shorter side to 512, use 512 × 512 windows at stride 341, average overlap logits, and resize to native size. Writes 2,000 indexed PNG masks and class mIoU. | **2.4 s** for ten validation pairs, including 1.56 s setup and all mask writes. Images two through ten averaged 0.019 s each. **32–60 s** for the full split.  · [ADE20K publisher](https://groups.csail.mit.edu/vision/datasets/ADE20K/) |
| Mask2Former segmentation | Same ADE20K validation split, official ViT-g/14 Mask2Former checkpoint, one image at a time using Meta's 2,048 × 512 resize bound and multiples of 32. Produces 150-class masks for the 2,000 images and mIoU if joined to labels. | The official checkpoint URL responded to an HTTP range check and reports an 11.55 GB download. The legacy MMSegmentation stack requires compiled MMCV extensions. The installed pure Python MMCV 1.5 raises `ModuleNotFoundError: mmcv._ext` at import on this machine. On an allocated A100 with the original compatible CUDA/PyTorch environment, measure ten evenly spaced validation images and mask writes within five minutes. The measured linear-head runtime applies to that distinct model. |

### Microscopy and radiograph features

| Run | Dataset, weights, and full workload | Evidence and full wall time |
| --- | --- | --- |
| Cell-DINO self-supervised training | Human Protein Atlas HPAone ALL with 839,612 varied-size single-cell index rows. ViT-L/16 from scratch, 100 scheduled epochs × 1,756 optimizer batches, 16 images per GPU, 10 workers per rank, 32 A100-80GB GPUs. 89,907,200 image visits and a teacher export every 9,000 steps. Writes loss, restart checkpoints and teacher weights. | The publisher recipe reports approximately **2 days**. There is no matching cluster allocated here. The BioImage Archive's public file list contains the varied-size index, while the complete varied-size image tree required by the data reader was unavailable locally. [Cell-DINO recipe](knowledge/cell_dino.md#training) · [BioImage Archive](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2443) |
| Cell-DINO k-NN | HPAone TRAIN and VAL in cell-line mode with 570,401 reference images and 96,062 validation images, official HPA single-cell ViT-L/16. One feature pass per split at crop 384, batch 256 and five workers, followed by a one-neighbour lookup on the complete reference bank. Writes validation macro-F1. | Timings need the researcher-approved Meta checkpoint and image data. BioImage Archive lists the fixed-size image archive at 218.5 GB. The independently retrieved publisher CSVs supplied both split counts. [Meta weight request](https://ai.meta.com/resources/models-and-libraries/cell-dino-downloads/) · [HPA evaluation recipe](knowledge/cell_dino.md#evaluation) |
| Cell-DINO linear probe | Same HPAone splits (570,401 training and 96,062 validation images) and weights, protein localization with a multilabel linear classifier and macro-F1. Batch 64, eight workers, 30 × 145 steps, 278,400 training visits and four full validation passes. Saves classifier state and scores. | Same input and checkpoint dependencies as cell k-NN. Calibrate one labelled train batch and one validation batch at batch 64 with the same channel counts and crop settings within five minutes. [HPA evaluation recipe](knowledge/cell_dino.md#evaluation) |
| Cell-DINO embedding demonstration | HPA single-cell ViT-L/16 and the three publisher microscopy examples, one image at a time. Produces the notebook's image and patch embeddings and visualizations. | A complete run uses all three images when a licensed weight file and the notebook images are available. [Embedding notebook](../scripts/notebooks/cell_dino/inference.ipynb) |
| XRay-DINO research embeddings | Meta XRay-DINO ViT-L/16 with its released checkpoint. A complete candidate workload uses the 25,596 NIH ChestX-ray14 test radiographs and saves one feature row per image. | The temporary checkpoint download URL is issued by Meta after access approval. With the approved checkpoint, run about ten patient-distributed test images or one full batch within five minutes using the same intended batch, decoding, and feature writer to establish a full-pass estimate. [Meta weight request](https://ai.meta.com/resources/models-and-libraries/raydino-downloads/) · [NIH data release](https://nihcc.app.box.com/v/ChestXray-NIHCC) |

### Start a selected run

Activate the project environment and set the data and output variables to the paths for one chosen run. `WEIGHTS` names a `checkpoints` directory containing the original Meta filenames. `OUT` names a new writable output directory. All commands run from the project root. For the submitted jobs, set `DINO_SLURM_PARTITION` to the allocated partition and use an output path on the cluster shared filesystem. The longer timeouts require partition limits that cover the full job. [Environment](environment/README.md)

The existing quick precheck takes one optional image and verifies a finite untrained ViT-S/14 feature. The classification commands use the official model files and dataset metadata.

```bash
XFORMERS_DISABLED=1 python main.py precheck --image "$EXAMPLE_IMAGE"

train="ImageNet:split=TRAIN:root=$IMAGENET:extra=$IMAGENET_EXTRA"
val="ImageNet:split=VAL:root=$IMAGENET:extra=$IMAGENET_EXTRA"
backbone="$WEIGHTS/dinov2_vits14_pretrain.pth"

python main.py train --nodes 4 --ngpus 8 --partition "$DINO_SLURM_PARTITION" --config-file train/vitl16_short \
  --output-dir "$OUT" "train.dataset_path=$train"
python main.py train --nodes 12 --ngpus 8 --partition "$DINO_SLURM_PARTITION" --timeout 7200 --config-file train/vitl14 \
  --output-dir "$OUT" "train.dataset_path=ImageNet22k:root=$IMAGENET_LARGE:extra=$IMAGENET_LARGE_EXTRA"

XFORMERS_DISABLED=1 python -m dinov2.eval.knn --config-file eval/vits14_pretrain \
  --pretrained-weights "$backbone" --output-dir "$OUT" \
  --train-dataset "$train" --val-dataset "$val" --batch-size 25 --nb_knn 10 20 100
XFORMERS_DISABLED=1 python -m dinov2.eval.linear --config-file eval/vits14_pretrain \
  --pretrained-weights "$backbone" --output-dir "$OUT" \
  --train-dataset "$train" --val-dataset "$val" --batch-size 25 --num-workers 4
XFORMERS_DISABLED=1 python -m dinov2.eval.log_regression --config-file eval/vits14_pretrain \
  --pretrained-weights "$backbone" --output-dir "$OUT" \
  --train-dataset "$train" --val-dataset "$val"

XFORMERS_DISABLED=1 python scripts/evaluate_image_classifiers.py linear \
  --root "$IMAGENET" --extra "$IMAGENET_EXTRA" --weights "$WEIGHTS" --batch-size 25 --workers 4 --output "$OUT"
XFORMERS_DISABLED=1 python scripts/evaluate_image_classifiers.py text \
  --root "$IMAGENET" --extra "$IMAGENET_EXTRA" --weights "$WEIGHTS" --batch-size 25 --workers 4 --output "$OUT"
XFORMERS_DISABLED=1 python scripts/evaluate_visual_heads.py depth \
  --dataset-root "$NYU" --weights "$WEIGHTS" --output "$OUT"
XFORMERS_DISABLED=1 python scripts/evaluate_visual_heads.py semantic \
  --dataset-root "$ADE" --weights "$WEIGHTS" --output "$OUT"
```

Use the NYU staging layout `rgb/<name>.png` and `depth/<name>.npy` with depth in metres. ADE uses `images/validation` and `annotations/validation` from the publisher archive. For Mask2Former, open the [semantic segmentation notebook](../scripts/notebooks/semantic_segmentation.ipynb) in the compatible environment, load the official ViT-g/14 Mask2Former configuration and checkpoint, and run its inference over the ADE20K validation directory. Preserve the original image names for the mask-to-label join.

```bash
hpa_train="HPAone:split=TRAIN:mode=PROTEIN_LOCALIZATION:root=$HPA"
hpa_val="HPAone:split=VAL:mode=PROTEIN_LOCALIZATION:root=$HPA"

python main.py train --nodes 4 --ngpus 8 --partition "$DINO_SLURM_PARTITION" --timeout 3600 --config-file train/cell_dino/vitl16_hpaone \
  --output-dir "$OUT" "train.dataset_path=HPAone:split=ALL:root=$HPA"
python main.py cell-linear --nodes 1 --ngpus 1 --partition "$DINO_SLURM_PARTITION" --config-file eval/cell_dino/vitl16_pretrain \
  --pretrained-weights "$CELL_CHECKPOINT" --output-dir "$OUT" \
  --train-dataset "$hpa_train" --val-dataset "$hpa_val" --val-metric-type mean_per_class_multilabel_f1 \
  --loss-type binary_cross_entropy --avgpool
python main.py cell-knn --nodes 1 --ngpus 1 --partition "$DINO_SLURM_PARTITION" --config-file eval/cell_dino/vitl16_pretrain \
  --pretrained-weights "$CELL_CHECKPOINT" --output-dir "$OUT" \
  --train-dataset "HPAone:split=TRAIN:mode=CELL_TYPE:root=$HPA" \
  --val-dataset "HPAone:split=VAL:mode=CELL_TYPE:root=$HPA" \
  --metric-type mean_per_class_multiclass_f1 --crop-size 384 --batch-size 256 --resize-size 0 --nb_knn 1
```

The CHAMMI launchers use the same cell evaluation tasks for their separate benchmarks. [CHAMMI launcher settings](../scripts/cell_dino)

For microscopy embeddings, follow the local [Cell-DINO notebook](../scripts/notebooks/cell_dino/inference.ipynb) with its licensed checkpoint and three images. The XRay-DINO constructor is `torch.hub.load("third_party/pytorch_hub", "xray_dino_vitl16", source="local", weights=checkpoint)`. Prepare the NIH patient-separated test list and use the preprocessing supplied with the approved checkpoint. The model uses 512-pixel input and 16-pixel patches. Calibrate at a fixed batch size before choosing the full run. [XRay-DINO model definition](../README.md#pretrained-backbone-xray-dino)

### Sample evidence

Example relative locations under a user-selected `DINO_DATA_ROOT` are `${DINO_DATA_ROOT}/nyu_timing` and `${DINO_DATA_ROOT}/ade_timing/ADEChallengeData2016`. NYU preparation read three split files totaling 1.04 GB. ADE validation came from the 967 MB official challenge archive. The dino.txt model components total 3.47 GB. The observed transfers for ADE and dino.txt each took roughly 8–11 minutes at the shared link's recorded load. Those preparation times are outside the timed task runs. Reuse a verified local weight cache.

The short ImageNet samples use real records selected by synset. The local timing wrapper relaxes the dataset length assertion for sample indexes and the full commands use the standard reader. The ImageNet training pictures for the probes came from the 320-pixel Imagenette release and follow the project's 224-pixel transforms. Mask and depth outputs were reopened and checked against the requested sample size.

The ImageNet classifier projections use one full batch per split. A single batch measures startup and the first batch cost. A sustained batch rate remains unobserved. The estimates allow for overlap of decoding and GPU work in the lower planning scenario, and use repeated cold-batch costs to represent the high planning scenario. Exported predictions follow validation index order.

- **k-NN.** One reference batch took 0.527 s, including first-batch dataloading and feature collection, and the validation loop took 0.335 s. A 25-record real reference set supports the 10- and 20-neighbour sample scores. A separate one-batch control used 25 real queries and a seeded random reference bank of the full 1,281,167-vector dimensions. It timed the 100-neighbour retrieval path at 0.063 s for that first search. The complete job has 51,247 reference batches and 2,000 query batches. The planning range uses roughly 0.06–0.53 s per reference batch including data I/O and budgets full-size lookup on validation. The bank control measures compute cost only. Runtime and control
- **Linear probe.** One training batch took 0.522 s including the checkpoint and one validation batch took 0.362 s. The complete recipe has 12,500 optimizer batches, 20,000 validation batches and scheduled checkpoint writes. The lower planning scenario uses about 0.08 s per training batch and 0.06 s for validation with overlap. At batch 25 the three smallest scaled learning rates share a formatted name and yield 44 live classifiers across four variants. The calibration retained all 1,000 output dimensions while using images from ten synsets. 
- **Released linear head and dino.txt.** Full predictions use 2,000 batches. The lower planning scenarios use about 0.06 s per linear-head batch and 0.08 s per dino.txt image batch with persistent workers and overlapped data loading. For dino.txt, the initialization and prompt-encoding stage is charged once. The released-linear head has no prompt stage. Released head timing · dino.txt timing

The earlier profiles of roughly 100 images per split are retained as historical comparisons. Training · k-NN · Linear probe · Logistic diagnostic · Released head · dino.txt · Depth · Segmentation
