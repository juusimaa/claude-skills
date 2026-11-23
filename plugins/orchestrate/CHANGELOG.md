# Changelog

## 1.1.0 – 2026-11-23

- Each worker runs in its own git worktree, so parallel test runs and builds no longer collide. The orchestrator commits shared groundwork before workers launch and applies each worker's changes to your folder after reviewing them.
- Your folder must have no other uncommitted changes when workers launch; the orchestrator asks you if it does. Without git, workers share the folder as before.
- Worktrees need `worktree.baseRef` set to `"head"`; the orchestrator asks to add it to the project's `.claude/settings.local.json` if it is missing.
- The worker definitions request worktree isolation themselves, and the command only launches the `orchestrate:` workers, never same-named workers of your own.

## 1.0.0 – 2026-11-09

- First release: `/orchestrate` plans a task with the session model and implements subtasks in parallel with Haiku and Sonnet workers.
