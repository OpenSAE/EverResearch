"""Launch the installed DA-2K pairwise scoring workflow.

Use with the project environment active and the official annotated images available locally.
"""

from depth_anything_v2.research.tasks.pairwise_depth.evaluate import main


if __name__ == "__main__":
    main()
