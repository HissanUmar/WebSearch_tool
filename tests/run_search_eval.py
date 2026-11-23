"""
tests/run_search_eval.py

Runs every question in the GAIA Level-1 search set through search_tool.run(),
checks whether the expected answer string appears in any returned window,
and writes:
    eval_out/results.json   raw per-question data
    eval_out/report.html    green/red visual report

Usage:
    python -m tests.run_search_eval
"""
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from search_tool import run as run_search

OUT_DIR = Path("eval_out")
OUT_DIR.mkdir(exist_ok=True)

# ---------- test set ----------
# (task_id, expected_answer, question)
QUESTIONS = [
    ("e1fc63a2-da7a-432f-be78-7c4a95598703", "17",
     "If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon its closest approach? Please use the minimum perigee value on the Wikipedia page for the Moon when carrying out your calculation. Round your result to the nearest 1000 hours and do not use any comma separators if necessary."),
    ("8e867cd7-cff9-4e6c-867a-ff5ddc2550be", "3",
     "How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia."),
    ("ec09fa32-d03f-4bf8-84b0-1f16922c3ae4", "3",
     "You have been selected to play the final round of the hit new game show 'Pick That Ping-Pong'. A device consisting of a winding clear ramp and a series of pistons controls the outcome of the game. The ramp begins with 100 numbered ping-pong balls, arranged in ascending order from 1 to 100. Which ball should you choose to maximize your odds of winning the big prize? Please provide your answer as the number of the ball selected."),
    ("5d0080cb-90d7-4712-bc33-848150e917d3", "0.1777",
     "What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper 'Can Hiccup Supply Enough Fish to Maintain a Dragon's Diet?'"),
    ("46719c30-f4c3-4cad-be07-d5cb21eee6bb", "Mapping Human Oriented Information to Software Agents for Online Systems Usage",
     "Of the authors (First M. Last) that worked on the paper 'Pie Menus or Linear Menus, Which Is Better?' in 2015, what was the title of the first paper authored by the one that had authored prior papers?"),
    ("4b6bb5f7-f634-410e-815d-e673ab7f8632", "THE CASTLE",
     "In Series 9, Episode 11 of Doctor Who, the Doctor is trapped inside an ever-shifting maze. What is this location called in the official script for the episode? Give the setting exactly as it appears in the first scene heading."),
    ("dc28cf18-6431-458b-83ef-64b3ce566c10", "2",
     "My family reunion is this week, and I was assigned the mashed potatoes to bring. The attendees include my married mother and father, my twin brother and his family, my aunt and her family, my grandma and her brother, her brother's daughter, and his daughter's family. All the adults but me have been married, and no one is divorced or remarried, but my grandpa and my grandma's sister-in-law passed away last year. All living spouses are attending. My brother has two children that are still kids, my aunt has one six-year-old, and my grandma's brother's daughter has three kids under 12. I figure each adult will eat about 1.5 potatoes of mashed potatoes and each kid will eat about 1/2 a potato of mashed potatoes, except my second cousins don't eat carbs. The average potato is about half a pound, and potatoes are sold in 5-pound bags. How many whole bags of potatoes do I need? Just give the number."),
    ("b816bfce-3d80-4913-a07d-69b752ce6377", "fluffy",
     "In Emily Midkiff's June 2014 article in a journal named for the one of Hreidmar's sons that guarded his house, what word was quoted from two different authors in distaste for the nature of dragon depictions?"),
    ("72e110e7-464c-453c-a309-90a95aed6538", "Guatemala",
     "Under DDC 633 on Bielefeld University Library's BASE, as of 2020, from what country was the unknown language article with a flag unique from the others?"),
    ("b415aba4-4b68-4fc6-9b89-2c812e55a3e1", "diamond",
     "In Nature journal's Scientific Reports conference proceedings from 2012, in the article that did not mention plasmons or plasmonics, what nano-compound is studied? Don't use the prefix nano in your answer if there is one."),
]


# ---------- matching ----------
def answer_in_text(expected: str, text: str) -> bool:
    """Case-insensitive substring match, with light normalization."""
    if not text:
        return False
    exp = expected.strip().lower()
    hay = text.lower()
    if exp in hay:
        return True
    # normalize whitespace and punctuation variants
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^\w\s.]", " ", s)).strip()
    return norm(exp) in norm(hay)


def find_matches(expected: str, results: list[dict]) -> list[dict]:
    """Return which results contain the expected answer."""
    out = []
    for r in results:
        if answer_in_text(expected, r.get("text", "")):
            out.append({"url": r["url"], "title": r["title"], "score": r["score"]})
    return out


def snippet_matches(expected: str, results: list[dict]) -> bool:
    """Also check the search snippets, not just fetched windows."""
    for r in results:
        if answer_in_text(expected, r.get("snippet", "")):
            return True
    return False


# ---------- runner ----------
async def run_one(task_id: str, expected: str, question: str) -> dict:
    print(f"\n[{task_id[:8]}] {question[:70]}...", flush=True)
    try:
        result = await run_search(question)
    except Exception as e:
        return {
            "task_id": task_id,
            "expected": expected,
            "question": question,
            "error": str(e),
            "hit": False,
            "results": [],
        }

    results = result.get("results", [])
    matches = find_matches(expected, results)
    hit = len(matches) > 0

    print(f"  expected={expected!r}  hit={hit}  "
          f"n_results={len(results)}  matches={len(matches)}", flush=True)

    return {
        "task_id": task_id,
        "expected": expected,
        "question": question,
        "hit": hit,
        "matches": matches,
        "results": results,
        "timings": result.get("timings", {}),
    }


