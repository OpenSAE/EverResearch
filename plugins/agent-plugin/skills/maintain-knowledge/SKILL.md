---
name: maintain-knowledge
description: Save or update a durable note about a lesson, decision, or idea from a conversation. Use when asked to capture knowledge people can read and build on later.
---

## Runtime compatibility

The repository skills are synchronized with EverResearch source. This distribution's launcher uses the published EverResearch 0.3.1 wheel. For source workflows that require the `.everresearch/` setup or a source-only command, use the CLI from the corresponding [EverResearch source checkout](https://github.com/OpenSAE/EverResearch/commit/9b036cb2109788a8545724a03c313502d255d187). Use the project's existing maintenance entry point when working with the published runtime.

# Knowledge maintenance

## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately.

## Purpose

The exchange preserves knowledge worth long-term use. The `note` function is currently available to organize knowledge generation situations, human thinking, AI ideas, methods of use, potential roles and subsequent comments into a stand-alone Markdown document.

## Scope

Use the skill directory for local notes in a source checkout. In an installed release, use the directory printed by `rh guide skill-state maintain-knowledge`. Keep `note/` and its approved Markdown records under that directory.

## Note: Recording knowledge

### From communication to preservation

1. To listen to the thoughts of humankind and to understand the state or problems that it creates in the context of current exchanges, to distill core ideas that deserve to be preserved.
2. Collapse the title, file name and complete draft. Human thought faithfully expresses its intentions; AI's ideas write AI's understanding, evolution and addition to this idea. Use the methodology to illustrate how knowledge can be used for practical action, and the potential role of it suggests its potential value. Key elements need to be further developed and understood to humans with short questions; the information yet to be added is actually marked as “to be supplemented”.
3. The name of the document to be saved and the full text are sent to humans for reading.
4. Human beings who have seen it have either accepted it or made it clear that there is no objection, such as “can be” “very good” “so” “no opinion”, i.e., consent to be preserved and immediately retain the content as if `note/<Two words.>.md`,Returns the full path link of the actual document. When humans agree to continue discussing other issues, then finish saving and then deal with subsequent discussions. Saves follow this endorsement directly. Keeps the displays while humans have not responded.

The initial “follow-up notes” section of the record remains blank. When a new understanding, feedback or addition is presented, the original record is read, the original record is collated and displayed, and the corresponding document is updated as soon as the human person has acknowledged or has made it clear that there is no objection. The subsequent notes are added in chronological order, and the process of thinking is maintained; the text is revised using the same rules of presentation and immediate preservation.

### Save failed processing and reporting

Keep the full text that has been approved, check whether the note/ name of this skill is written, whether the file name conflicts and whether the original record has any corresponding content. Read the target file with the Python path and text read-back, checking word-for-word approval of the body and the fixed chapter, and give the actual path to the human being. If you are still blocked, state where the body is kept, the specific reasons for the failure and the conditions for continuation.

### Title and filename

- The title expresses a clear core idea, which is kept within ten words, and is streamlined and accurate. The Chinese title is phrased in natural semantics.
- Each knowledge is saved independently as a Markdown file, whose name consists of two short English words, using lowercase letters and a underline, such as `shared_understanding.md`, `patient_reasoning.md`. The filename expresses the actual meaning of knowledge.
- See `note/` documents before saving. Supplements to the same knowledge are added to the corresponding records; new knowledge is named using two terms that are relevant and stand-alone, and the file name is displayed with the body of the document, and is saved in a uniform way according to human feedback.

### Fixed record format

The following heading order is used for each knowledge, with the text shown and accepted by humans. The first line is the title of knowledge, with the end of the “follow-up comment” left blank for initial retention.

```markdown
# Title of knowledge

## Status or problem of knowledge generation

Describe what circumstances, experiences or problems give rise to this knowledge.

## Human thinking.

"To organize the core of human thoughts in a faithful and clear expression.".

## AI Thoughts.

Records AI Understanding, evolution and complementarity of core ideas.

## Usage method

Describe how this knowledge can be used in practical thinking and action.

## Potential role

An indication of the potential help and value of this knowledge.

## Follow-up comment
```

### Record expression

Writes around ideas themselves, using common terms and complete, simple and natural language. Technical terms are used to convey the actual needs of core ideas, and to describe meaning in easily understandable terms.

Use a positive and clear sentence to directly describe ideas, reasons, actions and roles. The facts are documented on the basis of the facts, and are expressed in their actual meanings, such as “I think that ” “this knowledge can help ” and to bring language certainty into line with the original intent, the basis for it.

Each section focuses on the substance of the knowledge, expressing the audience and communicating through a positive statement. The whole body is structured around core ideas, maintaining a coherent interpretation; focusing on how ideas are generated, understood, used and how they continue to develop.
