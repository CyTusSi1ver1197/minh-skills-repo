---
name: explain-skills-in-details
description: Explain a topic in depth to someone new to it who may already know its foundations or related topics. Bridges from what they know, maps related concepts and how they connect, walks the flow of actions between them, and ends with how to apply it for real advantage. Keeps a checkpoint file so long explanations survive context compaction. Use when asked to explain, teach, break down, or help someone understand a concept, technology, process, or system.
argument-hint: "[topic] [optional: what you already know] [optional: overview|working|expert]"
license: MIT
metadata:
  version: "2.0.0"
---

# Explain Skills in Details

Teach a topic to a learner who is new to it but may know its foundation or
something nearby. Keep the **context**, show the **relationships** between
related topics, walk the **flow of actions** across them, and finish with
**how to apply it** to gain an advantage.

Model-agnostic: plain Markdown and Mermaid only.

## How this skill is organised (load only what you need)

This file is the router. Detailed instructions live in separate files. Read a
file **only when you reach the stage that needs it**, and do not re-read a
file you already read in this conversation unless context was compacted.

| Stage | Steps | Read before starting the stage |
|---|---|---|
| A. Ground | 1 Calibrate · 2 Payoff · 3 Bridge · 4 Map | [references/stage-a-ground.md](./references/stage-a-ground.md) |
| B. Build | 5 Core layers · 6 Flow of actions · 7 Worked example | [references/stage-b-build.md](./references/stage-b-build.md) |
| C. Use | 8 Apply · 9 Myths · 10 Check + recap | [references/stage-c-use.md](./references/stage-c-use.md) |
| Any | Style, depth, follow-ups | [references/style-and-depth.md](./references/style-and-depth.md) (read once, at the start) |

Templates: [assets/output-template.md](./assets/output-template.md) for the
answer layout, [assets/checkpoint-template.md](./assets/checkpoint-template.md)
for the checkpoint file.

## Inputs

| Input | Required | If missing |
|---|---|---|
| topic | Yes | Ask for it. |
| known foundation | No | Infer from the request and open files; else ask one short question (Step 1). |
| goal | No | Assume "apply it in real work"; state the assumption. |
| depth | No | `working` (can apply it unaided). |
| context (stack, project) | No | Use workspace files if relevant; else neutral examples. |

## Checkpoint protocol (prevents context loss)

Long explanations can push earlier turns out of the context window. The
checkpoint file is the **single source of truth** for the explanation's state.

1. **Location:** `.explain/<topic-slug>.md` at the workspace root
   (`<topic-slug>` = lowercase, hyphens, e.g. `dependency-injection`).
   If no workspace folder is open or file writes are not allowed, keep the
   same content as a short "Context Card" block in chat instead and say so once.
2. **Start:** before Step 1, check whether the file exists.
   - Exists → read it and **resume** from `Next step`. Do not restart.
   - Missing → create it from the checkpoint template after Step 1.
3. **After each stage (A, B, C):** update the file: status, key terms
   defined, map nodes, running example, decisions, open questions, next step.
4. **Before each stage:** re-read the checkpoint, not earlier chat turns.
   Trust the file over your memory of the conversation.
5. **Keep it small:** ≤ 60 lines. Store summaries and decisions, never the
   full explanation text.
6. **On "continue", "go on", or a new chat about the same topic:** read the
   checkpoint first, then carry on from `Next step`.
7. The folder is scratch data. Suggest adding `.explain/` to `.gitignore`
   once; never commit it.

## Delivery rules (keep each turn's context small)

- `overview` depth → one reply covering the short form of all stages.
- `working` / `expert` → deliver **one stage per reply** (A, then B, then C).
  End each reply with one line: what the next stage covers and "say *continue*".
  If the learner asks for everything at once, deliver it all, still updating
  the checkpoint after each stage.
- Reuse the **same running example** in every stage (it is in the checkpoint).
- If the learner asks to save the explanation, write it to
  `.explain/<topic-slug>-explanation.md` using the output template.

## Done criteria

All must be true before the explanation is finished:

1. Starts from something the learner already knows (explicit bridge).
2. Every new term is defined in plain words on first use.
3. A relationship map shows the topic, its parts and related topics, with typed links.
4. The flow of actions is shown in order (input → steps → output) with failure points.
5. One concrete end-to-end worked example, using the running example.
6. A "use it to your advantage" section: when to use, when not, trade-offs, first action.
7. Misconceptions named and corrected.
8. Ends with an understanding check, recap, and next topics.
9. Checkpoint file shows `Status: complete`.
