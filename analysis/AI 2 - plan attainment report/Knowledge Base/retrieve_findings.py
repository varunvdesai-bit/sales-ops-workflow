"""
Retrieval step for the Weekly Plan Attainment Report (Use Case 2).

Honest note on scope: the workflow description calls for "an existing knowledge base" providing
historical context. As of this build, no separate knowledge base exists in this project -- there
is no populated "Knowledge Base" folder anywhere in analysis/. The closest real thing is
analysis/assumptions_and_findings.md, the findings log already built and used throughout this
engagement. This script treats that log AS the knowledge base rather than inventing a second,
duplicate store of historical context -- confirm this is the intended source before relying on it;
if a different knowledge base is meant to exist, this script's KB_PATH is the only line to change.

What this script does: splits the findings log into its numbered sections and returns the ones
relevant to a given channel or keyword, so a synthesis step (see README.md in this folder) gets
targeted historical context instead of the entire ~70KB log. Deterministic text search only --
no model call happens in this file.
"""
import re
from pathlib import Path

KB_PATH = Path(__file__).resolve().parents[2] / "assumptions_and_findings.md"

_HEADER_RE = re.compile(r"^(##|###) (Finding \d+[a-z]?.*|Baseline decisions.*)$", re.MULTILINE)


def load_sections(kb_path: Path = KB_PATH) -> list[dict]:
    """
    Splits the findings log into {title, level, body} sections at each ## / ### Finding header
    (and the Baseline decisions section). Returns them in document order.
    """
    text = kb_path.read_text()
    matches = list(_HEADER_RE.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append({
            "title": m.group(2).strip(),
            "level": len(m.group(1)),
            "body": text[start:end].strip(),
        })
    return sections


def retrieve(query: str, kb_path: Path = KB_PATH, max_results: int = 5) -> list[dict]:
    """
    Case-insensitive substring match against each section's title + body. Returns the top
    max_results sections by number of query-term occurrences, highest first. Ties broken by
    document order (earlier findings first).

    This is intentionally simple (no embeddings, no ranking model) -- the findings log is small
    enough (23 sections) that substring search over section text is transparent and auditable,
    which matters more here than recall on a fuzzier query.
    """
    sections = load_sections(kb_path)
    terms = [t.lower() for t in query.split()]

    scored = []
    for idx, s in enumerate(sections):
        haystack = (s["title"] + " " + s["body"]).lower()
        score = sum(haystack.count(t) for t in terms)
        if score > 0:
            scored.append((score, -idx, s))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [s for _, _, s in scored[:max_results]]


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "Outbound"
    results = retrieve(query)
    print(f"Query: {query!r} -- {len(results)} matching section(s)\n")
    for r in results:
        print(f"{'#' * r['level']} {r['title']}")
        print(r["body"][:300].strip() + ("..." if len(r["body"]) > 300 else ""))
        print()
