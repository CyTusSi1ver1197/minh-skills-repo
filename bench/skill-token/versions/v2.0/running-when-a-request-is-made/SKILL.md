---
name: "running-when-a-request-is-made"
description: "Align on a work request before doing it - done criteria (DC), given data (GD), MoSCoW-ranked questions - then write a BuildPlans plan (human + agent versions) or execute an approved plan with DC-by-DC verification."
---

# Running when a request is made

Goal: **consistent inputs → consistent agent → consistent outputs.** Agree on *what done looks like* and *what data is available* before any work starts.

Vocabulary: **DC-n** Done Criteria (testable "finished" conditions) · **GD-n** Given Data (supplied or discoverable inputs) · **Q-n** clarifying question, always mapped to a DC · **Stage** one sub-plan folder of a staged plan · **Flow** an ordered list of stages (main / parallel / optional).

## Step 0 - Classify the request

| Class | Signal | Read next |
|---|---|---|
| **A. Plan** | Something new created or changed, no approved plan yet | `references/planning.md` (Steps 1-3) |
| **B. Execute** | Points to `BuildPlans/.../PLAN.agent.md` or `BuildPlans/<plan>/FLOW.md`, or says "execute / run / continue the plan" | `references/execution.md` (Step 4); for a FLOW.md also `references/staged-plans.md` |
| **C. Other** | Anything else | Ask once (below) |

For class C, ask exactly once per conversation:

> "Do you want this request to follow the structured format (consistent inputs → consistent agent → consistent outputs: done criteria, clarifying questions, then a plan)? Or should I just handle it normally?"

- **Yes** → treat it as class A.
- **No** → handle it normally and ignore the rest of this skill for this request. Keep that answer for the conversation unless the user changes it.

`references/`, `assets/`, `scripts/` are in this skill's folder (`<skill>`). Read a reference file only when its class applies, once per conversation. Re-read only if it changed or was lost to compaction. Read a template from `assets/` only when you are about to write that file.

## Context budget (always on)

1. Search before you read: list or grep first, then read only the relevant files or line ranges. Read files over 300 lines in sections. Don't re-read a file already in context unless it changed.
2. Delegate broad discovery when a sub-agent tool exists (Claude Code: Explore/Task agent; Copilot: its sub-agent / `runSubagent` tool). Ask for a ≤ 30-line summary with `file:line` evidence. Without one, follow rule 1 inline.
3. Keep tool output small: filter command output (failures only, `tail`, `--quiet`, counts) instead of pasting whole logs.
4. Write each output file once, starting from its template. Fix it with targeted edits, not full rewrites.
5. State lives in files, not in chat: the plan in `BuildPlans/<plan-name>/`, execution progress in its `PROGRESS.md`. After compaction or resume, re-read only those files.
6. Replies summarize and link. Don't repeat file contents in chat.
7. Integrity before size: never compress away a DC, a Verify line, an exact path or signature, a rule and its source, a stop condition, an assumption, or the context a plan or stage needs to run alone.
