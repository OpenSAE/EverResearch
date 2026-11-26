# Whisper runtime tables

## Purpose and main function

Preserve the Mel filter matrix, tokenizer vocabularies, and English spelling normalization table used by Whisper.

## Scope of application

The audio implementation loads the Mel filters, the tokenizer loads the vocabulary for the selected model, and the English normalizer loads its spelling map. These files came from the original `whisper/assets/` and `whisper/normalizers/` directories. The package includes the original tables as runtime resources.
