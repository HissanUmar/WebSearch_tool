"""
SearXNG -> FlashRank(snippets) -> Jina Reader fetch -> structural chunk
        -> FlashRank(chunks, answer-shaped) -> diversity -> context window
        -> answerability gate

Usage:
    python search_tool.py "your query"

Env:
    SEARX_URL       default http://localhost:8080/search
    JINA_API_KEY    optional (higher rate limits on r.jina.ai)
    ANSWER_GATE     "1" to enable post-window answerability check (default "0")
"""
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

import httpx
from flashrank import Ranker, RerankRequest

# ---------- config ----------
SEARX_URL = os.getenv("SEARX_URL", "http://localhost:8080/search")
JINA_KEY = os.getenv("JINA_API_KEY")
ANSWER_GATE = os.getenv("ANSWER_GATE", "0") == "1"

SEARCH_TIMEOUT = 4.0
FETCH_TIMEOUT = 4.0
N_CANDIDATES = 20
N_FETCH = 4
CHUNK_CHARS = 900
MAX_PAGE_CHARS = 30_000
TOP_K = 5
MAX_PER_URL = 2             # per-page cap before final selection
WINDOW_CHARS = 2_000
MIN_CHUNK_CHARS = 80
MIN_WINDOW_SCORE = 0.30     # answerability gate threshold (if enabled)

FETCHED_BOOST = 0.001
PROSE_LINK_RATIO = 0.35

PAGES_DIR = Path("pages")

# Domains that must never reach the model (benchmark contamination).
BLOCKED_URL_PATTERNS = (
    r"huggingface\.co",
    r"arxiv\.org",
    r"openreview\.net",
    r"researchgate\.net",
    r"aclanthology\.org",
    r"etsy\.com/market/",
    r"neurometric\.ai",
)

# Benchmark-contamination signatures.
# A result is dropped if it mentions GAIA (or the GAIA paper author)
# AND at least one of these context markers.
BENCHMARK_MARKERS = (
    "gaia benchmark",
    "gaia-benchmark",
    "gaia dataset",
    "gaia eval",
    "gaia leaderboard",
    "mialon",
    "generalist assistant",
    "validation set",
    "test set",
    "ground truth answer",
    "huggingface.co/datasets",
)

_ranker = Ranker()


# ---------- data ----------
@dataclass
class Chunk:
    text: str
    start: int
    end: int


@dataclass
class Hit:
    """A scored unit headed for the final result list."""
    score: float
    url: str
    title: str
    fetched: bool
    body: str
    meta: dict = field(default_factory=dict)


# ---------- helpers ----------
def norm_url(u: str) -> str:
    p = urlsplit(u)
    path = unquote(p.path).rstrip("/")
    for prefix in ("/article/", "/general/", "/news/"):
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    return urlunsplit((p.scheme, p.netloc.lower(), path, p.query, ""))


def is_blocked(url: str) -> bool:
    return any(re.search(p, url) for p in BLOCKED_URL_PATTERNS)


def slug(url: str) -> str:
    readable = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("://", 1)[-1])[:60].strip("_")
    digest = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{readable}_{digest}.md"

def body_is_contaminated(page: str) -> bool:
    """Drop pages whose fetched body contains the benchmark question."""
    low = page.lower()
    if "gaia" not in low and "mialon" not in low:
        return False
    return any(marker in low for marker in BENCHMARK_MARKERS)

def is_valid_jina_response(text: str) -> bool:
    if not text or len(text) < 200:
        return False
    markers = (
        "Warning: Target URL returned error",
        "Warning: This page maybe requiring CAPTCHA",
        "Warning: This page maybe not yet fully loaded",
    )
    head = text[:500]
    return not any(m in head for m in markers)


def is_prose(text: str) -> bool:
    """True if text is prose-like, not a link/nav dump."""
    if len(text) < 120:
        return False
    link_chars = sum(len(m.group(0)) for m in re.finditer(r"\[[^\]]*\]\([^)]*\)", text))
    if link_chars / len(text) > PROSE_LINK_RATIO:
        return False
    return bool(re.search(r"\b(\w+\s+){3,}\w+[.!?]", text))


