# Models and checkpoints

The [model presets](../conf/models/model/config.yaml) describe the
DA3 Small, Base, Large, Giant, Mono, Metric and Nested configurations.
The Python constructor chooses a network architecture by its `model_name`.
`DepthAnything3.from_pretrained` uses the saved model configuration and
weights in the selected local checkpoint or Hub repository.

The depth model combines backbone and prediction heads from
[models/model](../models/model) and [models/backbone](../models/backbone).
The Nested model combines the any-view and metric branches. Streaming loop
detection additionally uses the [SALAD submodule](../third_party/salad).
