"""AgentFolio API client for Google ADK tools."""

from __future__ import annotations

import httpx
from typing import Any, Optional


class AgentFolioClient:
    """Lightweight client for the AgentFolio API."""

    def __init__(self, base_url: str = "https://agentfolio.bot"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=15.0)

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        resp = self._client.get(f"{self.base_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    def lookup(self, agent_id: str) -> dict:
        """Look up an agent profile by ID or slug."""
        return self._get(f"/api/agents/{agent_id}")

    def search(self, query: str, min_trust: int = 0, limit: int = 10) -> list[dict]:
        """Search agents by skill, name, or keyword."""
        params = {"q": query, "limit": limit}
        if min_trust > 0:
            params["minTrust"] = min_trust
        result = self._get("/api/agents", params=params)
        agents = result if isinstance(result, list) else result.get("agents", [])
        if min_trust > 0:
            agents = [a for a in agents if a.get("trustScore", 0) >= min_trust]
        return agents

    def get_trust(self, agent_id: str) -> dict:
        """Get trust score breakdown for an agent."""
        profile = self.lookup(agent_id)
        return {
            "agent_id": agent_id,
            "trust_score": profile.get("trustScore", 0),
            "verifications": profile.get("verifications", []),
            "endorsements": profile.get("endorsements", []),
            "name": profile.get("name", ""),
        }

    def search_jobs(self, status: str = "open", limit: int = 10) -> list[dict]:
        """Search marketplace jobs."""
        return self._get("/api/marketplace/jobs", params={"status": status, "limit": limit})

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
