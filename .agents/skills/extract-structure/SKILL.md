---
name: extract-structure
description: Read a Markdown, LaTeX, or PDF paper in depth, or explain how a codebase is organized. Use when asked for a structural walkthrough, diagram, or interactive HTML overview.
---

# Understand papers and code with ExtractStructure

## Purpose and main function

Explain how a research paper or codebase fits together and turn its structure into an interactive map.

## Scope of application

Use for Markdown, TeX, PDF, or code repositories. In text mode, trace questions, methods, claims, and evidence. In repository mode, map folder responsibilities, file collaboration, and selected implementations.

## Work from source to map

1. Identify the user's source and intended coverage. If the scope is open, the input is large, or earlier maps may be reusable, use the [scope guide](references/select-scope.md) to inspect the material, offer concrete choices, and check for reusable graphs. This guide also gives the size thresholds that require a scope decision.
2. Read the original source before drawing. Record the headings, pages, lines, or files that support each relationship. Use the [article analysis guide](references/article-analysis.md) for papers, the [folder analysis guide](references/folder-analysis.md) for repositories, and the [file analysis guide](references/file-analysis.md) for internals.
3. Use [Build and deliver structure maps](references/build-and-deliver.md) for graph text, presentation rules, and delivery. Preserve key claims or behavior and verify that the exported page actually opens. Use the user's language for the explanation and keep evidence tied to the original source.

Use `rh guide skill-state extract-structure` to find the writable working directory in an installed release. Use [Graph data and storage](references/graph-format.md) for inventory, reuse, exported pages, and local serving.
