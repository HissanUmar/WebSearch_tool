<!-- source: https://deepseekai.guide/api/deepseek-api-rate-limits/ -->

Title: DeepSeek API Rate Limits: How They Actually Work (2026)

URL Source: https://deepseekai.guide/api/deepseek-api-rate-limits/

Published Time: 2026-04-25T13:32:37+00:00

Markdown Content:
You wired up `deepseek-flash`, the smoke test passed, and the first real batch fell over with a wall of HTTP 429s. DeepSeek API rate limits are not a requests-per-minute table: DeepSeek’s [Rate Limit & Isolation page](https://api-docs.deepseek.com/quick_start/rate_limit/) sets a **concurrency limit per account** — 2,500 in-flight requests for `deepseek-flash` and 500 for `deepseek-v4-pro` (October 2026) — and answers anything above it with a 429. Its Error Codes page adds that a 429 can also mean you are sending requests too quickly or have exceeded a QPS limit.

This guide walks through what DeepSeek documents, what happens at the wire level while a request waits, and the client patterns that keep traffic flowing.

## What DeepSeek actually documents about rate limits

The official page is short. As of October 2026 it lists these concurrency limits for each account:

| Model | Concurrency limit (per account) |
| --- | --- |
| `deepseek-flash` | 2,500 |
| `deepseek-v4-pro` | 500 |

Three rules decide how the limit is counted:

*   **A request counts as one concurrent connection** from the time it is sent until the model response is complete.
*   **Limits are calculated at the account level**, regardless of which API key is used — creating more keys does not add capacity.
*   **Within the limit, requests receive a response; above it, you receive HTTP 429.**

If you need more, DeepSeek accepts a **capacity expansion request**: it says it will match the concurrency to your actual business needs, and there is no additional cost for the expansion. There is no published requests-per-minute or tokens-per-minute table.

The same page documents **`user_id` isolation** for platforms that serve many end users from one account. Passing `user_id` gives:

*   **Content safety isolation** — distinguishes user identities on your side for content safety handling.
*   **KVCache isolation** — isolates the KV cache per user for privacy management.
*   **Scheduling isolation** — schedules your users separately.

For regular API users, all `user_id` values are combined for the concurrency calculation. For accounts with increased concurrency quotas, DeepSeek limits the account total _and_ applies a limit to each `user_id` (an empty id is treated as a special `user_id`): 2,500 for `deepseek-flash` and 500 for `deepseek-v4-pro` per `user_id`. A `user_id` over its limit gets HTTP 429 for that `user_id`’s requests. The value must match the regex `[a-zA-Z0-9\-_]+`, be at most 512 characters long, and contain no user privacy information.

Older descriptions of DeepSeek’s policy no longer apply: in January 2025 the rate-limit page said the API did “NOT constrain user’s rate limit”, as [Simon Willison quoted on 18 January 2025](https://simonwillison.net/2025/jan/18/deepseek-api-docs-rate-limit/). Plan against the fixed per-account numbers above.

## The current API surface: models, legacy IDs, and where 429s come from

DeepSeek’s API lists two model IDs, both addressed through the same OpenAI-compatible endpoint, and each has its own concurrency limit:

*   **`deepseek-flash`** — served by DeepSeek-V4.1-Flash-1017; the recommended default and the only model with image input; limit 2,500.
*   **`deepseek-v4-pro`** — served by DeepSeek-V4-Pro-0813; limit 500.

Thinking mode is a request parameter on either model, not a separate model ID, and it is enabled by default. Set `reasoning_effort` to `"low"`, `"high"` or `"max"`; the response then returns `reasoning_content` alongside the final `content`. Pass `extra_body={"thinking": {"type": "disabled"}}` for non-thinking. Thinking requests usually generate more tokens, so each one holds a concurrency slot for longer.

If you maintain older integrations: the legacy `deepseek-chat` and `deepseek-reasoner` IDs were scheduled for retirement on **2026-07-24 at 15:59 UTC** and are no longer listed in DeepSeek’s docs. The names `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` are still accepted but are served by DeepSeek-V4.1-Flash-1017 and billed at the Flash price. Migrating is a one-line `model=` swap to `deepseek-flash`; `base_url` does not change. For the wider picture, see our [DeepSeek API documentation](https://deepseekai.guide/api/deepseek-api-documentation/) overview.

## Quickstart: a request with user_id and a generous timeout

Chat requests hit `POST /chat/completions`, the OpenAI-compatible endpoint. With the OpenAI SDK, `user_id` goes under `extra_body`:

```
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    timeout=900,  # seconds; leaves room for keep-alive waits plus generation
)

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "You are a precise assistant."},
        {"role": "user",   "content": "Summarise this changelog in 3 bullets."},
    ],
    max_tokens=512,
    extra_body={"user_id": "customer_42"},
)
print(resp.choices[0].message.content)
```

In a raw HTTP request body, `user_id` is a top-level field next to `model` and `messages`. DeepSeek also offers an Anthropic-compatible format at a separate base URL, `https://api.deepseek.com/anthropic`; there, `user_id` goes inside `metadata`:

```
{
    "model": "deepseek-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "metadata": {"user_id": "your_user_id"},
    "max_tokens": 1024
}
```

With the Anthropic SDK, pass `metadata={"user_id": "your_user_id"}` to `client.messages.create`. The OpenAI Python SDK’s README says requests time out after 10 minutes by default; don’t lower that for DeepSeek calls. If you are still wiring up keys, the [guide on how to get a DeepSeek API key](https://deepseekai.guide/api/deepseek-api-key-setup/) walks through the console.

## What waiting looks like at the wire level

The behaviour that catches teams out is often not the 429 — it is the wait before a response. DeepSeek’s page describes a **request keep-alive mechanism**: after a request is sent, it may take a while to receive a response, and the HTTP connection stays open meanwhile. Non-streaming requests continuously receive empty lines; streaming requests continuously receive SSE keep-alive comments (`: keep-alive`). These do not affect parsing of the JSON body, but if you parse HTTP responses yourself you must handle the empty lines or comments.

Two consequences worth designing for:

1.   **Long waits are possible.** Set generous read timeouts and make sure your reverse proxy, serverless runtime, or API gateway does not cut the connection prematurely.
2.   **If the request has not started inference after 10 minutes, the server closes the connection.** Treat this as the upper bound on queueing time for a single request and design your retry logic accordingly.

## What triggers a 429

DeepSeek’s documentation names these causes:

*   **Account concurrency exceeded** — more in-flight requests than the model’s limit (2,500 for `deepseek-flash`, 500 for `deepseek-v4-pro`), counted across all your API keys.
*   **A `user_id` over its own limit** — only for accounts with increased quotas, where each `user_id` also has a cap.
*   **Sending requests too quickly, or exceeding a QPS limit** — the wording on DeepSeek’s Error Codes page, whose advice is to pace requests reasonably. DeepSeek does not publish a QPS figure.

A simple mental model: each request holds one slot from the moment you send it until its response is complete. You will rarely hit the limit with a single sequential client; you will hit it when many processes fan out at once with no shared governor, or when long thinking-mode generations keep slots occupied.

## Production patterns that survive 429s

The concurrency limit is a known number, but it is shared across your whole account, so the safest approach is a well-behaved client. Four patterns help.

### 1. Exponential backoff with jitter

The canonical retry loop on a 429 is exponential backoff: wait, retry, double the wait on each subsequent failure, and add a small random offset (jitter) so synchronised clients do not retry in lockstep. The OpenAI Python SDK already retries 429 and 5xx errors twice by default with a short exponential backoff (per its README); the loop below adds longer, jittered retries on top — set `max_retries=0` on the client if you want it to be the only retry layer.

```
import os, random, time
from openai import OpenAI, RateLimitError

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

def call_with_backoff(messages, max_retries=6, max_delay=120.0):
    delay = 1.0
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="deepseek-flash",
                messages=messages,
                max_tokens=512,
            )
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            sleep_for = delay + random.uniform(0, delay * 0.5)
            time.sleep(sleep_for)
            delay = min(delay * 2, max_delay)
```

Cap the maximum delay (60–120 seconds is sensible) and the retry count. This follows DeepSeek’s Error Codes guidance: pace requests on a 429, and retry 500 and 503 errors after a brief wait.

### 2. A bounded concurrency pool

Backoff alone is reactive. The proactive companion is a semaphore that caps how many requests you ever have in flight at once. Because DeepSeek counts concurrency per account, regardless of API key, size the pool for the whole account — every worker, process and service that shares it — and keep it below 2,500 for `deepseek-flash` and 500 for `deepseek-v4-pro`. This works better than tuning requests per minute, because the limit DeepSeek enforces is concurrency-shaped.

### 3. Circuit breaker for sustained failure

When a large share of calls in a rolling window return 429 or 5xx, stop sending for a cool-off period, then send one or two canary requests. Resume full traffic only when canaries succeed. This prevents retry storms during DeepSeek incidents and keeps your own queues from filling. A message telling users the service is busy is better UX than a spinner that pretends progress.

### 4. Cut the work, not just the rate

Because a request holds its slot until the response completes, shorter requests free capacity sooner. Three levers:

*   **Right-size each call.** Cap `max_tokens` where answers are short, and use non-thinking mode (`extra_body={"thinking": {"type": "disabled"}}`) or `reasoning_effort="low"` for simple tasks.
*   **Context caching.** A repeated prompt prefix is billed at the cache-hit price automatically; it lowers cost, not the concurrency count. Pair this with the [DeepSeek context caching](https://deepseekai.guide/api/deepseek-api-context-caching/) guide to structure prompts so the cache actually hits.
*   **Streaming.** Streaming does not raise the limit, but it gets useful tokens to the user sooner and keeps the connection active with keep-alive comments while waiting. The [DeepSeek API streaming](https://deepseekai.guide/api/deepseek-api-streaming/) guide covers the SSE shape.

## Headers and parameters worth knowing

A short reference for the parameters that interact with rate-limit behaviour. Both models have a **1M-token context window** with output up to **384K tokens**, so most limits you hit will be concurrency, not size.

| Parameter | What it does | Notes for rate-limit work |
| --- | --- | --- |
| `user_id` | Identifies your end user | Content-safety, KVCache and scheduling isolation; per-`user_id` limits on increased quotas. OpenAI SDK: inside `extra_body`; Anthropic format: `metadata.user_id`. |
| `max_tokens` | Cap on output length | Lower this for chatty endpoints; long generations hold a slot longer. |
| `temperature` | Sampling randomness | Non-thinking mode only (thinking mode ignores it): 0.0 for code/maths, 1.0 for data analysis, 1.3 for chat/translation, 1.5 for creative writing — DeepSeek’s official guidance. |
| `top_p` | Nucleus sampling | Model-specific: on `deepseek-flash` only in thinking mode (0.95–1.0); on `deepseek-v4-pro` only in non-thinking mode. |
| `stream` | SSE streaming | While waiting, the server sends `: keep-alive` comments. |
| `reasoning_effort` | `"low"`, `"high"` (default) or `"max"` | Higher effort usually means longer generations, so each request holds its slot longer. |
| `response_format` | JSON mode (`{"type": "json_object"}`) | Designed to return valid JSON, not guaranteed — handle empty content, prompt with the word “json” plus a sample schema, set `max_tokens` high enough to avoid truncation. |

Two more notes. First, the API is **stateless** — clients must resend the full conversation history with every request, unlike the web chat which keeps state for the session. Second, FIM (Fill-In-the-Middle) completion is Beta and works in non-thinking mode only.

## How rate limits interact with cost: a worked example

Throttling is not just a latency problem — it also shapes how you size budgets. The math below uses rates from [DeepSeek’s pricing page](https://api-docs.deepseek.com/quick_start/pricing/) as of October 2026; peak hours are 01:00–04:00 and 06:00–10:00 UTC, Monday to Friday, excluding Chinese public holidays, and all other hours are off-peak at half price. For an in-depth breakdown see our [DeepSeek API pricing](https://deepseekai.guide/api/deepseek-api-pricing/) guide.

Scenario on `deepseek-flash`: 1,000,000 calls per month with a 2,000-token system prompt (cached after the first call), a 200-token user message (uncached on each call), and a 300-token response.

| Bucket | Tokens | Peak (rate / cost) | Off-peak (rate / cost) |
| --- | --- | --- | --- |
| Input — cache hit | 2,000,000,000 | $0.006 / $12.00 | $0.003 / $6.00 |
| Input — cache miss | 200,000,000 | $0.30 / $60.00 | $0.15 / $30.00 |
| Output | 300,000,000 | $1.20 / $360.00 | $0.60 / $180.00 |
| **Total** |  | **$432.00** | **$216.00** |

Rates are USD per 1M tokens. The same workload on `deepseek-v4-pro` ($0.044 / $1.32 / $3.96 at peak, $0.022 / $0.66 / $1.98 off-peak) lands at **$1,540.00** at peak and **$770.00** off-peak — about 3.6× the Flash bill. The rate-limit angle: `deepseek-v4-pro` also has one fifth of Flash’s concurrency (500 vs 2,500 per account), so a high-volume path on Pro hits 429s sooner. Keeping `deepseek-flash` as the default for high-volume paths and reserving `deepseek-v4-pro` for the requests that measurably benefit from it helps on both counts.

## Status pages, monitoring, and when to escalate

Sustained 429s that do not respond to backoff usually mean one of three things:

1.   **A platform incident.** Check [DeepSeek’s status page](https://status.deepseek.com/) first. If there is an active incident, aggressive retries are wasted work.
2.   **Your client is misbehaving.** Audit for unbounded fan-out, missing backoff, a stuck retry loop, or several services sharing one account without a shared concurrency budget.
3.   **Your workload genuinely exceeds the account limit.** Smooth the load with a queue, or submit a capacity expansion request — DeepSeek says it matches concurrency to your business needs at no additional cost. With an increased quota, remember the per-`user_id` limits.

For deeper troubleshooting on every status code DeepSeek emits, the [DeepSeek API error codes](https://deepseekai.guide/api/deepseek-api-error-codes/) reference is the companion piece to this article. Teams running DeepSeek alongside other providers should also review our [DeepSeek API best practices](https://deepseekai.guide/api/deepseek-api-best-practices/) for a fuller checklist, and the broader [DeepSeek API docs and guides](https://deepseekai.guide/api/) hub for the rest of the developer surface.

## What this means in practice

Treat DeepSeek’s rate limit as an account-wide concurrency budget: 2,500 in-flight requests on `deepseek-flash` and 500 on `deepseek-v4-pro`, shared by every key on the account, with keep-alive output while requests wait and a connection close if inference has not started after 10 minutes. The rest is on you: a shared concurrency pool, exponential backoff with jitter, a circuit breaker for sustained failure, `user_id` for multi-tenant isolation, and a capacity expansion request when the numbers genuinely don’t fit.

## Frequently asked questions

### What are the DeepSeek API rate limits in requests per minute?

DeepSeek does not publish a requests-per-minute or tokens-per-minute figure. Its Rate Limit & Isolation page sets concurrency limits per account — 2,500 for `deepseek-flash` and 500 for `deepseek-v4-pro` (October 2026) — counted from when a request is sent until its response is complete, regardless of which API key is used. Above the limit you get HTTP 429; the Error Codes page adds that a 429 can also mean requests sent too quickly or a QPS limit. See the [DeepSeek API documentation](https://deepseekai.guide/api/deepseek-api-documentation/) overview for context.

### How do you fix a DeepSeek 429 “Too Many Requests” error?

On a 429, pause and retry with exponential backoff and jitter — start at one second, double on each retry, cap around 60–120 seconds, and limit total attempts. Pair that with a concurrency pool shared across the whole account and kept below the model’s limit, and a circuit breaker for sustained failures. If your workload needs more than the limit, submit a capacity expansion request. Our [DeepSeek API error codes](https://deepseekai.guide/api/deepseek-api-error-codes/) guide covers the full status-code taxonomy.

### Do deepseek-flash and deepseek-v4-pro have different rate limits?

Yes. DeepSeek’s page lists a concurrency limit of 2,500 per account for `deepseek-flash` and 500 for `deepseek-v4-pro`. Legacy names `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` are served by DeepSeek-V4.1-Flash-1017; `deepseek-chat` and `deepseek-reasoner` were scheduled for retirement on 2026-07-24 15:59 UTC and are no longer listed. For other differences — vision, pricing — see [DeepSeek Flash](https://deepseekai.guide/models/deepseek-v4-flash/) and [DeepSeek V4-Pro](https://deepseekai.guide/models/deepseek-v4-pro/).

### Why does a DeepSeek request hang for minutes before returning?

That is the documented keep-alive behaviour, not a bug. While your request waits, DeepSeek sends empty lines (non-streaming) or SSE `: keep-alive` comments (streaming) to keep the HTTP connection open. If the request has not started inference after 10 minutes, the server closes the connection. Set generous read timeouts and ensure your gateway does not cut long-running responses. The [DeepSeek API streaming](https://deepseekai.guide/api/deepseek-api-streaming/) guide covers the SSE format.

### Can you get higher DeepSeek API rate limits?

Yes, without paying for a tier. DeepSeek’s Rate Limit & Isolation page says you can submit a capacity expansion request, that it will match the concurrency to your actual business needs, and that there is no additional cost for the expansion. With an increased quota, DeepSeek limits the account total and also each `user_id` (2,500 for `deepseek-flash`, 500 for `deepseek-v4-pro`). Per-token prices are the same for every account; see the [DeepSeek API pricing](https://deepseekai.guide/api/deepseek-api-pricing/) guide, and cut cost further with [DeepSeek context caching](https://deepseekai.guide/api/deepseek-api-context-caching/).

## Sources & Methodology

**Last source check:** October 25, 2026

### Primary sources

*   Official[DeepSeek API documentation](https://api-docs.deepseek.com/)Endpoints, request/response shape, model IDs Last checked: October 25, 2026
*   Official documentation[DeepSeek API Docs: Rate Limit & Isolation](https://api-docs.deepseek.com/quick_start/rate_limit/)Per-account concurrency limits (deepseek-flash 2,500, deepseek-v4-pro 500), counting rules, 429, capacity expansion at no cost, user_id isolation and format, keep-alive mechanism and 10-minute close Last checked: October 25, 2026
*   Official documentation[DeepSeek API Docs: Error Codes](https://api-docs.deepseek.com/quick_start/error_codes/)429 causes (too fast, concurrency or QPS limit) and retry guidance for 500/503 Last checked: October 25, 2026
*   Official documentation[DeepSeek API Docs: Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)Peak/off-peak rates and peak hours for the worked example Last checked: October 25, 2026
*   Official[DeepSeek status page](https://status.deepseek.com/)Triage step for sustained 429s during platform incidents Last checked: October 25, 2026

### Technical references

*   Technical report[DeepSeek-V3 technical report (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437)V3 architecture and training methodology Last checked: October 25, 2026
*   Official documentation[DeepSeek API Docs: Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)Thinking default, reasoning_effort values, temperature and top_p behaviour Last checked: October 25, 2026
*   Official SDK documentation[openai-python README](https://github.com/openai/openai-python)Default 10-minute timeout and automatic retries (2, including 429), checked 25 Oct 2026 Last checked: October 25, 2026

### Context sources

*   Analysis[Simon Willison: DeepSeek API Docs: Rate Limit (18 Jan 2025)](https://simonwillison.net/2025/jan/18/deepseek-api-docs-rate-limit/)January 2025 wording of DeepSeek's earlier rate-limit policy (history only)Last checked: October 25, 2026

### Methodology

Pricing figures were checked against the official DeepSeek pricing page and normalised into estimated monthly costs using sample token usage scenarios. Actual costs may vary depending on caching, input/output ratio, regional availability, and provider updates.

### Data confidence

High — figures checked directly against the official pricing page on the review date.

### Editorial note

The site's pricing dataset is fetched daily from DeepSeek's official pricing page; this article reflects the prices on the date shown above.
