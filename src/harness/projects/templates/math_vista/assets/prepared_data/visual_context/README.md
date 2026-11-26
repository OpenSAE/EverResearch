# Captions and recognized text

## Purpose and main function

These JSON files supply optional image captions and EasyOCR text to the MathVista
prompt builder.

## Scope of application

The files come from the original MathVista repository's `data/texts/` at revision
`24b1478`. Generation reads them when the corresponding caption or OCR flags
are set. The preparation commands live in the dataset component.
