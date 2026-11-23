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
   - Do shared groundwork yourself first (shared types, interfaces, config) so subtasks don't depend on each other. Workers run in their own git worktrees, which start from the last commit, so the groundwork gets committed before workers launch (step 4).

2. Route each subtask
   - haiku-worker: mechanical and fully specified - you can say exactly what to change.
   - sonnet-worker: needs some judgment, but is well-scoped.
   - Yourself: architecture, cross-cutting changes, tricky logic, anything security-sensitive.

3. Show me the plan as a table (subtask, worker, files) and wait for my OK before launching workers. If there is groundwork, add one line under the table naming the files you will commit as groundwork; my OK covers that commit.

4. Delegate
   - Isolation: if `git rev-parse HEAD` fails (not a git repo, or no commits yet), skip the groundwork commit, clean check and base check below, launch workers without `isolation` in this folder, and tell me they share it.
   - Groundwork commit: stage only the groundwork files by path and commit them as `orchestrate: groundwork for <task>`. No groundwork, no commit. Either way, note `BASE=$(git rev-parse HEAD)`.
   - Clean check: if `git status --porcelain` then shows anything, stop and ask me whether to commit it, stash it, or run without isolation. Never stash or discard my changes yourself.
   - Launch all independent subtasks in parallel in a single step, each with the Agent tool's `isolation: "worktree"`. Tell each worker it works in its own checkout of the repo.
   - Base check: for every worker that comes back with a worktree, before using its changes, run `git -C <worktree> merge-base --is-ancestor $BASE HEAD`. If it fails, that worktree did not start from BASE: discard its changes (never apply them), remove the worktree, tell me, and redo that subtask without isolation in this folder, one subtask at a time.
   - Give each worker a self-contained brief: goal, exact files, interfaces to respect, how to verify. Workers do not see this conversation. Give file paths relative to the repo root, never this folder's absolute path, or the worker edits this folder instead of its own checkout. Its checkout has no gitignored files (dependencies, `.env`, build caches): tell it to install what the checks need, or to report that it could not run them.
   - Tell every worker not to commit, push or change git state; you decide that.
   - Pass each subtask's `title` verbatim as the Agent tool's `description` (a re-delegation reuses it too): the agents panel matches runs to planned tasks by it.

5. Integrate
   - Bring in each worker's changes one at a time. A worker that changed nothing has no worktree left; skip it. For the others, using the worktree path and branch the Agent result reports:
     ```bash
     git -C <worktree> add -A   # includes new files; this only stages, inside the worker's checkout
     git -C <worktree> diff --cached --binary > <scratch dir>/worker-<n>.patch
     ```
     Review the patch. If it is right, `git apply <scratch dir>/worker-<n>.patch` in this folder; if `git apply` fails, fix it by hand or re-delegate, never overwrite.
   - Remove a worktree (`git worktree remove --force <worktree>`, then `git branch -D <its branch>`) only once its changes are applied, or once you have decided to drop or re-delegate that subtask.
   - Fix or re-delegate anything wrong.
   - If a worker fails or reports a blocker or an open question: answer it and re-brief it once, as a new Agent call with a full brief (it gets a fresh worktree; the old one's changes are not carried over). If it still fails, do the subtask yourself and say so in the summary.
   - Run the full test suite / build and fix failures.
   - Summarize what was done and by whom.

Progress bar (optional, needs the savvy-progress plugin)
If the tool `mcp__savvy-progress__progress` appears among your tools, including as a deferred tool, it is available: a deferred tool only needs loading first with ToolSearch (`select:mcp__savvy-progress__progress`). If the tool is absent or ToolSearch does not find it, skip every progress call silently; the rest of this command works without it. Call it:
- right after I approve the plan: `title` (a few words), `total` (number of worker subtasks, not counting work you do yourself), `tasks` (`[{ title, tier, after }]` in plan order; `after` is the numbers of the tasks it waits for), `phase: "delegate"`;
- each time a subtask is accepted in review: `done` (accepted so far), with `phase: "review"` while reviewing and back to `"delegate"` when launching more;
- if re-planning changes the subtasks: the new `tasks` and `total`;
- once at the end: `finished: true`.
The tool only accepts savvy-flow's tier names, so label haiku-worker tasks `light` and sonnet-worker tasks `medium`. This label is cosmetic: it names a planned row in the panel before the worker starts, and does not change which worker runs. Workers report their own steps with `mcp__savvy-progress__step`; they need no extra instruction.
