# Build and deliver structure maps

## Purpose and main function

Build and deliver structure maps.

## Scope of application

Use when preparing a graph, setting up delivery, or preserving analysis for reuse.

## Required presentation and writing rules

Apply this section to folder, file, and article graphs in both modes, and to user-facing pages and delivery explanations. ExtractStructure helps people understand structure, purpose, and actual connections. Follow the skill's established presentation. Apply user-requested changes to their specified scope. These requirements also govern presentation and writing guidance in references.

- **Use the existing visual structure.** Present content through existing nodes, groups, connections, and expansion. Additional visual regions, panels, banners, sidebars, legends, and explanatory components require an explicit user request. Requests for more explanation, background, or completeness use the established interface.
- **Describe structure and purpose directly.** Pages, nodes, connections, and delivery explanations state what objects do, how they connect, and what they produce. Explanations of capability boundaries, analysis boundaries, exclusions, and disclaimers stay outside the presentation. Follow the established selection process when users choose objects and scope.
- **Keep node names short and specific.** Name one clear purpose, object, or result, retaining identifying features. Examples: “Fit 256 combinations, evaluate 128” and “Pairwise modeling improves ranking from 0.9782 to 0.9959.” Use concrete content rather than generic labels such as “process data” or “effective method.” Give distinct topics their own nodes and keep paragraph-length explanations in appropriate detail.
- **Separate names and explanations.** Use short names for scanning and `meaning` for substantive explanations. Current cards are 230 × 72 pixels; aim for about twelve Chinese characters or twenty-one Latin characters per row and up to four rows. Folder cards also reserve space for filenames. Treat these as writing guidance; the viewer abbreviates overflowing names and shows the full name and explanation on hover or keyboard focus.
- **Preserve substance in node explanations.** Use concise natural sentences for concrete objects, procedures, necessary conditions, or key results as appropriate. Concision retains information needed for understanding. Split complex content into concrete nodes within existing expansion structures: summarize topics above and explain substance below. Each explanation adds relevant content and uses compact prose.
- **Keep connection explanations brief.** Use one short phrase for a concrete relationship, such as “provide selection criteria” or “generate summary report.” Existing interactive detail supports at most one short natural sentence. Each label conveys a single connection; background and boundary explanations remain outside connection text.
- **Use familiar words.** Express objects, actions, and results in everyday language. Keep necessary domain terms tied to concrete use. Store technical names used only for locating implementation in internal evidence. Show research objects, necessary assumptions, core calculations, and key values with the corresponding content.
- **Derive meaning from the source.** Node, group, and connection meanings come from code or documents actually read. Every function, connection, and explanation has an observed basis in that material.

## Phase 2: Analyze, draw, and deliver

Repository mode follows the steps below after agreeing on folder, scope, and existing results. Text mode organizes the agreed article structure into an expandable article graph, then follows steps 5 and 6. Both modes use the current drawing components.

1. **Explain the whole first.** Use one or two sentences for the folder's work, then explain file purposes.
2. **Find actual collaboration.** Describe which file supplies what, who receives it, and what results, saving original code or document locations. Apply “Markdown analysis and relationships” below to connections with code. Keep independent files as independent nodes.
3. **Draw a two-level folder graph.** The upper level summarizes main functions; the lower level shows files and collaboration. A file serving several functions appears once with its actual connections.
4. **Connect file details.** By default complete internal function graphs for selected files and connect them to the overview. Follow choices to show only the overview or reuse existing details. Analyze Python by functions and concrete processes; Markdown by purpose, topics, and specific explanations.
5. **Write clear graph text.** Follow the required presentation and writing rules for concise names and connections explaining objects, roles, and results. Write English first, then natural Chinese. Keep source locations and implementation-location details in graph data; show concrete procedures, conditions, and outcomes needed for understanding in nodes. Follow the user's selected translation scope for existing graphs.
6. **Deliver an accessible page.** Save graph data and select delivery according to the environment: use the local service when the user can access its address, or export an independent HTML page for file delivery or platform hosting. Use available host tools to attach or host the exported page and obtain a usable file link or hosted address. A service address identifies the running service; user access depends on the host network and forwarding facilities. Folder tasks open the selected folder graph with all expandable nodes collapsed. Text or individual-file tasks open that article or file graph with the same collapsed initial state. Explain in one or two sentences what it shows and how to expand it. Provide a result link and a brief explanation of how to explore it. Perform content and page checks when requested, within the specified scope.

