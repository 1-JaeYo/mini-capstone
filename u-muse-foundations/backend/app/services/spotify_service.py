"""Spotify Web API integration helpers."""

import base64
import time
import requests
from flask import current_app

TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"
AUDIO_FEATURES_URL = "https://api.spotify.com/v1/audio-features"

_cached_token = None
_token_expires_at = 0


def get_access_token():
    """Return a cached app token, refreshing when expired."""
    global _cached_token, _token_expires_at

    # Reuse token if still valid
    if _cached_token and time.time() < _token_expires_at:
        return _cached_token

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]

    if not client_id or not client_secret:
        raise ValueError("Spotify credentials are missing in environment variables.")

    creds = f"{client_id}:{client_secret}"
    creds_b64 = base64.b64encode(creds.encode()).decode()

    headers = {
        "Authorization": f"Basic {creds_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=20)
    response.raise_for_status()

    payload = response.json()
    _cached_token = payload["access_token"]

    # subtract a small buffer so we don't use an expired token
    expires_in = payload.get("expires_in", 3600)
    _token_expires_at = time.time() + expires_in - 60

    return _cached_token


def search_track(query):
    """Search Spotify tracks and return the top match payload."""
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "type": "track",
        "limit": 1
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=20)
    response.raise_for_status()

    items = response.json().get("tracks", {}).get("items", [])
    if not items:
        return None

    return items[0]


def get_track_audio_features(track_id):
    """Fetch Spotify audio features for one track ID."""
    if not track_id:
        return None

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{AUDIO_FEATURES_URL}/{track_id}",
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    if not payload or payload.get("error"):
        return None

    return payload