def chunk_text(text: str, size: int = CHUNK_CHARS) -> list[Chunk]:
    """Structural chunking: prefer Markdown heading boundaries, fall back to blank lines.
    Returns Chunk objects with offsets so windows are exact."""
    if not text:
        return []

    # Split at headings first; if that yields one giant block, split at blank lines.
    sections = re.split(r"\n(?=#{1,6}\s)", text)
    if len(sections) < 2:
        sections = re.split(r"\n\s*\n", text)

    chunks: list[Chunk] = []
    cursor = 0
    buf, buf_start = "", None

    def flush():
        nonlocal buf, buf_start
        if buf and len(buf) > MIN_CHUNK_CHARS:
            chunks.append(Chunk(buf, buf_start, buf_start + len(buf)))
        buf, buf_start = "", None

    for sec in sections:
        sec_len = len(sec)
        if buf_start is None:
            buf_start = cursor
        if len(buf) + sec_len + 2 <= size:
            buf = f"{buf}\n\n{sec}" if buf else sec
        else:
            flush()
            # hard-split oversized sections
            pos = cursor
            while pos < cursor + sec_len:
                piece = text[pos: pos + size]
                chunks.append(Chunk(piece, pos, pos + len(piece)))
                pos += size
        cursor += sec_len + 1

    flush()
    return [c for c in chunks if is_prose(c.text)]


def context_window(page: str, chunk: Chunk, size: int = WINDOW_CHARS) -> str:
    """Exact window centered on a chunk, using recorded offsets."""
    half = size // 2
    center = (chunk.start + chunk.end) // 2
    start = max(0, center - half)
    end = min(len(page), center + half)
    return page[start:end]


# ---------- scoring ----------
def _passages(texts: list[str], metas: list[dict]) -> list[dict]:
    return [{"id": i, "text": t, "meta": metas[i]} for i, t in enumerate(texts)]


def rerank(query: str, texts: list[str], metas: list[dict], k: int) -> list[dict]:
    if not texts:
        return []
    out = _ranker.rerank(RerankRequest(query=query, passages=_passages(texts, metas)))
    return out[:k]


def rerank_answer_shaped(query: str, texts: list[str], metas: list[dict], k: int) -> list[dict]:
    """Score each text against raw query AND an answer-shaped variant; take the max."""
    if not texts:
        return []
    raw = _ranker.rerank(RerankRequest(query=query, passages=_passages(texts, metas)))
    shaped_query = f"Find the text that answers: {query}"
    shaped = _ranker.rerank(RerankRequest(query=shaped_query, passages=_passages(texts, metas)))

    best: dict[int, dict] = {}
    for a, b in zip(raw, shaped):
        i = a["id"]
        winner = a if a["score"] >= b["score"] else b
        best[i] = winner
    return sorted(best.values(), key=lambda x: x["score"], reverse=True)[:k]


def cap_per_url(hits: list[dict], cap: int = MAX_PER_URL) -> list[dict]:
    """Keep at most `cap` hits per URL, preserving score order."""
    counts: dict[str, int] = {}
    kept = []
    for h in hits:
        url = h["meta"]["url"]
        if counts.get(url, 0) >= cap:
            continue
        counts[url] = counts.get(url, 0) + 1
        kept.append(h)
    return kept


