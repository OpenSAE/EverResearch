# Select the source and scope

## Purpose and main function

Select the source and scope.

## Scope of application

Use before analyzing a paper or repository or deciding whether to reuse previous graphs.

## Writing graph explanations

Use familiar words, complete natural sentences and affirmative descriptions. Explain the concrete objects, actions, results and relationships supported by the sources. Keep necessary scientific terms with their meaning. Progress updates communicate new findings, decisions and obstacles; delivery explains the graph's use and provides its page. Production records retain scope and evidence for later reading.

## Startup and conversation

When the user loads ExtractStructure without choosing an object, briefly introduce the two modes and recommend entry points from visible files and folders. When the user has already specified text, a folder, or scope, follow that choice. Requests to read or discuss the skill, or to pause execution, follow the requested scope.

Keep questions and progress updates focused on meaning, suggestions, and current user choices. Explain what a folder turns into what result and what that helps people accomplish. Explain technical details of reading, drawing, saving, and page operation when the user asks. Provide full paths for candidate folders and explain size and existing results when they affect scope selection.

Retain the user's language preference. Once Chinese is selected, use Chinese for conversation and results. Start in English when the first-use language preference remains undecided and mention Chinese support.

Use natural explanations of functions, such as “read records for later selection” or “save the selected results.” Graphs use understandable objects, actions, and results. Keep function names, fields, and implementation-location details in internal evidence. Show quantities, calculations, and conditions needed to understand methods and results in their corresponding nodes.

## Phase 1: Review and agree on scope

### 1. Introduce both modes and select an object

When the user is choosing an object, explain the two modes briefly: text mode turns an article's questions, methods and evidence into a graph; repository mode shows a project's functions, folder responsibilities and file collaboration. Scan visible files and offer relevant entry points with full paths and short descriptions.

An already selected article, project, file or coverage is the starting choice. Inspect its actual size and existing results, then ask only about choices that remain open. Reuse decisions already made in the current task. Introductions and recommendations support selection when needed.

### 2. Text mode: Select article scope

Inspect the title, sections, and length, then briefly explain the article's main topic. Locate Markdown and TeX by original headings and paragraphs; locate PDFs by actual pages, sections, and page content.

**For TeX above 500 lines or PDFs above 10 pages, offer scope choices and wait for a decision.** For multi-file TeX, count the main file and actual included body text. For long or multi-topic Markdown, recommend a scope based on reading size. Retain an explicit user choice of full text, sections, or main body.

Offer choices based on actual content, with a brief description of each:

1. **Full text.** Cover the whole article, including appendices when present.
2. **Main body.** Offer when appendices exist, describing the main questions, methods, and results covered.
3. **Selected sections.** Recommend one or two actual section combinations, explaining their content and allowing another user selection.

Read the chosen content in depth and understand claims and reasoning before extracting structure. For research articles, use “Research article analysis and information retention” below as a reading guide. Upper levels organize main questions or topics; lower levels develop claims, methods, derivations, evidence, and results according to their actual role. Connections briefly express real relationships such as “measure,” “support the claim,” or “derive the conclusion.” Headings support navigation and reading; article meaning determines groups.

Save original evidence: headings, paragraphs, and line numbers for Markdown; sections, original labels, and line numbers for TeX; physical pages and corresponding paragraphs, equations, or figures for PDFs. Save text graphs through the `article` command, retaining evidence from each original file. Then select existing graphs and follow shared drawing and delivery. For short texts, use the full text unless the user chooses otherwise.

After selecting text scope, read [Article analysis](article-analysis.md). Purpose and main functions: Explain how to turn selected Markdown, TeX and PDF passages into article topics, details and relationships with original source locations. Scope: Use when creating or updating an article graph after the user selects the text and coverage, including articles whose body spans several files.

### 3. Repository mode: Assess analysis size

Use file listings to count Python and Markdown files separately, their combined total, and major branches. Read detailed content during execution. Omit `__init__.py` from folder listings. Programs skip ExtractStructure's own folder, version control metadata, and Python environments. Recommend treatment of backups, historical material, and local outputs based on actual purpose.

For a combined total of up to 100 Python and Markdown files, continue with the selected scope. Above 100, briefly describe size, main file types, and major branch purposes. Follow an explicit coverage choice already made for this task; otherwise recommend a scope and wait for a choice:

1. **Analyze the recommended scope.** Describe included branches and file counts, plus skipped major branches, archives, backups, or local outputs.
2. **Analyze everything.** Cover all candidate files inventoried.
3. **Choose a custom scope.** Let users name included or skipped branches and provide one short example when useful.

List relevant branches as “path — approximate purpose; file count.” Explain historical archives too; mark uncertain purposes for confirmation. Summarize the agreed inclusion and count, then continue.

### 4. Look for reusable results

Internally inspect this project's or article's existing folder, file, or article graphs within the skill. Start analysis and drawing when there are no existing graphs. Otherwise assess suitability using original-file changes, briefly explain reuse or updates, and ask the user; recommend reuse when appropriate. Retain an existing decision.

When file graphs exist, use this wording in the user's language with actual counts and both choices in bold:

> Some files already have cached graphs, covering X/Y files in this scope. Would you like to **redraw and replace these cached graphs**, or **reuse them**?

X is the number of usable existing file graphs; Y is the selected file count. Repository mode counts Python and Markdown together; text mode counts selected text files. Replacement affects graph caches; original files retain their content. If only a folder overview exists, explain that it has a cached graph, offer the same two bold choices, and identify what replacement affects. Separate overview and detail choices when useful.

Inventory data supports internal work. Explain changes that actually affect user choices, for example: “Two files were added; I recommend updating the overview.”
