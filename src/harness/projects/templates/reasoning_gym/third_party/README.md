# Embedded upstream components

## Purpose and main function

Preserve the small upstream implementations called by the maintained dataset generators.

## Scope of application

The wheel bundles these modules for the existing Python import paths. Consult each retained notice and README before updating a component.

| Source | Used by |
| --- | --- |
| `bfit/` contains the BF-it compiler with its upstream license and documentation. | The brain-language dataset calls the compiler and minifier. |
| `sokoban/` contains the adapted Sokoban solver and generator with its upstream attribution. | The box-pushing dataset generates and validates levels. |
| `logic_puzzle/` contains the logic puzzle implementation adapted from Faith and Fate. | The zebra puzzle dataset builds and solves clue sets. |
| `rearc_generators/` contains the RE-ARC generator, domain-specific operations, and verification code included in the original checkout. | The RE-ARC dataset selects a generator and verifies its output. |