# ---------- stages ----------
async def searx_search(c: httpx.AsyncClient, query: str) -> list[dict]:
    try:
        r = await c.get(
            SEARX_URL,
            params={"q": query, "format": "json", "language": "en"},
            timeout=SEARCH_TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
    except Exception as e:
        print(f"[searx error] {e}", file=sys.stderr)
        return []

    seen, uniq = set(), []
    for x in results:
        u = x.get("url")
        if not u or is_blocked(u):
            continue
        key = norm_url(u)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(x)
    return uniq[:N_CANDIDATES]


async def jina_fetch(c: httpx.AsyncClient, url: str) -> str | None:
    headers = {"Accept": "text/plain", "X-Retain-Images": "none"}
    if JINA_KEY:
        headers["Authorization"] = f"Bearer {JINA_KEY}"
    try:
        r = await asyncio.wait_for(
            c.get(f"https://r.jina.ai/{url}", headers=headers), timeout=FETCH_TIMEOUT
        )
    except Exception:
        return None
    if r.status_code != 200 or not is_valid_jina_response(r.text):
        return None
    text = r.text[:MAX_PAGE_CHARS]
    PAGES_DIR.mkdir(exist_ok=True)
    (PAGES_DIR / slug(url)).write_text(
        f"<!-- source: {url} -->\n\n{text}", encoding="utf-8"
    )
    return text


# ---------- pipeline ----------
async def run(query: str) -> dict:
    t0 = time.perf_counter()
    timings: dict[str, float] = {}

    async with httpx.AsyncClient(follow_redirects=True, http2=False) as c:
        results = await searx_search(c, query)
        timings["search"] = round(time.perf_counter() - t0, 3)
        if not results:
            return {"query": query, "results": [], "timings": timings}

        t = time.perf_counter()
        snippets = [f"{x.get('title', '')}. {x.get('content', '')}" for x in results]
        top = await asyncio.to_thread(rerank, query, snippets, results, N_FETCH)
        timings["rerank_snippets"] = round(time.perf_counter() - t, 3)

        t = time.perf_counter()
        pages = await asyncio.gather(*[jina_fetch(c, p["meta"]["url"]) for p in top])
        timings["fetch"] = round(time.perf_counter() - t, 3)

    # --- chunk, chunk-with-offset, keep prose ---
    t = time.perf_counter()
    texts, metas, chunks_by_url = [], [], {}
    for p, page in zip(top, pages):
        url = p["meta"]["url"]
        src = {"url": url, "title": p["meta"].get("title", ""), "fetched": page is not None}
        
        if page and body_is_contaminated(page):
            print(f"[warn] contamination in body of {url}, dropping", file=sys.stderr)
            page = None  
        
            chunks = chunk_text(page)
            chunks_by_url[url] = chunks
            for ch in chunks:
                texts.append(ch.text)
                metas.append(src)
            if not chunks:
                print(f"[warn] no prose chunks for {url}, using snippet", file=sys.stderr)
                texts.append(p["text"])
                metas.append(src)
        else:
            texts.append(p["text"])
            metas.append(src)

    # --- answer-shaped rerank + diversity ---
    best = await asyncio.to_thread(rerank_answer_shaped, query, texts, metas, TOP_K * 2)
    best = cap_per_url(best, MAX_PER_URL)[:TOP_K]
    timings["rerank_chunks"] = round(time.perf_counter() - t, 3)

    # --- build windows (exact offsets) ---
    page_of = {p["meta"]["url"]: pg for p, pg in zip(top, pages) if pg is not None}
    chunk_index: dict[str, dict[str, Chunk]] = {
        url: {c.text: c for c in chs} for url, chs in chunks_by_url.items()
    }


    hits: list[Hit] = []
    for b in best:
        url = b["meta"]["url"]
        page = page_of.get(url)
        if page:
            ch = chunk_index.get(url, {}).get(b["text"])
            body = context_window(page, ch) if ch else b["text"]
            if not is_prose(body):
                body = b["text"]  # window was nav-dominated; fall back
        else:
            body = b["text"]
        boost = FETCHED_BOOST if b["meta"]["fetched"] else 0.0
        hits.append(Hit(
            score=float(b["score"]) + boost,
            url=url,
            title=b["meta"]["title"],
            fetched=b["meta"]["fetched"],
            body=body,
            meta=b["meta"],
        ))

    # --- optional answerability gate ---
    if ANSWER_GATE and hits:
        gate_texts = [h.body for h in hits]
        gate_metas = [{"url": h.url, "title": h.title, "fetched": h.fetched} for h in hits]
        gated = await asyncio.to_thread(rerank, query, gate_texts, gate_metas, len(hits))
        keep_urls = {g["meta"]["url"] for g in gated if g["score"] >= MIN_WINDOW_SCORE}
        if keep_urls:
            hits = [h for h in hits if h.url in keep_urls]

    hits.sort(key=lambda h: h.score, reverse=True)
    timings["total"] = round(time.perf_counter() - t0, 3)

    return {
        "query": query,
        "results": [
            {
                "score": round(h.score, 4),
                "url": h.url,
                "title": h.title,
                "fetched": h.fetched,
                "text": h.body,
            }
            for h in hits
        ],
        "timings": timings,
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "what is a cross-encoder reranker"
    print(json.dumps(asyncio.run(run(q)), indent=2, ensure_ascii=False))