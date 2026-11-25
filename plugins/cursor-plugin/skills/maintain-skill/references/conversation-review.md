# Conversation logs and independent review

## Purpose and main function

Define how to record what a person asked and what the assistant did, audit the resulting file decisions, and turn accepted feedback into skill changes tested on a real project.

## Scope of application

Use this workflow when a user invokes maintain-skill to record or analyze a project conversation, or to evaluate a subsequent skill change based on those findings.

## Record a conversation

1. Resolve the project from the user's selection, the current workspace, or an existing log that uniquely matches the conversation. Save the log as `agent_log/<ProjectName>_<summary>.md` under the writable skill directory specified by the skill entry. Use the real project name and one lowercase English word that describes the conversation, such as `ProjectName_figures.md`. Use the same file for later recording requests about that conversation. If another conversation already uses that name, choose a different relevant summary word. Preserve the existing log.
2. Read the available conversation in chronological order. Treat a supplied transcript or attachment as source material. Include substantive requests, corrections, and follow-up questions with their exact words, including typos, and summarize the assistant's observed actions in the paired row. Record failed, interrupted, or unverified work as such. Identify any gap in the available record instead of reconstructing unavailable wording. The invocation that merely requests logging serves as a command to this skill.
3. Preserve original wording in Markdown table cells. Escape literal pipes for table syntax and represent line breaks with `<br>`. For multiline content whose Markdown syntax would make a table unreadable, put a verbatim block below the table and link the row to that block. Keep each request identifiable by its row number.
4. Group the concrete paths under **新增和修改的文件**. Include source changes, moves, outputs, and temporary material when the conversation establishes them. Mark file status and add links to absolute paths where available. Group paths from successive revisions of the same output rather than duplicating them. State when a reported path has since moved or its current existence is unverified.
5. When updating a log, append newly recorded turns in order and merge their paths into the file section. Preserve prior wording and numbering and avoid duplicating rows already present. Read the saved file back and provide its link. These logs are local working records.

Use this format:

```markdown
# <项目名> <会话主题>

## 目的和主要功能

记录本次对话的用户原话、实际执行和涉及的文件，供后续维护分析。

## 适用范围

覆盖 <明确说明的项目和对话范围>。

### 逐轮记录

| # | 用户原话 | AI 的执行总结 |
| ---: | --- | --- |
| 1 | <逐字记录> | <实际执行、结果或未完成状态> |

### 新增和修改的文件

- **<实际用途>。** <操作、路径和可核对的结果>
```

## Analyze file decisions

Begin with the selected log as a record of intent and actions. Trace each material file or related group from the request to its producer, physical location, and downstream consumers. Compare those facts with the applicable project rules and maintenance skills. Check files beyond the ones the conversation highlighted when the same producer, configuration, writer, or reader has other outputs. Examine both historical paths recorded in the log and present paths verified on disk. Separate rules that existed at the time from rules the user added later.

Report confirmed issues to the user in this order:

| 位置或轮次 | 不符合之处 | 原因及适用规则 | 当前路径 | 正确路径 | 依据或待核实项 |
| --- | --- | --- | --- | --- | --- |
| <日志行号与文件用途> | <实际偏差> | <为何影响放置、命名或使用> | <已核实的绝对路径> | <预计的绝对路径或清楚标明的候选> | <生成器、读取者、检查结果或缺失信息> |

If an old path and the current path differ, report the recorded old path separately. Explain well-placed or disputed files only where that helps a decision. Keep the judgment focused on file placement, naming, ownership, and reproducibility of reading and writing. Treat technical research details as evidence for file purpose. If evidence is unavailable, distinguish the suspected issue from confirmed violations. A successful checker alone does not establish that a file sits with its real owner.

## Use feedback to improve and test the skills

1. Incorporate the user's additions and corrections. Drop findings they reject. Recheck evidence for a disputed finding when the user asks. Use the user's scope and the accepted problem to identify whether the missing rule belongs in one skill, several skills, or their supporting files.
2. Write a general rule with its trigger, how to make the judgment, what to fix, and what evidence proves it works. Check that the rule still makes sense for a different project name, layout, producer, or output format. Keep case-specific paths, model names, and repair details in the local review evidence. Retain the initial project state or comparable evidence before asking a subagent to repair it.
3. By default, show the edited file locations and explain how the changes cover the accepted problem categories. Honor `preview_after_edit=false` when the user wants the workflow to continue without the preview. Apply the user's review and execution authorization before launching the test.
4. Test with a fresh subagent. Its only instructions are the two lines defined in SKILL.md: `maintain-project` and the actual project name. The subagent starts with a clean conversation and a normally accessible project. Keep the log, specific problems, repair hints, and expected results out of its instructions and follow-ups.
5. Verify independently which issues the subagent discovered without hints, which it repaired through actual writers and readers, and what remains. Compare with the preserved initial evidence and look for exposed adjacent problems. For a further skill change, use a fresh subagent and comparable starting state. Report the actual results, including omissions and any verification blockers.
