# Harness Engineering Submission Evidence

This folder contains the available evidence for the four systems in the project rubric. The project source and exercise implementations are in their respective project folders.

## Verification status

| System | Automated tests | Run evidence |
| --- | --- | --- |
| Agentic loop | 29 passed | Pending live claims run: `summary.md` and a per-turn `stop_reason` trace |
| Context strategy | 28 passed, 2 skipped | Pending live retail run: `budget.json`, `eval.jsonl`, and `eval_control.jsonl`; these two tests require those run artifacts |
| Claude Code configuration | 35 passed | Validator output is `OK`; `.claude/` configuration is included |
| Multi-shift orchestration | 33 passed | Recorded-response run analyzed 40 fixture defects; `hot_state.json` is 1,037 bytes |

The claims and retail run artifacts require `ANTHROPIC_API_KEY`. No key was configured during this verification, so no live run output or API spend is represented here. Do not treat this evidence set as final until those artifacts and the reflection brief have been added.

## Evidence folders

- `evidence/system-1-claims/` — full exercise test output.
- `evidence/system-2-retail/` — full exercise test output; two run-artifact checks remain skipped.
- `evidence/system-3-claude-code/` — full test output, validator output, and the `.claude/` structure.
- `evidence/system-4-multi-shift/` — full test output, recorded shift output, scratchpad, hot state, and its byte-size record.
