# Migration and Merge Functions

## Purpose

Maintaining operational methods based on actual responsibilities migration, consolidation, handling of transboundary reliance on core components and re-use of core tests.

## Scope

It applies to cross-documentation functions and when cross-border reliance on core components is found.

## Organisation

1. From the identified core function and the actual call relationship, positioning should be the module responsible for that function.
2. The same function is maintained centrally, and the caller uses co-achievement; mission-specific behaviour is attributed to the corresponding task.
3. Synchronizes the caller, removes old realizations and their exclusive forwarding, configuration and testing.
4. Runs the same core set of functional tests to check that the same normal input continues to produce the required results.

For example, when the same SAE interpretation source is analysed separately at multiple entry points, the corresponding relationship can be concentrated in the module responsible for the resource record.

It is based on functional responsibilities and call needs.

## Addressing transboundary dependence on core components

When dependency is found, the launch documents and line numbers, public entry points, complete dependencies, final targets, and functions to be repaired are recorded in this maintenance memorandum.

1. ** Prioritizes the integration of the official function. ** confirms the purpose of the call, the input, the product and its subsequent use from the public entry point, and identifies the results that have been cited and used for the official purpose. This logic is integrated into the existing layout, such as the calculation or report generation logic of `scripts/` used by the official mission into the corresponding `tasks/` module. Formal tasks call the module.
   Experimental review and analysis of results `scripts/` or `tests/` Read `experiment/`,Submit the loaded value to the core component for processing. The core component's running results can be written `experiment/`.Yes. `experiment/` The copying of data or codes will still leave the core component to be read across borders and must be repaired with a change in the call relationship.
2. ** Removes only when the function is considered redundant. ** Confirms that the result of the official access commitment and downstream use does not require the function, removes the call in the core component within the mandate and only serves the configuration, testing and description of the call.
3. ** Review from the public entry point. ** Checks the results of the commitment with the original representative input, running the skills-dependent checker, checking the dynamic references along the actual configuration. All references to the core component match the boundaries of the four core directories and the external package, and the code in `experiment/` is cleared before this item is marked as approved.
