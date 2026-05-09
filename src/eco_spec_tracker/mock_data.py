"""Mock data shaped like what the Eco mod will eventually return.

Each player has a set of learned specialties (skill trees with Level > 0)
and a `last_seen` timestamp (None if the player has never logged in).
The tracker derives "active" from `last_seen >= now - ACTIVE_WINDOW_DAYS`,
so what the dashboard highlights matches "logged in within the last week"
rather than "online right this second."
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

ACTIVE_WINDOW_DAYS = int(os.getenv("ACTIVE_WINDOW_DAYS", "7"))


def _now() -> datetime:
    return datetime.now(UTC)


def is_active(last_seen: datetime | None, now: datetime | None = None) -> bool:
    if last_seen is None:
        return False
    cutoff = (now or _now()) - timedelta(days=ACTIVE_WINDOW_DAYS)
    return last_seen >= cutoff


@dataclass(frozen=True)
class PlayerSpecialty:
    player: str
    specialty: str
    level: int  # 0 means not learned; we only store learned rows in mock data
    last_seen: datetime | None  # None = never logged in

    @property
    def active(self) -> bool:
        return is_active(self.last_seen)


# Canonical profession → specialties map, mirroring Eco's skill tree roughly.
# (Final list will come from the mod; this is just for UI iteration.)
PROFESSION_SPECIALTIES: dict[str, list[str]] = {
    "Carpentry": ["Basic Carpentry", "Advanced Carpentry", "Furniture Making", "Lumber"],
    "Masonry": ["Basic Masonry", "Advanced Masonry", "Pottery", "Brick Making"],
    "Smelting": ["Basic Smelting", "Advanced Smelting", "Composites", "Alloys"],
    "Glassworking": ["Glassworking", "Hand-Plane Glass"],
    "Cooking": ["Campfire Cooking", "Baking", "Cutting Edge Cooking", "Advanced Baking"],
    "Farming": ["Farming", "Gardening", "Fertilizers"],
    "Hunting": ["Hunting", "Butchery"],
    "Mining": ["Mining", "Advanced Mining"],
    "Logging": ["Logging", "Advanced Logging"],
    "Engineering": ["Mechanics", "Electronics", "Industry"],
    "Tailoring": ["Tailoring", "Advanced Tailoring"],
    "Paper Milling": ["Paper Milling", "Printing"],
}


def _build_mock_rows() -> list[PlayerSpecialty]:
    """Build mock rows with `last_seen` values relative to now.

    Recomputed at module import; close enough for a dev dataset. Mix recent
    (within 7 days), stale (> 7 days), and never-logged-in players so the
    active filter has something to do.
    """
    now = _now()
    last_seen_by_player: dict[str, datetime | None] = {
        "coilysiren": now - timedelta(hours=2),
        "ekans": now - timedelta(days=1),
        "redwood": now - timedelta(days=30),
        "salt": now - timedelta(days=2),
        "quill": now - timedelta(days=4),
        "hammerhand": now - timedelta(days=6),
        "voltaic": now - timedelta(days=20),
        "fernweh": now - timedelta(hours=12),
        "ore-ge": now - timedelta(days=3),
        "tinkerbell": None,
    }

    rows_by_player: dict[str, list[tuple[str, int]]] = {
        "coilysiren": [("Basic Carpentry", 5), ("Advanced Carpentry", 3), ("Furniture Making", 2)],
        "ekans": [("Basic Carpentry", 4), ("Lumber", 1), ("Mining", 6)],
        "redwood": [("Glassworking", 5), ("Basic Masonry", 2), ("Pottery", 3)],
        "salt": [("Campfire Cooking", 4), ("Baking", 2), ("Farming", 5), ("Gardening", 3)],
        "quill": [("Paper Milling", 4), ("Printing", 2)],
        "hammerhand": [("Basic Masonry", 5), ("Brick Making", 4), ("Advanced Masonry", 3)],
        "voltaic": [("Mechanics", 5), ("Electronics", 4), ("Industry", 2)],
        "fernweh": [("Farming", 3), ("Fertilizers", 2), ("Hunting", 4), ("Butchery", 3)],
        "ore-ge": [("Basic Smelting", 5), ("Advanced Smelting", 3), ("Alloys", 2)],
        "tinkerbell": [("Tailoring", 4), ("Advanced Tailoring", 2)],
    }

    rows: list[PlayerSpecialty] = []
    for player, specialties in rows_by_player.items():
        last_seen = last_seen_by_player[player]
        for specialty, level in specialties:
            rows.append(PlayerSpecialty(player, specialty, level, last_seen))
    return rows


_MOCK_ROWS: list[PlayerSpecialty] = _build_mock_rows()


def all_rows() -> list[PlayerSpecialty]:
    return list(_MOCK_ROWS)


@dataclass(frozen=True)
class ProfessionStat:
    profession: str
    active: int
    total: int
    players: list[str]


def profession_stats(rows: list[PlayerSpecialty] | None = None) -> list[ProfessionStat]:
    """Per-profession counts: active (>=1 active learned specialty) / total (any learned)."""
    source = _MOCK_ROWS if rows is None else rows
    stats: list[ProfessionStat] = []
    for profession, specialties in PROFESSION_SPECIALTIES.items():
        specialty_set = set(specialties)
        scoped = [r for r in source if r.specialty in specialty_set]
        players_all = {r.player for r in scoped}
        players_active = {r.player for r in scoped if r.active}
        stats.append(
            ProfessionStat(
                profession=profession,
                active=len(players_active),
                total=len(players_all),
                players=sorted(players_all),
            )
        )
    stats.sort(key=lambda s: (-s.total, s.profession))
    return stats


@dataclass(frozen=True)
class PlayerView:
    name: str
    active: bool
    specialties: list[PlayerSpecialty]


def players(rows: list[PlayerSpecialty] | None = None) -> list[PlayerView]:
    source = _MOCK_ROWS if rows is None else rows
    by_player: dict[str, list[PlayerSpecialty]] = {}
    for r in source:
        by_player.setdefault(r.player, []).append(r)
    out: list[PlayerView] = []
    for name, player_rows in by_player.items():
        out.append(
            PlayerView(
                name=name,
                active=any(r.active for r in player_rows),
                specialties=sorted(player_rows, key=lambda r: r.specialty),
            )
        )
    out.sort(key=lambda p: (not p.active, p.name))
    return out


@dataclass(frozen=True)
class SpecialtyHolder:
    player: str
    level: int
    active: bool


@dataclass(frozen=True)
class SpecialtyView:
    name: str
    profession: str
    active: int  # holders flagged active
    total: int
    holders: list[SpecialtyHolder]  # sorted: active first, then level desc


def _specialty_to_profession() -> dict[str, str]:
    return {s: prof for prof, specs in PROFESSION_SPECIALTIES.items() for s in specs}


def specialties(rows: list[PlayerSpecialty] | None = None) -> list[SpecialtyView]:
    """The inverse of players(): per specialty, who holds it and at what level."""
    source = _MOCK_ROWS if rows is None else rows
    prof_of = _specialty_to_profession()
    by_spec: dict[str, list[PlayerSpecialty]] = {}
    for r in source:
        by_spec.setdefault(r.specialty, []).append(r)
    out: list[SpecialtyView] = []
    for spec, spec_rows in by_spec.items():
        holders = sorted(
            (SpecialtyHolder(r.player, r.level, r.active) for r in spec_rows),
            key=lambda h: (not h.active, -h.level, h.player),
        )
        out.append(
            SpecialtyView(
                name=spec,
                profession=prof_of.get(spec, "Other"),
                active=sum(1 for h in holders if h.active),
                total=len(holders),
                holders=holders,
            )
        )
    out.sort(key=lambda s: (s.profession, s.name))
    return out
