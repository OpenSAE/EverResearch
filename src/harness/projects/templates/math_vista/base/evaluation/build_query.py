"""Keep the original prompt-building import and module command available."""

import runpy

from mathvista.generation.build_query import *


if __name__ == "__main__":
    runpy.run_module("mathvista.generation.build_query", run_name="__main__")
