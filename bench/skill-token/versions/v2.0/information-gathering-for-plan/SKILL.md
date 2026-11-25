---
name: "information-gathering-for-plan"
description: "Gather and cross-validate context when a request or plan has unclear, vague, missing or conflicting Given Data (GD) or Done Criteria (DC). Searches the knowledge base and retrieval tools, resolves conflicts, then asks up to 10 missing and 6 additional questions in ranked order."
---

# Information gathering for plan

Purpose: before any plan or work starts, make the **Given Data (GD)** and the **Done Criteria (DC)** clear, consistent and complete enough to produce a **consistent result**. You do that by gathering evidence from the knowledge base and retrieval tools, resolving conflicts with the user, and asking a capped, ranked set of questions.

Works in two modes:
- **Standalone:** the user (or another workflow) asks to gather information or clarify a request or plan.
- **Integrated:** called from Step 1 of the `running-when-a-request-is-made` skill when its GD/DC are not clear enough. The IDs (`DC-n`, `GD-n`, `Q-n`) and the Question Map are shared with that skill.

Vocabulary: **DC** = Done Criteria (testable conditions for "finished"). **GD** = Given Data (everything supplied or discoverable). **KB** = knowledge base. **RAG** = retrieval tools. **C-n** = a conflict. **Q-n** = a question.

---

## Step 1 - Check whether this skill is needed

List the current DC and GD (rewrite each DC as a testable condition). Then flag every problem:

| Problem | Signal |
|---|---|
| **Unclear / vague** | A DC can't be tested by someone outside the conversation ("make it fast", "clean UI"); a GD item is ambiguous |
| **Missing** | A DC has no GD that supports reaching it; an input, constraint, owner, format or environment is unknown |
| **Conflicting** | GD vs DC, DC vs DC, GD vs GD, or any of them vs project rules or the existing code |

If nothing is flagged, say "GD and DC are clear - no information gathering needed" and stop (in integrated mode, return to the calling step).

If anything is flagged, read `references/gather-and-rank.md` and follow Steps 2-6. Write the report from `assets/report.template.md`.
