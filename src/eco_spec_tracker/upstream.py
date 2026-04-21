"""Fetch skill rows from the Eco mod's `/api/v1/skills` endpoint.

Set `UPSTREAM_URL` to the mod endpoint (e.g. `http://localhost:5100/api/v1/skills`
for the shell harness, or the real Eco server's mod URL in prod). When unset,
fall back to the in-repo mock data so local dev works offline.

Upstream shape (matches `mod/src/Dtos.cs`, camelCased by ASP.NET's default
System.Text.Json policy):

    [
      {
        "player": "coilysiren",
        "active": true,
        "specialties": [{"name": "Basic Carpentry", "level": 5, "maxLevel": 7}, ...]
      },
      ...
    ]
"""

from __future__ import annotations

import os

import httpx

from eco_spec_tracker.mock_data import PlayerSpecialty, all_rows

UPSTREAM_URL = os.getenv("UPSTREAM_URL")
UPSTREAM_TIMEOUT_SECONDS = 5.0


async def fetch_rows() -> list[PlayerSpecialty]:
    if not UPSTREAM_URL:
        return all_rows()
    async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT_SECONDS) as client:
        response = await client.get(UPSTREAM_URL)
        response.raise_for_status()
        payload = response.json()
    rows: list[PlayerSpecialty] = []
    for p in payload:
        player, active = p["player"], bool(p["active"])
        for s in p.get("specialties", []):
            level = int(s.get("level", 0))
            if level <= 0:
                continue
            rows.append(PlayerSpecialty(player, s["name"], level, active))
    return rows
