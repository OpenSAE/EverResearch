# Video and trajectory datasets

## Purpose and main function

Locate the video readers and annotated dataset implementations used by CoTracker.

## Scope of application

Use this page to select data for tracking, evaluation, or training.

The tracking CLI decodes the supplied video with `cotracker.datasets.video`. The default input is the bundled 50-frame apple clip. The [video source directory](../datasets/video_tracking/) also owns the TAP-Vid, Dynamic Replica, Kubric MOVI-f and real-video readers, annotation conversion, and batch collation. See the project README for benchmark sources and the expected directories.
