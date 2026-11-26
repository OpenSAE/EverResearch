---
title: CogVideoX-5B
emoji: 🎥
colorFrom: yellow
colorTo: blue
sdk: gradio
sdk_version: 4.42.0
suggested_hardware: a10g-large
suggested_storage: large
app_port: 7860
app_file: scripts/composite_demo/web_demo.py
models:
  - THUDM/CogVideoX-5b
tags:
  - cogvideox
  - video-generation
  - thudm
short_description: Text-to-Video
disable_embedding: false
---

# Gradio Composite Demo

This Gradio demo integrates the CogVideoX-5B model, allowing you to perform video inference directly in your browser. It
supports features like UpScale, RIFE, and other functionalities.

Run the commands below from the repository root.

## Environment Setup

Set the following environment variables in your system:

+ OPENAI_API_KEY = your_api_key
+ OPENAI_BASE_URL= your_base_url
+ GRADIO_TEMP_DIR= gradio_tmp

## Installation

```bash
python -m pip install -r requirements_composite.txt
```

## Running the code

```bash
python scripts/composite_demo/web_demo.py
```
