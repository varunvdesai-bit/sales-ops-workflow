#!/usr/bin/env bash
# Runs every script against the newest week in data/. Stops on the first failure
# except the validator, which exits 1 when it finds ERROR-level data issues (expected).
set -u
cd "$(dirname "$0")"

echo "== 1. Data validation"
python3 "analysis/AI 1 - data quality review/data_validation.py" || echo "(validator found ERROR-level issues, see the report)"

echo; echo "== 2. Plan attainment"
python3 "analysis/AI 2 - plan attainment report/plan_attainment.py"

echo; echo "== 3. Findings retrieval (query: Outbound)"
python3 "analysis/AI 2 - plan attainment report/Knowledge Base/retrieve_findings.py" Outbound

echo; echo "== 4. Outbound deep dive (opens with the Finding 12a sanity check)"
python3 "analysis/AI 3 - eda/outbound_deep_dive.py"

echo; echo "== 5. Funnel and deal economics"
python3 "analysis/AI 3 - eda/sales_funnel_analysis.py"
