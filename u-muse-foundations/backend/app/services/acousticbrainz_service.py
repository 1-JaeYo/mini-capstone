"""AcousticBrainz feature lookup helpers."""

import requests

BASE_URL = "https://acousticbrainz.org/api/v1"


def _safe_get_json(url):
    """Fetch a JSON document, returning None when the recording is not found."""
    response = requests.get(url, timeout=20)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def _nested(mapping, *keys):
    """Safely read a nested JSON field."""
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def get_recording_features(recording_id):
    """Fetch AcousticBrainz low/high-level features for one MusicBrainz recording ID."""
    if not recording_id:
        return None

    low_level = _safe_get_json(f"{BASE_URL}/{recording_id}/low-level") or {}
    high_level = _safe_get_json(f"{BASE_URL}/{recording_id}/high-level") or {}

    if not low_level and not high_level:
        return None

    danceability = _nested(high_level, "highlevel", "danceability", "all", "danceable")
    if danceability is None:
        raw_danceability = _nested(low_level, "rhythm", "danceability")
        if raw_danceability is not None:
            danceability = min(max(float(raw_danceability), 0.0), 1.0)

    return {
        "tempo": _nested(low_level, "rhythm", "bpm"),
        "danceability": danceability,
        "mood_happy": _nested(high_level, "highlevel", "mood_happy", "all", "happy"),
        "mood_sad": _nested(high_level, "highlevel", "mood_sad", "all", "sad"),
        "mood_relaxed": _nested(high_level, "highlevel", "mood_relaxed", "all", "relaxed"),
        "mood_party": _nested(high_level, "highlevel", "mood_party", "all", "party"),
    }