After scope selection, read [Folder analysis](folder-analysis.md). Purpose and main functions: Explain folder responsibilities, file collaboration, and subfolders so readers can move from the overview to individual files. Scope: Use when creating or updating a selected folder's function graph. Retain the agreed folder, file scope, and treatment of existing results.

For file internals, read [File analysis](file-analysis.md). Purpose and main functions: Explain a file through expandable functions and concrete processes, so readers can move from its overall purpose to its internal behavior. Scope: Use when creating or updating the internal function graph of a selected Python file, whether selected from a folder or specified directly by the user.

For inventory, drafts, saving, exporting, or serving pages, read [Graph data and storage](graph-format.md). Purpose and main functions: Describe internal draft fields, source locations, bilingual content, commands, and result storage. Scope: Use this skill's programs to create, save, link, or open graph data. This document guides internal program operation; explanations to users follow the folder and file analysis guidance.

## Research article analysis and information retention

Use this section for research papers and articles in text mode. Read selected originals in depth, find these common elements, understand their connections, and organize the graph:

- **Background.** Identify the research object, existing knowledge, and actual applications.
- **Motivation.** Explain the concrete questions left by existing methods or understanding and why this work studies them.
- **Contributions.** Identify new findings, methods, or evidence, using the article's actual distinctions: “Contribution 1: concrete content,” “Contribution 2: concrete content,” and so on.
- **Related work.** Explain what earlier studies actually did and how they connect to this work's questions, methods, and contributions.
- **Methods.** Explain selection of inputs and research objects, operations, comparisons, calculations, and resulting outputs.
- **Assumptions.** Identify specific conditions used by methods, theorems, or derivations and connect them to their results.
- **Theory.** Explain each theoretical result, its conditions, core relationships, and derivation evidence.
- **Corollaries.** State which further conclusions follow from which theories or conditions.
- **Experiments.** Identify objects, tasks, comparisons, controls, and key numerical or observed results.
- **Conclusions.** Explain what theory and experiments jointly support and how they answer the initial questions.

Use these elements as a reading guide; actual article content determines grouping. Include elements present in the original and expand multiple contributions, assumptions, theories, or experiments separately. An element can span several concrete nodes, with counts determined by what is needed to explain its substance. Original documents retain their content; nodes faithfully extract or paraphrase meaning and preserve evidence.

Upper levels summarize topics; lower levels retain concrete substance. Each concrete node should explain what the authors studied, did, or found. Experimental nodes keep objects, controls, and key values needed to understand results; method nodes retain key steps and computational meaning; theory nodes retain results and necessary conditions. Split large amounts of content into connected expandable nodes.

For example, expand “sampled fitting” into “select 16 features” and “fit 256 combinations, evaluate 128.” For “pairwise modeling improves prediction,” retain “ranking correlation increases from 0.9782 to 0.9959,” then connect equal-parameter controls and actual repeated-split results. Replace example objects and numbers with original content during analysis.

Connections express supported relationships, such as “motivate the research question,” “provide validity conditions,” and “support contribution 2.” Keep shared content as one concrete node linked to every actual role. Explain theoretical results, observations, and author interpretations according to their own meaning. Every node and connection refers to a position in the selected original.

## Developer feedback

