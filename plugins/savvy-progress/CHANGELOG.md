# Changelog

## 1.5.0

- New `currency` setting: `USD` (default) or `EUR`. EUR converts the estimate at a fixed rate (0.86 € per $, `EUR_PER_USD` in `hooks/register.tsx`) and shows it as `0,25 €`.
- `/orchestrate`'s workers get their own crab: `haiku-worker` wears the light tier's racer, `sonnet-worker` the medium tier's chef. Before, both wore the generic costume.

## 1.4.0

- New `background` setting: `dots` (default) keeps the dotted grid behind the desktop agents panel, `none` draws a plain background.

## 1.3.0

- Forked from [johnnyvizz/claude-kit](https://github.com/johnnyvizz/claude-kit) savvy-progress 1.2.1.
- A planned task in `mcp__savvy-progress__progress` may carry `model` and `effort`. The panel shows them in place of the tier's model and effort until the worker starts, so `/orchestrate`'s Haiku and Sonnet tasks no longer show as Opus.
