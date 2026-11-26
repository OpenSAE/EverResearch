# CogVideoX generation settings

## Purpose and main function

Describe the settings used by the CogVideoX precheck and Diffusers generation command.

## Scope of application

These settings apply to `cogvideo precheck` and `cogvideo generate`. The fine-tuning and SAT settings are documented in their own guides.

[The default configuration](../conf/config.json) selects CogVideoX1.5-5B, text-to-video, 81 frames at 16 fps, 50 denoising steps, bfloat16 and seed 42. The model determines the default frame dimensions. Supply `--config settings.json` to override defaults and use command-line flags for final overrides. You can also pass an effective `config.json` from an earlier managed run.

Use `--generate_type i2v` with an image model and `--image_or_video_path` for image conditioning. Use `--generate_type v2v` with a text/video model and the same media flag for video conditioning. The pipeline applies the model's original resolution rules. The standalone `cogvideo-infer` command retains the default export to `./output.mp4`.

`--num_frames` sets the requested frame count for text-to-video and image-to-video. Video-to-video uses the frame count of the supplied clip. Prepare the clip at the intended frame count before passing it to the command.