When the user asks about the developer or how to send feedback, provide [Haotian's GitHub profile](https://github.com/AtheavenMa) or hma232@wisc.edu. A known project repository provides its own issue-reporting page.

## Markdown analysis and relationships

Markdown and Python files share folder nodes, file details, existing-result handling, and progressive exploration. For documents, explain overall purpose before main topics and specific details, saving headings, paragraphs, and original line numbers as evidence. Headings support navigation; content determines graph groups.

Classify Markdown by its actual role in the current work:

- **Input.** Supply requirements, rules, data, or instructions actually used by code or agents. Connections run from the document to consuming code and explain what is supplied and how it is used.
- **Output.** Be generated or organized by code, or written using code information, such as runtime reports, interface descriptions, and source analysis. Connections run from the producing or supplying code to the document and describe the result.
- **Process.** Perform an intermediate role, such as organizing agent reading, decisions, and later operations. Explain actual inputs, guidance, and connections before and after it.
- **Independent.** General background, folder descriptions, and reading guidance usually appear as independent gray nodes. When reading establishes actual input, output, or processing roles, classify and connect accordingly.

Base relationships on code behavior, concrete document requirements, and actual use. Filenames, links, and shared topics help locate related content; actual purpose determines connections. Independent nodes retain their own positions and detail entries. Classify a document's overall role and internal topics separately.

Folder inventory and Python file details use Python syntax to locate classes and functions. Article saving accepts Markdown, TeX and PDF evidence through the `article` command and uses the same graph assembly and viewer. For folder scopes containing Markdown, supplement the Python inventory with text listings and save document details through the article entry. Python-specific reference methods apply to Python; Markdown analysis and relationships follow this section. Program extensions follow user-approved scope.

## Working files and delivery selection


For an installed release, keep working files and results under the directory returned by `rh guide skill-state extract-structure`. Set `RH_SKILL_WORK_DIR` to that path when starting this skill's scripts.

Save extracted text, page extracts, drafts and any task-specific working files inside `results/tasks/<task-id>/` in this skill. Use a descriptive task identifier. Record created or updated artifacts in that directory's `log_updates.jsonl`, with a timezone-aware timestamp, skill-relative path, brief content and actual source tool or script. Saved graph commands and exports maintain their own result logs. Original documents and analyzed code retain their content.

Choose an accessible delivery after saving. A local service suits environments with user access to its printed address or a supported forwarded address. Independent HTML suits file attachments and static hosting: export the chosen graph, its available descendants and ancestor navigation using the shared viewer. The exported file contains its required graph data, styles, scripts and background computation resources. A hosting platform supplies the publication URL; use available host tools within the user's requested delivery scope. When interactive hosting is unavailable, provide the exported file through the host's file attachment or download facility. State the actual delivery status when access remains unresolved.

Keep the chosen article or folder as the initial view, with expandable nodes collapsed. Language switching works inside the page. Browser storage saves preferences when available. Background label placement uses a worker when permitted and falls back to page computation when workers are unavailable; complex layouts may take longer in that fallback.

## Page use and result storage

Top navigation browses levels like a file browser. Folder paths open folder graphs; filenames open existing detail graphs. Use independent subfolder graphs when available. When a parent graph covers a subfolder, display its files and collaboration from that parent.

Deliver the selected folder or file's own path with all expandable nodes collapsed. Keep its overall view; users locate, highlight, and expand content after opening.

Drawing components handle compact layout, expansion, connection labels, highlighting, and languages. Store projects separately under this skill's `results/<project-id>/`. Deliver graph data and page links by default. Choose the local service or independent HTML export according to user access and the host environment. Follow explicit requests for static images or other formats.

For an enrolled ResearchHarness project whose exported page needs a persistent review record, register the independent HTML with `rh projects structure add`, supplying the source revision and analysis scope. ResearchHarness stores the registered page and review record under its own `src/project/maintained/<project-id>/structure/`.

New and reused graph data share these page defaults:

- **Fixed within groups, compact between groups.** Keep concrete file/process positions within groups; allow whole-group movement on expansion. A collapsed overview occupies one card; expanding everything restores the full lower-level layout.
- **Immediate interaction.** Expansion, collapse, location, and view movement switch immediately. Connection label placement runs in the background while browsing stays responsive.
- **Mineral Atlas themes.** Follow the system initially and remember manual choices. Show four category colors at bottom right; cards use translucent category fills, expanded regions match the canvas, and highlights retain category colors.
- **Simple toolbar and connections.** Keep search, expand/collapse all, and zoom. Connections explain actual collaboration, with relationship classifications and badges omitted.
- **Deduplicated connection labels.** Merged labels express a distinct shared purpose. When only branch labels are meaningful, show each once. Keep concatenated text for internal relationship reading and use the distinct labels on the current view.
- **Saved categories.** For new or redrawn graphs, classify overview and concrete nodes independently as input, process, or output based on actual responsibilities and context. Zero-connection nodes are independent and gray. Save categories with the graph; arrow direction supports preliminary inference for nodes awaiting labels.
- **Transparent labels.** Use transparent areas with width at least height, allowing slight nearby-border overlap while keeping text and connections clear. Node names and path navigation convey ownership.

For graph generation, reuse, delivery, or presentation changes, read [Presentation and interaction](presentation.md). Purpose and main functions: Describe ExtractStructure's established visual, layout, interaction, and performance requirements, and identify the shared page resources responsible for them. Scope: Use when generating or reusing ExtractStructure graph data, delivering pages, or modifying this skill's drawing and presentation resources.

Analysis and drawing read selected code and documents. Changes to originals or the skill, old-result deletion, additional tests, and browser checks follow explicit user authorization. Saving checks that required drawing fields are complete so the page can load. Explain functional accuracy and readability based on actual reading or requested checks.
