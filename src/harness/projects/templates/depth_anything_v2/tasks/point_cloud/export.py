"""Export metric depth as a colored PLY point cloud.

Adapted from the upstream Depth Anything exporter contributed by @1ssb.
"""

import cv2
import numpy as np
import open3d as o3d
from PIL import Image


def predict(args, model, files, output_path):
    # Process each image file
    for k, filename in enumerate(files):
        print(f'Processing {k+1}/{len(files)}: {filename}')

        # Load the image
        color_image = Image.open(filename).convert('RGB')
        width, height = color_image.size

        # Read the image using OpenCV
        image = cv2.imread(str(filename))
        pred = model.infer_image(image, height)

        # Resize depth prediction to match the original image size
        resized_pred = Image.fromarray(pred).resize((width, height), Image.NEAREST)

        # Generate mesh grid and calculate point cloud coordinates
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        x = (x - width / 2) / args.focal_length_x
        y = (y - height / 2) / args.focal_length_y
        z = np.array(resized_pred)
        points = np.stack((np.multiply(x, z), np.multiply(y, z), z), axis=-1).reshape(-1, 3)
        colors = np.array(color_image).reshape(-1, 3) / 255.0

        # Create the point cloud and save it to the output directory
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        path = output_path(filename, k, "point_cloud", ".ply")
        if not o3d.io.write_point_cloud(str(path), pcd):
            raise OSError(f"Cannot write point cloud: {path}")

