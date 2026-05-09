"""Fetch skill rows from the Eco mod's `/api/v1/skills` endpoint.

Set `UPSTREAM_URL` to the mod endpoint (e.g. `http://localhost:5100/api/v1/skills`
for the shell harness, or the real Eco server's mod URL in prod). When unset,
fall back to the in-repo mock data so local dev works offline.

New mod shape (matches `mod/src/Dtos.cs`, camelCased by ASP.NET's default
System.Text.Json policy):

    [
      {
        "player": "coilysiren",
        "lastSeen": "2026-05-08T12:34:56Z",   // null if never logged in
        "specialties": [{"name": "Basic Carpentry", "level": 5, "maxLevel": 7}, ...]
      },
      ...
    ]

Pre-#3 mods returned `"active": bool` instead of `"lastSeen"`. We keep parsing
that as a fallback so the web app keeps working through the rollout window
between deploying this app and pushing the new mod DLL onto kai-server. True
maps to "seen right now"; False/missing maps to None. Once every Eco server
has the new mod, this branch can be deleted.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import httpx

from eco_spec_tracker.mock_data import PlayerSpecialty, all_rows

UPSTREAM_URL = os.getenv("UPSTREAM_URL")
UPSTREAM_API_KEY = os.getenv("UPSTREAM_API_KEY")
UPSTREAM_TIMEOUT_SECONDS = 5.0


def _parse_last_seen(raw: str | None) -> datetime | None:
    if not raw:
        return None
    # Accept the trailing-Z form the mod emits, plus any ISO-8601 with offset.
    text = raw.replace("Z", "+00:00") if raw.endswith("Z") else raw
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _resolve_last_seen(payload_player: dict) -> datetime | None:
    last_seen = _parse_last_seen(payload_player.get("lastSeen"))
    if last_seen is not None:
        return last_seen
    # Fallback for old mods that only return `active: bool`.
    if payload_player.get("active") is True:
        return datetime.now(UTC)
    return None


async def fetch_rows() -> list[PlayerSpecialty]:
    if not UPSTREAM_URL:
        return all_rows()
    headers = {"X-API-Key": UPSTREAM_API_KEY} if UPSTREAM_API_KEY else {}
    async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT_SECONDS) as client:
        response = await client.get(UPSTREAM_URL, headers=headers)
        response.raise_for_status()
        payload = response.json()
    rows: list[PlayerSpecialty] = []
    for p in payload:
        player = p["player"]
        last_seen = _resolve_last_seen(p)
        for s in p.get("specialties", []):
            level = int(s.get("level", 0))
            if level <= 0:
                continue
            rows.append(PlayerSpecialty(player, s["name"], level, last_seen))
    return rows
