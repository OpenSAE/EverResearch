# Return Check

## Purpose

Formal regression check for location and configuration, data and performance processing.

## Scope

Use the Python, which has been installed to support the project, for the selection of inspections when the project maintains the affected functionality.

- [Run the link.](../tests/test_workflow.py)Check the regular entrance and the results.
- [Border checks](../tests/test_boundaries.py)Checking configuration isolation, data disaggregation and candidate failure.
- Runs a check of this directory with `python -m unittest discover -s tests`. The inspection's input, function and execution range are shown in the tests; the corresponding assertions and instructions are updated when functional changes occur.
