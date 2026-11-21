# FastVLM code and interfaces

The checkout command `python main.py` and the installed command `fastvlm` call the same parser and runtime. Use `--show-config` to inspect values and `--read-result` to inspect a prediction.

```mermaid
flowchart TD
    Command["base/fast_vlm/commands.py"] --> Runtime["base/fast_vlm/runtime.py"]
    Runtime --> Precheck["tasks/precheck"]
    Precheck --> Image["datasets/user_image"]
    Precheck --> Model["models/fast_vision"]
    Model --> Builder["models/model/builder.py"]
    Precheck --> Task["tasks/image_prompt"]
    Runtime --> Task
    Runtime --> Results["base/fast_vlm/records.py"]
```

Setuptools maps the source directories to the established `fastvlm`, `llava` and `model_export` import names. The Apple application retains Apple's Xcode project and camera layout. [Package mapping](../../pyproject.toml) [Xcode demo](../../third_party/apple_demo/README.md) [Export](apple_silicon/README.md)
