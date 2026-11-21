# Migration and Merge Functions

## Purpose

Saves the operating methods based on actual responsibilities, merges and reuses the core test.

## Scope

For cross-document sorting functions.

## Organisation

1. From the identified core function and the actual call relationship, positioning should be the module responsible for that function.
2. The same function is maintained centrally, and the caller uses co-achievement; mission-specific behaviour is attributed to the corresponding task.
3. Synchronizes the caller, removes old realizations and their exclusive forwarding, configuration and testing.
4. Runs the same core set of functional tests to check that the same normal input continues to produce the required results.

For example, when the same SAE interpretation source is analysed separately at multiple entry points, the corresponding relationship can be concentrated in the module responsible for the resource record.

It is based on functional responsibilities and call needs.
