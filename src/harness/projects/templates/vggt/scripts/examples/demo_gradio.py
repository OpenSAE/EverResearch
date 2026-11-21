"""Command-line entry point for the VGGT Gradio application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "base"))
import geometry_runtime

from vggt.demos.gradio_app import (
    clear_fields,
    demo,
    gradio_demo,
    handle_uploads,
    main,
    run_model,
    update_gallery_on_upload,
    update_log,
    update_visualization,
)


if __name__ == "__main__":
    main()
