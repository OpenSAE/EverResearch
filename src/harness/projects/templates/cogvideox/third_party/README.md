# Upstream source used by CogVideoX

## Purpose and main function

Keep code bundled by the original CogVideoX checkout with its Python package names and license files.

## Scope of application

`stability_ai/sgm/` is the SGM tree delivered by CogVideoX for SAT. The build exposes its existing `sgm` imports. `rife/rife/` is the RIFE tree delivered with the composite Gradio demo. The demo imports it to interpolate frames. Update these copies against their upstream sources together with the CogVideoX callers that use them.
