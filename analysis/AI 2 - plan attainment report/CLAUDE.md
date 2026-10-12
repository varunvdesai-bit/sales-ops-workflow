# CLAUDE.md — AI 2: Plan Attainment Report

Layered on top of the root `CLAUDE.md`. This folder's job: answer "are we on pace," grounded in the
correct plan baseline and the engagement's own historical context — not just this week's raw numbers
in isolation.

## Architecture

```
data/<newest dated folder>
        |
        v
plan_attainment.py                  (deterministic pandas -- v1/v2 plan blending,
                                      proration to latest week with data)
        |
        v
Knowledge Base/retrieve_findings.py  (deterministic text search over the findings log,
                                      returns the sections relevant to this week's numbers)
        |
        +-------------------+
        |                   |
        v                   v
  plan_attainment       relevant findings
  output (numbers)      (historical context)
        |                   |
        +---------+---------+
                  v
      Claude Code synthesis (below)   (LLM step -- executive summary: performance,
                                        trends, recommended follow-up questions)
                  |
                  v
            HUMAN REVIEW               (required before distribution)
```

`retrieve_findings.py` treats `analysis/assumptions_and_findings.md` as the knowledge base, rather
than a second, separate store of the same information — deterministic substring search over the
log's 23 sections (no embeddings, no ranking model), transparent and good enough at this size. If a
different knowledge base is meant to exist instead, its `KB_PATH` constant is the only line that
needs to change. Real RAG (embeddings, semantic retrieval) is the named target once the knowledge
base outgrows substring search — see the README — not built yet.

## Answering questions without being told which script to run

When asked anything about plan attainment, pacing, performance this week, or "how are we doing":

```bash
python3 "analysis/AI 2 - plan attainment report/plan_attainment.py"
python3 "analysis/AI 2 - plan attainment report/Knowledge Base/retrieve_findings.py" <query>
```

Then write the executive summary with both outputs in context:

> Using this week's plan attainment numbers and the retrieved findings-log sections, write an
> executive summary: (1) performance — where we stand vs. plan, units and ARR, stated separately;
> (2) trends — what changed from the retrieved historical context, and whether this week continues,
> breaks, or is too early to say relative to a known pattern; (3) recommended follow-up questions —
> specific, answerable questions a human should chase next, not generic ones. Label anything you
> cannot verify as an open question, not a conclusion.

Save as `plan_attainment_summary_<week>.md`, in this same folder. Same intent-triggered-not-scheduled
caveat as the data quality folder — see its `CLAUDE.md` for the real automation constraint (no local
file access from a cloud routine, no git repo here) and the n8n target architecture.

## Standards for this folder specifically

- **`plan_attainment.py`'s core logic — know this before explaining any number it produces:**
  - FY26Q4 has two plan versions (v1 original, v2 Finance's mid-quarter revision). The script blends
    them: v1 for early weeks, v2 from the week the revision took effect onward, with the switchover
    week derived from the plan data itself (`plan_version == "v2"`), never hardcoded.
  - In-progress quarters are compared only through the last week actual data exists — a partial
    quarter's actuals never get compared against a full quarter's plan.
  - Comparisons use PLAN, not QUOTA — quota is a single current snapshot per rep with no history, so
    it can't be trusted for past-quarter comparisons.
- **Units and ARR are always reported separately, never blended into one ratio.** A channel can be
  under on units and over on ARR (or vice versa) — collapsing that into one number hides the actual
  story every time it happens.
- **Always state whether a comparison is QoQ or YoY, explicitly, in the same sentence as the number.**
  This has been the single most common real error in this engagement (including inside the findings
  log's own prose once) — don't let a channel/quarter pairing go unnamed.
