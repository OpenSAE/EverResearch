# CoTracker model variants

## Purpose and main function

Locate point-tracking networks, predictors, and released checkpoint loaders.

## Scope of application

Use this page when selecting a CoTracker variant or calling the prediction API.

[Predictors and checkpoint selection](../models/tracking/) expose `cotracker.predictor` and `cotracker.models`. The [network implementations](../models/network/) cover CoTracker2 and the CoTracker3 offline and streaming architectures. The [PyTorch model factories](../base/tracking/hub_api.py) preserve the original variant names and checkpoint URLs. The standard tracking CLI uses the scaled offline checkpoint and window length 60.
