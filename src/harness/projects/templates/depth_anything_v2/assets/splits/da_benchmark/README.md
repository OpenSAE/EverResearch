# DA-2K inference lists

## Purpose and main function

Select the complete annotated DA-2K image set or its official indoor scenario for the project's image, metric depth, point cloud, and local demo workflows.

## Scope of application

Use these lists on the project machine after extracting the publisher's DA-2K dataset. The entries use absolute paths so the image loader can find each source from another working directory.

- [All annotated images](files/all_images.txt) contains 1,033 original image files across eight scenarios, sorted by the keys in `annotations.json`.
- [Indoor images](files/indoor_images.txt) contains all 195 annotated images in the indoor scenario. The image, metric depth, and point cloud commands consume the image paths. The benchmark scorer reads annotations directly.

The data comes from publisher revision `528f83c`. The downloaded archive's SHA-256 is `ff0e48e7cc53273efd1312610e51f1ec87bea0b8a22daf37125fd81246592b81`. One transparent-reflective image uses UTF-8 bytes without the archive's Unicode flag. The local extraction uses the name in the annotation file, preserving the source image bytes. [Publisher archive](https://huggingface.co/datasets/depth-anything/DA-2K/blob/528f83c/DA-2K.zip)
