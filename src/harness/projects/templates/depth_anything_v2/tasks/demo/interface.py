"""Serve interactive relative depth prediction and downloadable outputs."""

import gradio as gr
import matplotlib
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile
from gradio_imageslider import ImageSlider


css = """
#img-display-container {
    max-height: 100vh;
}
#img-display-input {
    max-height: 80vh;
}
#img-display-output {
    max-height: 80vh;
}
#download {
    height: 62px;
}
"""
title = "# Depth Anything V2"
description = """Official demo for **Depth Anything V2**.
Please refer to our [paper](https://arxiv.org/abs/2406.09414), [project page](https://depth-anything-v2.github.io), or [github](https://github.com/DepthAnything/Depth-Anything-V2) for more details."""


def predict(model, image, output_directory=None):
    if image is None:
        raise ValueError("Select an image for depth prediction.")
    depth = model.infer_image(image[:, :, ::-1])
    if depth.shape != image.shape[:2] or not np.isfinite(depth).all():
        raise ValueError("The depth model returned invalid values or dimensions.")

    low, high = depth.min(), depth.max()
    scaled = ((depth - low) / (high - low) * 255.0).astype(np.uint8) if high > low else np.zeros(depth.shape, np.uint8)
    cmap = matplotlib.colormaps.get_cmap("Spectral_r")
    colored_depth = (cmap(scaled)[:, :, :3] * 255).astype(np.uint8)

    def save(data):
        with tempfile.NamedTemporaryFile(suffix=".png", dir=output_directory, delete=False) as output:
            Image.fromarray(data).save(output, format="PNG")
            return str(Path(output.name))

    return (image, colored_depth), save(scaled), save(depth.astype(np.uint16))


def build_demo(model, examples_root):
    with gr.Blocks() as demo:
        gr.Markdown(title)
        gr.Markdown(description)
        gr.Markdown("### Depth Prediction demo")

        with gr.Row():
            input_image = gr.Image(label="Input Image", type='numpy', elem_id='img-display-input')
            depth_image_slider = ImageSlider(label="Depth Map with Slider View", elem_id='img-display-output', position=0.5)
        submit = gr.Button(value="Compute Depth")
        gray_depth_file = gr.File(label="Grayscale depth map", elem_id="download",)
        raw_file = gr.File(label="16-bit raw output (can be considered as disparity)", elem_id="download",)

        def on_submit(image):
            return predict(model, image)

        submit.click(on_submit, inputs=[input_image], outputs=[depth_image_slider, gray_depth_file, raw_file])

        example_files = [str(path) for path in sorted(examples_root.glob("*.jpg"))]
        gr.Examples(examples=example_files, inputs=[input_image], outputs=[depth_image_slider, gray_depth_file, raw_file], fn=on_submit)

    return demo


def launch(model, examples_root, port=None):
    build_demo(model, examples_root).queue().launch(css=css, server_name="127.0.0.1", server_port=port)
