# Datasets

## Image folders

COLMAP reads the immediate files in a scene's `images/` directory in filename order. Viser takes the image directory directly and Gradio stages a user's images or video frames. The public preprocessing functions preserve input order and support aspect-ratio cropping or square padding. Square padding retains original image coordinates for the COLMAP export. The [example media](../assets/examples/) includes single-image scenes, multi-view scenes, and videos.

## Co3D

The default fine-tuning recipe selects Co3D. Set `CO3D_DIR` and `CO3D_ANNOTATION_DIR` in the training and validation sections. The reader uses separate compressed `*_train.jgz` and `*_test.jgz` annotations, then loads the selected views, depths, masks and cameras. The [fine-tuning guide](code/training.md) explains how to select the paths.

## Virtual KITTI 2

The preparation script and [reader](../datasets/virtual_kitti_2/reader/dataset.py) use the Virtual KITTI 2 scene and camera hierarchy. `sequence_list_path` can select separate camera lists for different splits. When omitted, the reader checks the dataset's `sequence_list.txt` and otherwise discovers its camera directories without modifying the input.
