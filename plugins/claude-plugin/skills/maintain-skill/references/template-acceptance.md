# Accept a research project template

## Purpose and main function

Verify that a template can be copied and run and that a reader can identify and inspect the original source and understand how EverResearch organized it.

## Scope of application

Apply these checks to each project added to or maintained in the template catalog. The [whole-project verification guide](../../maintain-project/references/coordination.md#verify-and-deliver-the-whole-project) specifies the layout and runtime checks for scientific projects. This page adds the requirements for a redistributable template.

## Verify a copied template

- Use `.everresearch/` as the maintenance directory. The active documentation, paths used by executable code, and ignore entries must match the files on disk. Use EverResearch as the product name and the `everresearch` prefix for managed HTML comment markers. Preserve historical upstream files and their original spelling in source archives.
- Keep the portable offline launcher and guide in `.everresearch/`. In a copy, run `python -IS .everresearch/maintain.py status`, `python -IS .everresearch/maintain.py check`, and `rh projects project check <copy> --strict`. Follow the setup guide and run a representative documented command with the declared inputs. Read the result through the documented interface and rerun the strict check with the generated files in place. Record any checkout, resource, or runtime blocker with its evidence.
- Preserve source licenses and executable commands. Keep local credentials, online bindings, environments, machine-local paths, and temporary outputs out of the delivered template. Use the project README and component guides for installation, configuration, tasks, and results.

## Add project origin to AGENTS.md

Keep project-specific coding instructions. Keep operational guidance in the file that owns it and link to that file where readers need it. Consolidate duplicate installation, data, model, or experiment instructions into the matching existing guide. Append the following user-facing section outside the generated maintenance markers. Use the same labels and headings in each template.

````markdown
## Original project and template layout

- **Original project** [official project name](upstream URL)
- **Source revision** [commit or release](permalink for the archived source)
- **Paper** [verified paper title](official venue or paper page) · ICLR 2025 Oral
- **Authors** Full author list in the official order, or the credited project authors for a project without a paper
- **Original source archive** [project.zip](third_party/upstream/project.zip)
- **Archive SHA-256** `<SHA-256 of the saved ZIP>`

### Before organization

```text
OriginalProject/
├── source/
│   ├── datasets/
│   └── training.py
└── README.md
```

### After organization

```text
TemplateProject/
├── base/
│   └── launcher.py
└── README.md
```
````

Use the publication venue, year, and designation as stated by the publisher or conference. When there is no verified designation, report the verified venue and year. For a preprint use its actual publication status. For a project without a dedicated paper use `No dedicated paper` and credit the upstream authors or maintainers. Papers for a dataset used by a template can be linked with an explicit dataset label.

Generate both trees from the actual source archive and template. Show two directory levels, root files, and entries that explain the project layout. Use a fenced text tree with `├──`, `└──`, and `│`. If a branch is shortened for readability, mark the omitted entries explicitly. The final tree includes `.everresearch/` and `third_party/upstream/`. The archive link above gives the full filename.

## Keep the original archive

Store the untouched original source as a ZIP under `third_party/upstream/<project>.zip`. Use an upstream ZIP for the identified revision or produce one from the untouched tracked source or a verified original package. For an EverResearch-authored example, use the identifiable original example release or baseline and label it as such. Keep the ZIP intact in the template and inspect its member list without extracting it there. Verify the ZIP integrity, its origin and revision, and the link from `AGENTS.md`. Keep datasets, weights, local work, and generated results out of an archive assembled locally. If the exact original source or its redistribution terms cannot be established, report that gap before accepting the template.

Record the originating revision and SHA-256 of the saved archive when the project is acquired,
before reorganizing it. Check both against the files being delivered and include them in
`AGENTS.md`. For a previously organized project with a
missing record, recover the source from the original checkout, baseline archive, or operation
records. Check repository history and compare unchanged tracked files when they can establish
the starting tree. If recovery fails, rebuild a candidate from one explicitly pinned upstream
archive and verify the organized result through its documented public commands before replacing
the template. Keep the earlier template available until the rebuilt copy passes. This gives the
replacement a verified starting archive and before/after trees.