async def main():
    rows = []
    for task_id, expected, question in QUESTIONS:
        rows.append(await run_one(task_id, expected, question))

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(rows),
        "hits": sum(1 for r in rows if r["hit"]),
        "rows": rows,
    }
    (OUT_DIR / "results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "report.html").write_text(render_html(payload), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Hit rate: {payload['hits']}/{payload['total']}")
    print(f"Wrote {OUT_DIR/'results.json'}")
    print(f"Wrote {OUT_DIR/'report.html'}")


# ---------- html ----------
def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight(text: str, expected: str) -> str:
    """Escape text and wrap occurrences of expected in <mark>."""
    if not text:
        return ""
    t = esc(text)
    if not expected:
        return t
    # case-insensitive literal highlight
    pattern = re.escape(esc(expected))
    return re.sub(f"(?i)({pattern})", r"<mark>\1</mark>", t)


def render_html(payload: dict) -> str:
    rows_html = []
    for r in payload["rows"]:
        status = "hit" if r["hit"] else ("error" if r.get("error") else "miss")
        badge = {"hit": "✅ HIT", "miss": "❌ MISS", "error": "⚠️ ERROR"}[status]

        results_html = []
        for res in r.get("results", []):
            contains = answer_in_text(r["expected"], res.get("text", ""))
            cls = "contains" if contains else ""
            results_html.append(f"""
            <div class="result {cls}">
              <div class="meta">
                <span class="score">{res['score']}</span>
                <span class="fetched">{'fetched' if res['fetched'] else 'snippet'}</span>
                <a href="{esc(res['url'])}" target="_blank">{esc(res['title'] or res['url'])}</a>
              </div>
              <pre>{highlight(res.get('text','')[:1500], r['expected'])}</pre>
            </div>""")

        err = f'<div class="error">{esc(r["error"])}</div>' if r.get("error") else ""
        timings = r.get("timings", {})
        timing_str = " · ".join(f"{k}={v}s" for k, v in timings.items())

        rows_html.append(f"""
        <section class="question {status}">
          <header>
            <span class="badge {status}">{badge}</span>
            <span class="taskid">{esc(r['task_id'][:8])}</span>
            <span class="expected">expected: <code>{esc(r['expected'])}</code></span>
            <span class="timings">{esc(timing_str)}</span>
          </header>
          <p class="qtext">{esc(r['question'][:300])}{'…' if len(r['question'])>300 else ''}</p>
          {err}
          <div class="results">{''.join(results_html) or '<em>no results</em>'}</div>
        </section>""")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Search Tool Eval — {payload['hits']}/{payload['total']}</title>
<style>
  :root {{ --green:#0a7d32; --red:#b3261e; --amber:#a15c00; --bg:#0f1115; --card:#181b22; --line:#2a2f3a; --fg:#e6e6e6; }}
  body {{ font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); margin:0; padding:24px; }}
  h1 {{ margin:0 0 4px; font-size:20px; }}
  .summary {{ color:#9aa4b2; margin-bottom:24px; }}
  section.question {{ background:var(--card); border-left:4px solid var(--line); border-radius:6px; padding:14px 16px; margin-bottom:16px; }}
  section.question.hit {{ border-left-color:var(--green); }}
  section.question.miss {{ border-left-color:var(--red); }}
  section.question.error {{ border-left-color:var(--amber); }}
  header {{ display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; margin-bottom:8px; }}
  .badge {{ font-weight:700; padding:2px 8px; border-radius:4px; font-size:12px; }}
  .badge.hit {{ background:#10361f; color:#7ee2a8; }}
  .badge.miss {{ background:#3a1412; color:#ff9c95; }}
  .badge.error {{ background:#3a2a10; color:#ffc36b; }}
  .taskid {{ color:#9aa4b2; font-family:ui-monospace,monospace; }}
  .expected code {{ background:#20242e; padding:1px 6px; border-radius:3px; color:#ffd479; }}
  .timings {{ color:#6f7a8a; font-size:12px; margin-left:auto; font-family:ui-monospace,monospace; }}
  .qtext {{ color:#c8d0da; margin:6px 0 12px; }}
  .results {{ display:flex; flex-direction:column; gap:10px; }}
  .result {{ background:#11141a; border:1px solid var(--line); border-radius:5px; padding:10px; }}
  .result.contains {{ border-color:var(--green); box-shadow:0 0 0 1px var(--green) inset; }}
  .result .meta {{ display:flex; gap:10px; align-items:baseline; margin-bottom:6px; flex-wrap:wrap; }}
  .result a {{ color:#7fb8ff; text-decoration:none; }}
  .result a:hover {{ text-decoration:underline; }}
  .score {{ font-family:ui-monospace,monospace; color:#ffd479; }}
  .fetched {{ font-size:11px; color:#9aa4b2; border:1px solid var(--line); padding:0 6px; border-radius:10px; }}
  .result pre {{ margin:0; white-space:pre-wrap; word-break:break-word; font:13px/1.45 ui-monospace,monospace; color:#c8d0da; max-height:260px; overflow:auto; }}
  mark {{ background:#ffd479; color:#111; padding:0 2px; border-radius:2px; }}
  .error {{ color:#ff9c95; margin:8px 0; font-family:ui-monospace,monospace; }}
</style></head><body>
<h1>Search Tool Eval</h1>
<div class="summary">
  {payload['hits']}/{payload['total']} questions have the expected answer in at least one returned window ·
  generated {esc(payload['generated_at'])}
</div>
{''.join(rows_html)}
</body></html>"""


if __name__ == "__main__":
    asyncio.run(main())