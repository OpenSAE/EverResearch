# Model

## Purpose

Note 200 Series of classification models, variants and initialization methods.

## Scope

For the selection of models, for the adjustment of variations or for the interpretation of existing model products.

## Purposes and access

Select the model in the YaML formulation with `--set model=<id>`, see [model registration](../models/plugins.py).

## Shared Parameters

The models receive RGB image batches, output 200 categories are not classified fractions. The selection and proprietary parameters are listed in [parameter](conf.md) (for the configuration file, default value and overwrite rules, the default values and effects of `training.batch_size` can be found).

## Component

### `resnet18_mlp`

Default whole chart classification model. ResNet18 takes the RGB image into a feature vector, then converts it from a multilayer sensor with a width of 256 to 200 class fractions. The current source code starts with random initialization and can be formally trained using CUB data and can be used to check the entry with synthetic images.

Select with `--set model=resnet18_mlp`. Hidden width determines the parameter shape of the header. History ImageNet fine-tunes the current source code and configuration. [formulation specification](../models/residual/residual18/specs.py)] [training record](experiment.md) (for comparison results and limitations based on a real running check, check for random initialization and fine-tuning conditions)

### `resnet18_mlp_small`

Follow the same ResNet18 image feature extracter and change the width of the header to 16. It lowers the amount of parameters and expression capacity of the header, and the output remains the 200-class fraction of the same group. Use `--set model=resnet18_mlp_small` to select the header check point of the original width to be different from the shape of the option. Offline precheck records that this variant has been used. [Proposition specification](../models/residual/residual18/specs.py)] [Exline log](experiment.md)]

### `small_cnn`

- **function**.
- **select method**. `--set model=small_cnn`, randomly initialized by model.
- **Enter and produce**. The RGB batch is quenched by volume and global average and output 200 class fractions.
- **proprietary parameter**. `model.channels` determines the number of volume output channels, default 16.
- **Validation basis**. [Variance statement](../models/convolution/small_cnn/specs.py) and [model achieved](../models/convolution/small_cnn/model.py)].
