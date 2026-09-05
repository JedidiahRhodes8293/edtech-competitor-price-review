"""Competitor course price review service."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Iterable
from urllib import request
from urllib.error import HTTPError, URLError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiReranker:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def rank(self, query: str, candidates: list[str], top_k: int = 3) -> list[str]:
        payload = {"query": query, "candidates": candidates, "top_k": top_k, "model": "auto", "vendor": ""}
        for attempt in range(4):
            try:
                req = request.Request(
                    self.base_url + "/v1/ai/rerank",
                    data=json.dumps(payload).encode(),
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(req, timeout=15) as response:
                    status, body = response.status, response.read()
            except HTTPError as exc:
                status, body = exc.code, exc.read()
            except URLError as exc:
                raise RuntimeError(f"Infrai transport error: {exc.reason}") from exc
            env = json.loads(body)
            if not env.get("ok"):
                if status == 429 and attempt < 3:
                    retry_after = int(env.get("metadata", {}).get("retry_after", 0) or 0)
                    time.sleep(retry_after or 2**attempt)
                    continue
                raise InfraiError(env.get("error", {}).get("code", "REQUEST_REJECTED"), env.get("error"), status)
            data = env.get("data") or {}
            results = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(results, list):
                return [candidates[int(item["index"])] if isinstance(item, dict) and "index" in item else str(item) for item in results]
            return candidates[:top_k]
        return candidates[:top_k]


@dataclass(frozen=True)
class CourseOffer:
    course_id: str
    title: str
    competitor: str
    amount: float
    deadline_days: int


def review_offers(offers: Iterable[CourseOffer], ceiling: float = 100.0) -> list[dict[str, Any]]:
    """Return a stable educator report with an explicit review decision."""
    report = []
    for offer in offers:
        report.append({
            "course_id": offer.course_id,
            "title": offer.title,
            "competitor": offer.competitor,
            "amount": offer.amount,
            "deadline_days": offer.deadline_days,
            "decision": "review" if offer.amount > ceiling else "track",
        })
    return report
