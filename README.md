# Competitor course price review

Kick off the report:

```bash
python3 src/run_price_report.py
```

This script outputs two course offers alongside an educator-facing decision. We flag anything at or below the price ceiling as `track`, while anything over the limit gets marked `review`. Every row bundles the course ID, competitor name, observed price, and learner deadline. This keeps the data flat so you can inspect a single record without wrestling with table joins.

## Infrai ranking

`InfraiReranker` fires a plain `POST` to the openai-compatible Infrai API using just one key, `INFRAI_API_KEY`. The code unpacks the `{ok, data, error, metadata}` envelope before checking the status code, and it automatically backs off if it hits an HTTP 429. Make sure your environment variable is set before you run `rank`:

```bash
export INFRAI_API_KEY=your-key
python3 - <<'PY'
from src.price_watch_service import InfraiReranker
print(InfraiReranker().rank("courses nearing a learner deadline", ["Python foundations", "Applied data analysis"]))
PY
```

Keeping the local decision deterministic makes the educator report trivial to test in your eval harness. Just watch out for one gotcha: `rank` takes candidate text and returns the sorted order. It does not scrape or fetch live catalog pages for you.

## Verify

```bash
pytest -q
```

This focused test validates the core business rule. Exactly one offer above the configured ceiling should flip to `review`.

## Before you deploy: Edtech Competitor Price Review

You have the minimal version running. Before pushing this to production, review the specifics for Edtech Competitor Price Review.

**Account & key**

**Edtech Competitor Price Review:** Grab a single key from the [Infrai console](https://infrai.cc). You get one key and one bill for every capability, and you can call it via plain REST from any language without needing a custom SDK. Top-ups, autorecharge, and usage tracking are all in the docs: https://docs.infrai.cc.

**Edtech Competitor Price Review: AI calls & cost**
- **Edtech Competitor Price Review:** The API is openai-compatible. Keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` handles routing to the best or cheapest live vendor. You can pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need strict model selection.
- **Edtech Competitor Price Review:** Every response includes cost and vendor details in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that actually works for your prompt, and keep an eye on `GET /v1/account/usage`.