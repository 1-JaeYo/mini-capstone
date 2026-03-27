"""Deezer lookup helpers."""

from __future__ import annotations

import re

import requests

SEARCH_URL = "https://api.deezer.com/search"
TRACK_URL = "https://api.deezer.com/track"


def _normalize(value):
    """Collapse a title or artist string for fuzzy equality checks."""
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _extract_release_year(date_value):
    """Convert Deezer release-date strings into a 4-digit year."""
    if not date_value:
        return None

    try:
        return int(str(date_value)[:4])
    except (TypeError, ValueError):
        return None


def _candidate_score(track, title, artist_name):
    """Rank Deezer search hits using exact title/artist bonuses."""
    score = 0.0
    target_title = _normalize(title)
    target_artist = _normalize(artist_name)
    track_title = _normalize(track.get("title"))
    track_artist = _normalize((track.get("artist") or {}).get("name"))

    if target_title and track_title == target_title:
        score += 120
    elif target_title and target_title in track_title:
        score += 45

    if target_artist and track_artist == target_artist:
        score += 120
    elif target_artist and target_artist in track_artist:
        score += 45

    score += min(float(track.get("rank", 0)) / 100000, 25)
    return score


def _search_tracks(title, artist_name=None, limit=5):
    """Run one Deezer search query and return the track list payload."""
    if artist_name and artist_name.lower() != "unknown":
        query = f'artist:"{artist_name}" track:"{title}"'
    else:
        query = title

    response = requests.get(
        SEARCH_URL,
        params={"q": query, "limit": limit},
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def _get_track(track_id):
    """Fetch the detailed Deezer track document for one track ID."""
    response = requests.get(f"{TRACK_URL}/{track_id}", timeout=20)
    response.raise_for_status()
    return response.json()


def get_track_by_id(track_id):
    """Return a normalized Deezer track payload for one known track ID."""
    if not track_id:
        return None

    details = _get_track(track_id)
    album = details.get("album") or {}
    artist = details.get("artist") or {}

    bpm = details.get("bpm")
    if bpm in (None, 0):
        bpm = None

    duration_seconds = details.get("duration")
    duration_ms = int(duration_seconds * 1000) if duration_seconds else None

    return {
        "deezer_id": str(details.get("id")),
        "title": details.get("title"),
        "artist_name": artist.get("name"),
        "album_name": album.get("title"),
        "release_year": _extract_release_year(details.get("release_date")),
        "duration_ms": duration_ms,
        "preview_url": details.get("preview"),
        "gain": details.get("gain"),
        "tempo": bpm,
    }


def lookup_track(title, artist_name=None):
    """Return the best Deezer track match with extended metadata fields."""
    if not title:
        return None

    candidates = _search_tracks(title, artist_name)
    if not candidates and artist_name:
        candidates = _search_tracks(f"{title} {artist_name}")

    if not candidates:
        return None

    best_match = max(
        candidates,
        key=lambda track: _candidate_score(track, title, artist_name or ""),
    )
    details = get_track_by_id(best_match.get("id")) or {}
    if not details:
        return None

    if not details.get("artist_name"):
        details["artist_name"] = (best_match.get("artist") or {}).get("name") or artist_name
    if not details.get("album_name"):
        details["album_name"] = (best_match.get("album") or {}).get("title")
    if not details.get("duration_ms") and best_match.get("duration"):
        details["duration_ms"] = int(best_match["duration"] * 1000)
    if not details.get("preview_url"):
        details["preview_url"] = best_match.get("preview")

    return details
