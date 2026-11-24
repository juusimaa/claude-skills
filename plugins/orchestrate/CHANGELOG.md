# Changelog

## 1.1.2 – 2026-11-24

- Planned tasks sent to savvy-progress now carry `model` and `effort`, so the agents panel shows Haiku and Sonnet before workers start, not Opus. Needs savvy-progress 1.3.0 from this repository; the original 1.2.1 ignores the new fields.

## 1.1.1 – 2026-11-23

- The progress report is now a required part of steps 4 and 5 whenever savvy-progress is installed. Orchestrators were skipping the optional section at the end, so the progress bar above the prompt never appeared.

## 1.1.0 – 2026-11-23

- New `--worktree` option: `/orchestrate --worktree <task>` runs each worker in its own git worktree, so parallel test runs and builds can't collide. The orchestrator commits shared groundwork first and applies each worker's changes to your folder after reviewing them. It needs `worktree.baseRef` set to `"head"` and asks to add it to the project's `.claude/settings.local.json` if missing; your folder must otherwise be clean.
- Without the option, workers share your folder as in 1.0.0. The plan suggests `--worktree` when workers would build or test at the same time.
- The command only launches the `orchestrate:` workers, never same-named workers of your own.

## 1.0.0 – 2026-11-09

- First release: `/orchestrate` plans a task with the session model and implements subtasks in parallel with Haiku and Sonnet workers.
