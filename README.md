# sales-ops-workflow

An AI-assisted sales ops analysis setup built in Claude Code: weekly data validation, plan attainment
against the right baseline, and exploratory root-cause analysis. All data in this repo is synthetic.

**Design rule: code computes every number. The LLM only writes narrative. A human checks before anything ships.**

## Run it

```bash
pip install -r requirements.txt
./run_all.sh
```

Or one script at a time:

```bash
python3 "analysis/AI 1 - data quality review/data_validation.py"
python3 "analysis/AI 2 - plan attainment report/plan_attainment.py"
python3 "analysis/AI 2 - plan attainment report/Knowledge Base/retrieve_findings.py" Outbound
python3 "analysis/AI 3 - eda/outbound_deep_dive.py"
```

Each script reads the newest folder in `data/`. Pass a week (`... 2026-07-11`) to check an older one,
or set `SALES_DATA_DIR=/path/to/data` to use your own.

## The three workflows

| Workflow | Question it answers | Deterministic step | LLM step (human-reviewed) |
|---|---|---|---|
| AI 1 - data quality | Can I trust this week's CRM extract? | `data_validation.py`: duplicates, missing values, join problems, impossible values, ID-sequence gaps. Exits 1 on any ERROR. | One-page plain-English summary of the report |
| AI 2 - plan attainment | Are we on pace, against the right baseline? | `plan_attainment.py`: blends plan v1 and v2 by effective week, prorates to the last week with data | Executive summary, using `retrieve_findings.py` to pull relevant history from the findings log |
| AI 3 - exploratory | Why did a channel miss? | `outbound_deep_dive.py`, `sales_funnel_analysis.py` | None. Started by a human question, never auto-triggered. |

Each folder has its own `CLAUDE.md` with that workflow's architecture and standards. With these in place,
asking "how are we doing vs plan?" in Claude Code runs the right scripts without naming a file.
The root `CLAUDE.md` holds the shared rules.

## Proof it works

`outbound_deep_dive.py` opens with a sanity check: it must reproduce the headline number from the
findings log (Outbound organic units -61.9% QoQ, ARR -62.5%) before anything else in the file is
trusted. It does, on the data in this repo.

## Where the AI went wrong, and how it was caught

| Mistake | How it was caught | Now enforced by |
|---|---|---|
| Compared 10 weeks of actuals to a full 13-week plan (63% attainment) | Contradicted what I knew about the quarter | Proration to the last week with data, inside `plan_attainment.py` |
| Called a QoQ comparison YoY, inside the findings log itself | Asked it to justify a -4.3% figure | Root `CLAUDE.md`: QoQ or YoY goes in the same sentence as the number |
| Blended units and ARR into one attainment number | Two figures for one channel could not both be true | Units and ARR always reported separately |
| Said a summary file was saved when it was only on screen | Opened the folder, file was missing | Verify deliverables exist before reporting them |
| Presented general industry knowledge as a finding from the data | Asked how it knew; no lead-source field exists | Label outside knowledge or cut it |
| Projected a baseline run-rate as if it were incremental lift | Caught on a draft slide number | `AI 3 - eda/CLAUDE.md`: state which one a projection is |

## Findings log

`analysis/assumptions_and_findings.md` is the project's memory. Later analysis cites a finding by number
instead of re-deriving it. `retrieve_findings.py` does keyword search over it (no embeddings).

## Honest gaps

- Nothing runs unattended. A person opens a session and asks. Scheduling options (launchd, a git repo
  plus a cloud routine, or n8n) are written up in `analysis/AI 1 - data quality review/CLAUDE.md`, not built.
- `retrieve_findings.py` is keyword search. Real RAG is the named next step.
- No automated test suite. The data validator and the Finding 12a sanity check are the guardrails.
