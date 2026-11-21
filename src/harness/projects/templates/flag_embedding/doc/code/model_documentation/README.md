# BGE documentation site

This directory contains the Sphinx source and local build entry points for the published BGE documentation. Run these commands from the project root to preview model guides, tutorials, and the installed Python API reference.

```sh
python -m pip install '.[evaluation]' -r doc/code/model_documentation/requirements.txt mteb air-benchmark beir
make -C doc/code/model_documentation html
python -m http.server --directory tmp/documentation_build/.build/html
```

The documentation workflow publishes the HTML build from the master branch.
