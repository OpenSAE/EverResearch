# Gantry container image

## Purpose and main function

Keep the upstream Gantry image definition used to prepare the evaluation environment.

## Scope of application

Build from the project root with `docker build -f assets/container/gantry/files/Dockerfile` and the CUDA, TARGET, and DIST arguments required by the NVIDIA base image.
