<!-- source: https://www.requesty.ai/blog/rate-limits-for-llm-providers-openai-anthropic-and-deepseek -->

Title: LLM API rate limits for OpenAI, Claude, Gemini and DeepSeek

URL Source: https://www.requesty.ai/blog/rate-limits-for-llm-providers-openai-anthropic-and-deepseek

Published Time: 2025-02-14T00:00:00Z

Markdown Content:
In November 2026, OpenAI's Build tier allows 5,000 requests per minute and 1 million tokens per minute for Astra, Sol and Terra on Standard. [Anthropic's Start tier](https://platform.claude.com/docs/en/api/rate-limits) allows 1,000 requests per minute, 2 million input tokens per minute and 400,000 output tokens per minute for Sonnet 5.5 and Opus 5.5. Gemini limits apply per project; DeepSeek allows 2,500 concurrent Flash requests and 500 concurrent Pro requests. For prices and measured latency on the same model families, see [GPT vs Claude vs Gemini API price and latency](https://www.requesty.ai/blog/gpt-vs-claude-vs-gemini-api-price-latency).

## LLM API rate limits compared

RPM counts requests per minute. TPM counts tokens per minute, and a provider can count input and output tokens separately. Concurrency counts calls in progress.

The November 2026 limits below cover direct API paths. Check the linked provider pages and account consoles for the limits that apply to your model and account.

| Provider | Published limit or rule | Where to check |
| --- | --- | --- |
| OpenAI | Build: 5,000 RPM and 1 million TPM for Astra, Sol and Terra on Standard | [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits) |
| Anthropic | Start: 1,000 RPM, 2 million input TPM and 400,000 output TPM for Sonnet 5.5 and Opus 5.5 | [Claude rate limits](https://platform.claude.com/docs/en/api/rate-limits) |
| Gemini Developer API | Limits apply per project | [Google AI Studio](https://aistudio.google.com/rate-limit?timeRange=last-28-days) |
| DeepSeek | 2,500 concurrent Flash requests and 500 concurrent Pro requests | [DeepSeek rate limits](https://api-docs.deepseek.com/quick_start/rate_limit/) |

## OpenAI limits rise with your tier

[OpenAI's November 2026 Standard limits](https://developers.openai.com/api/docs/guides/rate-limits) use three paid tiers: Build, Launch and Grow. The table shows RPM and TPM by model family.

| Tier | Astra, Sol and Terra RPM | Astra, Sol and Terra TPM | Luna RPM | Luna TPM |
| --- | --- | --- | --- | --- |
| Build | 5,000 | 1,000,000 | 5,000 | 2,000,000 |
| Launch | 10,000 | 4,000,000 | 10,000 | 10,000,000 |
| Grow | 15,000 | 40,000,000 | 30,000 | 180,000,000 |

These are Standard limits. OpenAI lists different limits for Ultrafast service, and models shown under a shared limit draw from the same pool. Check [Organization Limits](https://platform.openai.com/settings/organization/limits) for your account.

OpenAI says organizations upgrade automatically as total credit purchases reach the tier thresholds: $5 for Build, $100 for Launch and $500 for Grow. The corresponding monthly usage limits are $500, $5,000 and $200,000 respectively. The [tier guide](https://developers.openai.com/api/docs/guides/rate-limits) lists the purchase and usage limits alongside the rate limits.

### Which OpenAI limit binds first?

Take a Build account using a Standard Astra, Sol or Terra model. It has a published allowance of 5,000 RPM and 1 million TPM. We can estimate its throughput with one assumption: each request uses 20,000 tokens counted against the token limit.

| Counter | Calculation | Allowance |
| --- | --- | --- |
| Requests | Published RPM | 5,000 calls per minute |
| Tokens | 1,000,000 TPM / 20,000 tokens per call | 50 calls per minute |

Under that assumption, tokens bind at 50 calls per minute. Quadrupling the allowance to 4 million TPM on Launch raises the estimate to 200 calls per minute, assuming the same token usage per call.

The assumption is the part to test against your own requests. OpenAI says its rate-limit estimate uses the larger of `max_tokens` and an estimate based on request character count, so set `max_tokens` close to the response size the task needs. The calculation is a minute average; [OpenAI can enforce limits over shorter periods](https://help.openai.com/en/articles/5955604-troubleshooting-api-rate-limits-and-429-errors).

## Anthropic limits by tier

[Anthropic's November 2026 rate limits](https://platform.claude.com/docs/en/api/rate-limits) for Sonnet 5.5 and Opus 5.5 vary by tier:

| Tier | RPM | Input TPM | Output TPM |
| --- | --- | --- | --- |
| Start | 1,000 | 2,000,000 | 400,000 |
| Build | 5,000 | 5,000,000 | 1,000,000 |
| Scale | 10,000 | 10,000,000 | 2,000,000 |

Input and output tokens are counted separately, so output TPM can bind first on long responses.

## How to stop hitting OpenAI rate limits

Start with the 429 body. [OpenAI says](https://help.openai.com/en/articles/5955604-troubleshooting-api-rate-limits-and-429-errors) a 429 can mean a temporary rate limit, an exhausted prepaid balance or a spending limit. Retrying a billing or usage error will not restore access.

1.   1 Check the limit and your tier

Inspect the error. OpenAI returns [rate-limit headers](https://developers.openai.com/api/docs/guides/rate-limits) on each response, including `x-ratelimit-limit-requests`, `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, `x-ratelimit-reset-requests` and `x-ratelimit-reset-tokens`. These show which counter (requests or tokens) is running out and when it resets. Check [Organization Limits](https://platform.openai.com/settings/organization/limits) too. OpenAI moves organizations to Launch at $100 and Grow at $500 in total credit purchases. Check the [tier guide](https://developers.openai.com/api/docs/guides/rate-limits) if you need more sustained capacity. 
2.   2 Pace requests and tokens

Coordinate workers against the quota they share. Set output allowances close to expected response sizes, and spread requests evenly across shorter intervals, such as per second, instead of sending a minute's allowance at once. [OpenAI's troubleshooting guide](https://help.openai.com/en/articles/5955604-troubleshooting-api-rate-limits-and-429-errors) explains how shorter enforcement windows can trigger a 429. 
3.   3 Retry temporary throttles with a deadline

Use [exponential backoff](https://developers.openai.com/api/docs/guides/rate-limits#retry-with-exponential-backoff): double the delay after each failed attempt, treat `Retry-After` as a minimum when it appears, and add random jitter so clients do not retry together. Stop after a fixed number of retries or a total deadline. OpenAI's official SDKs automatically retry eligible 429 and 503 responses, so account for those attempts in your retry budget. 
4.   4
5.   5 Test a fallback with its own capacity

Provision a backup route with an independent quota and test it with your workload before relying on it. If the primary route is throttled, the backup needs available capacity to accept the traffic. 

OpenAI also recommends a gradual ramp once traffic reaches 1 million input TPM: increase traffic by no more than 50% every 15 minutes. Its [rate-limit guide](https://developers.openai.com/api/docs/guides/rate-limits) identifies rapid increases with a `429 slow_down` response.

## Gemini uses project limits

[Google's Gemini Developer API](https://ai.google.dev/gemini-api/docs/rate-limits) applies limits per project. Open [AI Studio](https://aistudio.google.com/rate-limit?timeRange=last-28-days) to find the limits for the project and model you use.

[All API keys in the same project share that project's limit](https://ai.google.dev/gemini-api/docs/rate-limits), so extra keys in one project add no capacity. [Requests-per-day quotas reset at midnight Pacific time](https://ai.google.dev/gemini-api/docs/rate-limits).

## DeepSeek limits concurrent requests

[DeepSeek's published limits](https://api-docs.deepseek.com/quick_start/rate_limit/) are 2,500 concurrent requests for Flash and 500 for Pro. DeepSeek calculates concurrency at the account level, regardless of API key. A concurrent request occupies capacity while it is in progress, so the number of calls you can start per minute depends on how long calls run.

For example, if an application has 500 calls in progress against a 500-call Pro limit, further requests receive HTTP 429, according to [DeepSeek's rate-limit documentation](https://api-docs.deepseek.com/quick_start/rate_limit/). The application should queue or delay new calls until in-progress calls finish.

## Put the backup route to work

Requesty provides an OpenAI-compatible API with automatic failover chains across providers and weighted load balancing. You can bring your own provider keys or use one Requesty key. A fallback still needs available capacity on the route receiving the request. Requesty itself does not cap requests per minute; it limits how many requests can be [in flight at once](https://docs.requesty.ai/features/in-flight-rate-limits).

Test a fallback route

Choose a backup provider with its own quota, configure a failover chain, and test it with the prompts your application sends. See the [AI gateway](https://www.requesty.ai/ai-gateway) for the routing setup and [Requesty's error codes](https://docs.requesty.ai/features/error-codes) when testing the route. If you route through OpenRouter, see [OpenRouter rate limits](https://www.requesty.ai/blog/openrouter-rate-limits-why-they-happen-and-how-multi-provider-fallback-fixes-them).

Before a launch, record the limits for each route, calculate the token budget using a sample of your requests, and run a 429 test. For the related failure modes, see our guides to [automatic fallback when the Claude API is down](https://www.requesty.ai/blog/llm-api-fallback-when-claude-is-down) and [setting API spending limits](https://www.requesty.ai/blog/llm-spend-limits-per-api-key-and-customer). For Claude workloads that resend the same prefix, see [Anthropic prompt caching](https://www.requesty.ai/blog/anthropic-prompt-caching).

Frequently asked questions
What are the LLM API rate limits in November 2026?OpenAI's Build tier has 5,000 requests per minute and 1 million tokens per minute for Astra, Sol and Terra on Standard. Anthropic's Start tier has 1,000 requests per minute, 2 million input tokens per minute and 400,000 output tokens per minute for Sonnet 5.5 and Opus 5.5. Gemini limits apply per project, while DeepSeek allows 2,500 concurrent Flash requests and 500 concurrent Pro requests.

How do I stop hitting rate limits on the OpenAI API?Check the 429 body for billing or usage errors, pace requests and tokens, retry temporary throttles with exponential backoff and Retry-After, and route to a fallback with its own quota. OpenAI moves organizations to Launch at $100 and Grow at $500 in total credit purchases.

What are OpenAI's API rate limits by tier?For Astra, Sol and Terra on the Standard service, OpenAI lists 5,000 RPM and 1 million TPM on Build, 10,000 RPM and 4 million TPM on Launch, and 15,000 RPM and 40 million TPM on Grow.

What are Anthropic's API rate limits by tier?For Sonnet 5.5 and Opus 5.5, Anthropic's Start tier allows 1,000 RPM, 2 million input TPM and 400,000 output TPM. Build allows 5,000 RPM, 5 million input TPM and 1 million output TPM; Scale allows 10,000 RPM, 10 million input TPM and 2 million output TPM.

Does DeepSeek have an API rate limit?DeepSeek publishes concurrency limits of 2,500 simultaneous requests for Flash and 500 for Pro. A concurrency limit caps how many requests can be in progress at once; requests above it receive HTTP 429.

Does a new API key increase my rate limit?A new API key does not increase capacity if it draws on the same quota pool. For example, [DeepSeek calculates concurrency at the account level](https://api-docs.deepseek.com/quick_start/rate_limit/), regardless of which API key sends the request.

Why can I hit a rate limit below my RPM allowance?A token limit or another counter can bind before requests per minute. OpenAI can also enforce limits over shorter windows, so a burst can fail even when the minute average is below the published RPM.
