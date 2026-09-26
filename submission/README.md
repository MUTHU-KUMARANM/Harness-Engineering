# Harness Engineering Submission Evidence

This folder contains offline verification evidence for the four systems in the project rubric. The completed project code and exercise implementations are in their respective project folders.

## Verification status

| System | Automated tests | Run evidence |
| --- | --- | --- |
| Agentic loop | 29 passed | Live claims run not executed; reviewer can generate `summary.md` and a per-turn `stop_reason` trace with an API key |
| Context strategy | 28 passed, 2 skipped | Live retail run not executed; reviewer can generate `budget.json`, `eval.jsonl`, and `eval_control.jsonl` with an API key, then rerun the two skipped checks |
| Claude Code configuration | 35 passed | Validator output is `OK`; `.claude/` configuration is included |
| Multi-shift orchestration | 33 passed | Recorded-response run analyzed 40 fixture defects; `hot_state.json` is 1,037 bytes |

Per the project owner's instruction, no Anthropic API calls were made. No live model output or API spend is represented here. The reviewer should run the API-backed workflows with their own key before assessing run-specific results. A reflection brief requiring live run metrics is not included because those metrics were not generated.

## Evidence folders

- `evidence/system-1-claims/` — full exercise test output.
- `evidence/system-2-retail/` — full exercise test output; two run-artifact checks remain skipped.
- `evidence/system-3-claude-code/` — full test output, validator output, and the `.claude/` structure.
- `evidence/system-4-multi-shift/` — full test output, recorded shift output, scratchpad, hot state, and its byte-size record.
