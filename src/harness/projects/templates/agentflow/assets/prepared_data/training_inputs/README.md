# Generated Flow-GRPO inputs

## Purpose and main function

Provide a destination for the training and validation Parquet files generated from public datasets.

## Scope of application

The [dataset preparation scripts](../../../datasets/preparation) write these files.
The Flow-GRPO configuration reads them by default. Set `BASE_DATA_DIR` to reuse prepared files
from another location.

The verified preparation used the following Hugging Face snapshots. The scripts preserve
the original split choices and use seed 42 for shuffling before reindexing the rows.

| Input | Revision | Selected rows |
| --- | --- | ---: |
| Natural Questions from FlashRAG, `nq/train` | `bcafb8dd07d453be3cbeeeb3f78be1841bddf92c` | 79,168 |
| DeepMath-103K, `train` | `5cf055d1fe3d7a2eb19719ac020211469736ae44` | 103,022 |
| AIME 2024, `train` used for validation | `8d88b2876a82a080e2f172cc9b25d0d9d2cb4792` | 30 |

The prepared files are `files/train/combined_train.parquet` with 182,190 rows and
`files/val/aime24.parquet` with 30 rows.
