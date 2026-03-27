"""MusicBrainz lookup helpers."""

from __future__ import annotations

import re
import time

import requests
from flask import current_app

BASE_URL = "https://musicbrainz.org/ws/2/recording"

_last_request_started = 0.0


def _normalize(value):
    """Collapse a title or artist string for fuzzy equality checks."""
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _throttle():
    """Respect MusicBrainz's published one-request-per-second guidance."""
    global _last_request_started

    now = time.monotonic()
    elapsed = now - _last_request_started
    if elapsed < 1.05:
        time.sleep(1.05 - elapsed)

    _last_request_started = time.monotonic()


def _headers():
    """Build headers for MusicBrainz requests."""
    contact = current_app.config.get("MUSIC_METADATA_CONTACT")
    user_agent = current_app.config["MUSIC_METADATA_USER_AGENT"]

    if contact and contact not in user_agent:
        user_agent = f"{user_agent} ({contact})"

    return {
        "Accept": "application/json",
        "User-Agent": user_agent,
    }


def _extract_artist_name(recording):
    """Convert MusicBrainz artist-credit arrays into one label."""
    parts = recording.get("artist-credit") or []
    names = [part.get("name") for part in parts if part.get("name")]
    return " ".join(names).strip() or None


def _extract_release_year(recording):
    """Read the release year from MusicBrainz search results."""
    date_value = recording.get("first-release-date")
    if not date_value:
        return None

    try:
        return int(date_value[:4])
    except (TypeError, ValueError):
        return None


def _candidate_score(recording, title, artist_name):
    """Blend MusicBrainz search score with exact-match bonuses."""
    score = float(recording.get("score", 0))
    target_title = _normalize(title)
    target_artist = _normalize(artist_name)
    recording_title = _normalize(recording.get("title"))
    recording_artist = _normalize(_extract_artist_name(recording))

    if target_title and recording_title == target_title:
        score += 120
    elif target_title and target_title in recording_title:
        score += 45

    if target_artist and recording_artist == target_artist:
        score += 120
    elif target_artist and target_artist in recording_artist:
        score += 45

    return score


def search_recording_candidates(title, artist_name=None, limit=5):
    """Return ranked MusicBrainz recording candidates for one title/artist query."""
    if not title:
        return []

    query_parts = [f'recording:"{title}"']
    if artist_name and artist_name.lower() != "unknown":
        query_parts.append(f'artist:"{artist_name}"')

    _throttle()
    response = requests.get(
        BASE_URL,
        params={
            "query": " AND ".join(query_parts),
            "fmt": "json",
            "limit": limit,
        },
        headers=_headers(),
        timeout=20,
    )
    response.raise_for_status()

    recordings = response.json().get("recordings", [])
    ranked = sorted(
        recordings,
        key=lambda candidate: _candidate_score(candidate, title, artist_name or ""),
        reverse=True,
    )

    return [
        {
            "musicbrainz_recording_id": candidate.get("id"),
            "title": candidate.get("title"),
            "artist_name": _extract_artist_name(candidate) or artist_name,
            "release_year": _extract_release_year(candidate),
            "duration_ms": candidate.get("length"),
        }
        for candidate in ranked
    ]


def search_recording(title, artist_name=None, limit=5):
    """Return the single best MusicBrainz recording candidate."""
    candidates = search_recording_candidates(title, artist_name=artist_name, limit=limit)
    return candidates[0] if candidates else None
