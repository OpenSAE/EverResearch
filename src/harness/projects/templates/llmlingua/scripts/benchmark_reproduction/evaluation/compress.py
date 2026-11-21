# Copyright (c) 2023 Microsoft
# Licensed under The MIT License [see LICENSE for details]

"""Keep the published evaluation compression command available."""

from llmlingua.runtime.compression import legacy_main

if __name__ == "__main__":
    legacy_main()
