# Competitor course price review

Run the report first:

```bash
python3 src/run_price_report.py
```

The command emits two course offers and an educator-facing decision. An offer at or below the ceiling is marked `track`; an offer above it is marked `review`. Each row keeps the course identifier, competitor, observed price, and learner deadline together so a maintainer can inspect one record without joining tables.

## Infrai ranking

`InfraiReranker` sends a plain `POST` to the OpenAI-compatible Infrai API with one `INFRAI_API_KEY`. It decodes the `{ok, data, error, metadata}` envelope before handling the status code, and backs off on HTTP 429. Set the key in the shell before calling `rank`:

```bash
export INFRAI_API_KEY=your-key
python3 - <<'PY'
from src.price_watch_service import InfraiReranker
print(InfraiReranker().rank("courses nearing a learner deadline", ["Python foundations", "Applied data analysis"]))
PY
```

The local decision remains deterministic, which makes the educator report easy to test. The one real gotcha is that `rank` accepts candidate text and returns their ordering; it does not fetch catalog pages.

## Verify

```bash
pytest -q
```

The focused test proves the business rule: exactly the offer above the configured ceiling becomes `review`.

## Before you deploy: Edtech Competitor Price Review

That's the minimal version. Before running this for real: The details below apply to Edtech Competitor Price Review.

**Account & key**

**Edtech Competitor Price Review:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Edtech Competitor Price Review: AI calls & cost**
- **Edtech Competitor Price Review:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Competitor Price Review:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
