---
description: Plan a task with the session model, then implement it in parallel with Haiku and Sonnet workers
argument-hint: <task description>
---
Act as the orchestrator for this task: $ARGUMENTS

You think, plan, decide and review. Workers execute small, well-scoped pieces. You run on whatever model this session uses.

Worker names: the workers are `haiku-worker` and `sonnet-worker`. When they ship with the orchestrate plugin the Agent tool lists them as `orchestrate:haiku-worker` and `orchestrate:sonnet-worker`; use the listed name that ends in the worker name, and prefer the `orchestrate:` one if both exist. If neither worker is listed, stop and tell me.

1. Plan
   - Explore the relevant code and write a short plan.
   - Split the work into small, independent subtasks with NON-OVERLAPPING file boundaries.
   - Do shared groundwork yourself first (shared types, interfaces, config) so subtasks don't depend on each other.

2. Route each subtask
   - haiku-worker: mechanical and fully specified - you can say exactly what to change.
   - sonnet-worker: needs some judgment, but is well-scoped.
   - Yourself: architecture, cross-cutting changes, tricky logic, anything security-sensitive.

3. Show me the plan as a table (subtask, worker, files) and wait for my OK before launching workers.

4. Delegate
   - Launch all independent subtasks in parallel in a single step.
   - Give each worker a self-contained brief: goal, exact files, interfaces to respect, how to verify. Workers do not see this conversation.
   - Tell every worker not to commit, push or change git state; you decide that.
   - Pass each subtask's `title` verbatim as the Agent tool's `description` (a re-delegation reuses it too): the agents panel matches runs to planned tasks by it.

5. Integrate
   - Review each worker's changes. Fix or re-delegate anything wrong.
   - If a worker fails or reports a blocker or an open question: answer it and re-brief that worker once. If it still fails, do the subtask yourself and say so in the summary.
   - Run the full test suite / build and fix failures.
   - Summarize what was done and by whom.

Progress bar (optional, needs the savvy-progress plugin)
If the tool `mcp__savvy-progress__progress` appears among your tools, including as a deferred tool, it is available: a deferred tool only needs loading first with ToolSearch (`select:mcp__savvy-progress__progress`). If the tool is absent or ToolSearch does not find it, skip every progress call silently; the rest of this command works without it. Call it:
- right after I approve the plan: `title` (a few words), `total` (number of worker subtasks, not counting work you do yourself), `tasks` (`[{ title, tier, after }]` in plan order; `after` is the numbers of the tasks it waits for), `phase: "delegate"`;
- each time a subtask is accepted in review: `done` (accepted so far), with `phase: "review"` while reviewing and back to `"delegate"` when launching more;
- if re-planning changes the subtasks: the new `tasks` and `total`;
- once at the end: `finished: true`.
The tool only accepts savvy-flow's tier names, so label haiku-worker tasks `light` and sonnet-worker tasks `medium`. This label is cosmetic: it names a planned row in the panel before the worker starts, and does not change which worker runs. Workers report their own steps with `mcp__savvy-progress__step`; they need no extra instruction.
