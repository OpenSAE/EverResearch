# FlagEmbedding Tests

This directory contains tests for the FlagEmbedding library, including compatibility tests for Transformers 5.x.

## Test Files

- `test_transformers_import_compatibility.py`: Tests that imports work with Transformers v5, particularly the compatibility layer for `is_torch_fx_available`.
- `test_finetune_trainer_compat.py`: Tests the Transformers Trainer API migration, including `processing_class`/legacy `tokenizer` construction, reranker runner arguments, and processor checkpoint saving.
- `test_reranker_tokenizer_compat.py` tests pair preparation and truncation with local tokenizer doubles.
- `test_tokenizer_pad_compat.py` tests normalization of per-example tokenized records before `tokenizer.pad`.
- `test_retrieval_evaluation.py` runs the public custom, BEIR, and BRIGHT evaluation workflows with generated local data and weights. Install the `evaluation` extra and `beir` to run all cases.
- `test_mteb_evaluation.py` checks task-specific examples, fallback instructions, and report generation through the MTEB command using a local benchmark double. Install the `evaluation` extra and `mteb==1.15.0` to run it.
- `integration/` covers public BGE checkpoints and tokenizers. These tests use cached Hub files or download the required files when run online. The tokenizer tests accept `FLAGEMBEDDING_ENCODER_MODEL` and `FLAGEMBEDDING_RERANKER_MODEL` to select local model directories.

## Running Tests

1. create a python venv `python -m venv pytest_venv`
2. activate venv  `source pytest_venv/bin/activate`
3. install pytest `pip install pytest`
4. install flagembedding package in development mode: `pip install -e .`

Then run the tests using pytest:

```bash
# Run all tests
pytest tests/

# Run the software checks without public checkpoints or tokenizers
pytest --ignore=tests/integration

# Run a specific test file
pytest tests/test_transformers_import_compatibility.py

# Run the fine-tuning Trainer compatibility tests
pytest tests/test_finetune_trainer_compat.py

# Run the reranker tokenizer compatibility tests
pytest tests/test_reranker_tokenizer_compat.py

# Run the tokenizer padding compatibility tests
pytest tests/test_tokenizer_pad_compat.py

# Run with verbose output
pytest -v tests/
```

## Transformers 5.x Compatibility

The tests verify that FlagEmbedding works with Transformers 5.x, which removed the `is_torch_fx_available` function and renamed the Trainer `tokenizer` argument to `processing_class`.
The compatibility layer in `base/flag_embedding/compatibility/transformers_compat.py` provides this function for backward compatibility.

**Note:** Transformers 5.0 requires Python 3.10 or higher. If you're using Python 3.9 or lower, you'll need to upgrade your Python version to test with Transformers 5.0.

To test with a specific version of transformers (with Python 3.10+):

```bash
pip install transformers==5.0.0
pytest tests/
