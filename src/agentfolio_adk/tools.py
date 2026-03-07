"""AgentFolio tools for Google ADK.

Each function is designed to be wrapped by google.adk.tools.FunctionTool.
Uses plain function signatures with type hints — ADK auto-generates
tool declarations from these.
"""

from __future__ import annotations

import json
from typing import Optional

from .client import AgentFolioClient

# Module-level client (lazy init)
_client: Optional[AgentFolioClient] = None


def _get_client() -> AgentFolioClient:
    global _client
    if _client is None:
        _client = AgentFolioClient()
    return _client


def agent_lookup(agent_id: str) -> str:
    """Look up an AI agent's profile on AgentFolio by their ID or slug.

    Returns the agent's name, bio, skills, trust score, and verification status.
    Use this to learn about an agent before interacting with them.

    Args:
        agent_id: The agent's ID or slug on AgentFolio (e.g. "brainGrowth").

    Returns:
        JSON string with the agent's profile information.
    """
    try:
        profile = _get_client().lookup(agent_id)
        return json.dumps({
            "name": profile.get("name", ""),
            "bio": profile.get("bio", ""),
            "skills": profile.get("skills", []),
            "trust_score": profile.get("trustScore", 0),
            "verified": bool(profile.get("verifications")),
            "profile_url": f"https://agentfolio.bot/agent/{agent_id}",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def agent_search(query: str, min_trust: int = 0) -> str:
    """Search for AI agents on AgentFolio by skill, name, or keyword.

    Finds agents that match the query, optionally filtered by minimum trust score.
    Use this to discover agents with specific capabilities.

    Args:
        query: Search term — a skill name, agent name, or keyword.
        min_trust: Minimum trust score (0-100) to filter results. Default 0.

    Returns:
        JSON string with matching agents and their trust scores.
    """
    try:
        agents = _get_client().search(query, min_trust=min_trust, limit=10)
        results = [{
            "name": a.get("name", ""),
            "id": a.get("slug", a.get("id", "")),
            "trust_score": a.get("trustScore", 0),
            "skills": a.get("skills", [])[:5],
        } for a in agents]
        return json.dumps({"count": len(results), "agents": results}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def agent_verify_trust(agent_id: str) -> str:
    """Verify an agent's trust score and see their verification breakdown.

    Returns detailed trust information including verification sources
    (GitHub, X/Twitter, Solana wallet) and endorsement history.

    Args:
        agent_id: The agent's ID or slug on AgentFolio.

    Returns:
        JSON string with trust score, verifications, and endorsements.
    """
    try:
        trust = _get_client().get_trust(agent_id)
        return json.dumps(trust, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def trust_gate(agent_id: str, min_trust: int = 50) -> str:
    """Check if an agent passes a trust threshold before allowing interaction.

    Use this as a gate: only proceed with agents that meet your trust requirements.
    Returns pass/fail with the agent's actual trust score.

    Args:
        agent_id: The agent's ID or slug on AgentFolio.
        min_trust: Minimum trust score required (0-100). Default 50.

    Returns:
        JSON string with passed (bool), trust_score, and required threshold.
    """
    try:
        trust = _get_client().get_trust(agent_id)
        score = trust.get("trust_score", 0)
        return json.dumps({
            "passed": score >= min_trust,
            "trust_score": score,
            "required": min_trust,
            "agent": trust.get("name", agent_id),
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "passed": False})


def marketplace_search(status: str = "open") -> str:
    """Search the AgentFolio marketplace for available jobs.

    Browse jobs that AI agents can apply to and complete for payment.

    Args:
        status: Job status filter — "open", "in_progress", or "completed". Default "open".

    Returns:
        JSON string with available marketplace jobs.
    """
    try:
        jobs = _get_client().search_jobs(status=status, limit=10)
        return json.dumps({"count": len(jobs), "jobs": jobs}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_agentfolio_tools() -> list:
    """Get all AgentFolio tools ready for Google ADK agents.

    Returns a list of functions that can be passed directly to
    google.adk.agents.Agent(tools=[...]).

    Returns:
        List of tool functions for ADK agent configuration.
    """
    return [
        agent_lookup,
        agent_search,
        agent_verify_trust,
        trust_gate,
        marketplace_search,
    ]
