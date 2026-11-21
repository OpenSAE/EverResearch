# Image inputs

## Use and entry point

The PyTorch inference task reads one user-supplied image selected with `--image-file`. Use a local file recognized by Pillow. The task needs neither labels nor split metadata. [Configuration](conf.md)

## Shared parameters

The caller's working directory is the base for relative image paths. The [image reader](../datasets/user_image/__init__.py) hashes the original bytes with SHA-256, records the original width and height, and supplies an RGB image. The inference task uses the checkpoint's image processor and passes the original size to the model. [Task contract](tasks.md)

## Inputs used by project workflows

- `user_image` is the source name for one-off images. Use `--dataset` to record an identifiable collection, such as `coco_val` for COCO validation images. The image remains selected by `--image-file`. The path, digest and original size are recorded with the answer. The same path can be reused for a new image while the digest distinguishes the two samples. [Input and result mapping](experiment.md)
- `assets/examples/serving/files/` contains two bundled images used by Gradio examples. The examples serve as manual inputs. [Gradio entry point](../tasks/serve/gradio_web_server.py)
- The training launchers share the supervised data reader. Each `--data_path` entry selects an external JSON conversation shard. Image names in a shard resolve relative to its corresponding `--image_folder` entry. The experiment owner supplies the upstream training recipe and split policies. [Supervised data reader](../datasets/supervised/__init__.py) [Inherited training code](../tasks/train/train.py)
