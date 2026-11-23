# Changelog

## 1.1.0 – 2026-11-23

- New `--worktree` option: `/orchestrate --worktree <task>` runs each worker in its own git worktree, so parallel test runs and builds can't collide. The orchestrator commits shared groundwork first and applies each worker's changes to your folder after reviewing them. It needs `worktree.baseRef` set to `"head"` and asks to add it to the project's `.claude/settings.local.json` if missing; your folder must otherwise be clean.
- Without the option, workers share your folder as in 1.0.0. The plan suggests `--worktree` when workers would build or test at the same time.
- The command only launches the `orchestrate:` workers, never same-named workers of your own.

## 1.0.0 – 2026-11-09

- First release: `/orchestrate` plans a task with the session model and implements subtasks in parallel with Haiku and Sonnet workers.
