"""
SearXNG -> FlashRank(snippets) -> Jina Reader fetch -> chunk -> FlashRank(chunks) -> context window

Usage:
    python search_tool.py "your query"

Env:
    SEARX_URL     default http://localhost:8080/search
    JINA_API_KEY  optional (higher rate limits on r.jina.ai)
"""
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

import httpx
from flashrank import Ranker, RerankRequest

# ---------- config ----------
SEARX_URL = os.getenv("SEARX_URL", "http://localhost:8080/search")
JINA_KEY = os.getenv("JINA_API_KEY")  # set this env var; no hardcoded default

SEARCH_TIMEOUT = 4.0
FETCH_TIMEOUT = 4.0
N_CANDIDATES = 20
N_FETCH = 4
CHUNK_CHARS = 800
MAX_PAGE_CHARS = 30_000
TOP_K = 5
WINDOW_CHARS = 2_000        # parent context returned per winning page
MIN_CHUNK_CHARS = 80

FETCHED_BOOST = 0.001

PAGES_DIR = Path("pages")
_ranker = Ranker()


# ---------- helpers ----------
def norm_url(u: str) -> str:
    p = urlsplit(u)
    path = unquote(p.path).rstrip("/")
    for prefix in ("/article/", "/general/", "/news/"):
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    return urlunsplit((p.scheme, p.netloc.lower(), path, p.query, ""))


def _slug(url: str) -> str:
    readable = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("://", 1)[-1])[:60].strip("_")
    digest = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{readable}_{digest}.md"


def is_valid_jina_response(text: str) -> bool:
    if not text or len(text) < 200:
        return False
    error_markers = (
        "Warning: Target URL returned error",
        "Warning: This page maybe requiring CAPTCHA",
        "Warning: This page maybe not yet fully loaded",
    )
    head = text[:500]
    return not any(m in head for m in error_markers)


def chunk_text(text: str, size: int = CHUNK_CHARS) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 1 <= size:
            buf = f"{buf}\n{p}" if buf else p
        else:
            if buf:
                chunks.append(buf)
            while len(p) > size:
                chunks.append(p[:size])
                p = p[size:]
            buf = p
    if buf:
        chunks.append(buf)
    return [c for c in chunks if len(c) > MIN_CHUNK_CHARS]


def rerank(query: str, texts: list[str], metas: list[dict], k: int) -> list[dict]:
    if not texts:
        return []
    passages = [{"id": i, "text": t, "meta": metas[i]} for i, t in enumerate(texts)]
    return _ranker.rerank(RerankRequest(query=query, passages=passages))[:k]


def context_window(page: str, needle: str, size: int = WINDOW_CHARS) -> str:
    """Return a ~size-char window of `page` centered on `needle`."""
    idx = page.find(needle)
    if idx == -1:
        return page[:size]
    half = size // 2
    start = max(0, idx - half)
    end = min(len(page), idx + len(needle) + half)
    return page[start:end]

def is_prose_chunk(chunk: str) -> bool:
    """Reject chunks dominated by markdown links (nav menus, footers, sitemaps)."""
    if len(chunk) < 120:
        return False

    # Total characters consumed by markdown links [text](url)
    link_chars = sum(len(m.group(0)) for m in re.finditer(r"\[[^\]]*\]\([^)]*\)", chunk))
    link_ratio = link_chars / len(chunk)

    # Nav chunks are typically >35% link markup
    if link_ratio > 0.35:
        return False

    # Require sentence-like structure: at least one run of 4+ words ending in punctuation
    if not re.search(r"\b(\w+\s+){3,}\w+[.!?]", chunk):
        return False

    return True

def snippet_quality(r: dict) -> float:
    content = r.get("content", "") or ""
    # Prefer longer snippets (topic pages have short blurbs, articles have real excerpts)
    return min(len(content) / 500.0, 1.0) * 0.001


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
        if not u:
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
    (PAGES_DIR / _slug(url)).write_text(
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

    t = time.perf_counter()
    texts, metas = [], []
    for p, page in zip(top, pages):
        src = {
            "url": p["meta"]["url"],
            "title": p["meta"].get("title", ""),
            "fetched": page is not None,
        }
        pieces = [c for c in chunk_text(page) if is_prose_chunk(c)] if page else []
        if not pieces:
            pieces = [p["text"]]
            print(f"[warn] no valid chunks for {src['url']}, using snippet instead", file=sys.stderr)
        for ch in pieces:
            texts.append(ch)
            metas.append(src)

    best = await asyncio.to_thread(rerank, query, texts, metas, TOP_K)

    # parent-child: return a window from each winning page's best chunk
    # Build page_of from top/pages directly (1:1), NOT from metas
    page_of = {
        p["meta"]["url"]: page
        for p, page in zip(top, pages)
        if page is not None
    }

    ranked = []
    for b in best:
        boost = FETCHED_BOOST if b["meta"]["fetched"] else 0.0
        ranked.append((float(b["score"]) + boost, b))
    ranked.sort(key=lambda x: x[0], reverse=True)


    seen_urls = set()
    results_out = []
    for final_score, b in ranked:
        url = b["meta"]["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        page = page_of.get(url)
        body = context_window(page, b["text"]) if page else b["text"]
        results_out.append(
            {
                "score": round(final_score, 4),
                "url": url,
                "title": b["meta"]["title"],
                "fetched": b["meta"]["fetched"],
                "text": body,
            }
        )


    timings["rerank_chunks"] = round(time.perf_counter() - t, 3)
    timings["total"] = round(time.perf_counter() - t0, 3)
    return {"query": query, "results": results_out, "timings": timings}


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "what is a cross-encoder reranker"
    print(json.dumps(asyncio.run(run(q)), indent=2, ensure_ascii=False))