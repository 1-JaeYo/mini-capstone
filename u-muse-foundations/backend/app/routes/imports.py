"""Song import endpoints for the Spotify-first and catalog metadata pipelines."""

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.extensions import db
from app.models.song import Song
from app.services.acousticbrainz_service import get_recording_features
from app.services.deezer_service import lookup_track
from app.services.feature_service import (
    apply_catalog_payload,
    build_catalog_payload,
    summarize_provider_status,
)
from app.services.musicbrainz_service import search_recording_candidates
from app.services.spotify_service import search_track

imports_bp = Blueprint("imports", __name__)


def _parse_song_query(query):
    """Parse a free-form query into (title, artist) best-effort values."""
    raw = query.strip()
    lowered = raw.lower()

    if " - " in raw:
        title, artist = raw.split(" - ", 1)
    elif " by " in lowered:
        split_at = lowered.find(" by ")
        title = raw[:split_at]
        artist = raw[split_at + 4:]
    elif "," in raw:
        title, artist = raw.split(",", 1)
    else:
        return raw, "Unknown"

    title = title.strip() or raw
    artist = artist.strip() or "Unknown"
    return title, artist


def _find_existing_song(title, artist_name):
    """Find an existing song by case-insensitive title + artist."""
    return Song.query.filter(
        func.lower(Song.title) == title.lower(),
        func.lower(Song.artist_name) == artist_name.lower(),
    ).first()


def _find_existing_song_by_provider(
    spotify_id,
    musicbrainz_recording_id,
    deezer_id,
    title,
    artist_name,
):
    """Prefer stable provider IDs before falling back to title + artist."""
    if spotify_id:
        existing_song = Song.query.filter_by(spotify_id=spotify_id).first()
        if existing_song:
            return existing_song

    if musicbrainz_recording_id:
        existing_song = Song.query.filter_by(
            musicbrainz_recording_id=musicbrainz_recording_id
        ).first()
        if existing_song:
            return existing_song

    if deezer_id:
        existing_song = Song.query.filter_by(deezer_id=deezer_id).first()
        if existing_song:
            return existing_song

    return _find_existing_song(title, artist_name)


def _extract_release_year(date_value):
    """Read a release year from Spotify-style date strings."""
    if not date_value:
        return None

    try:
        return int(str(date_value)[:4])
    except (TypeError, ValueError):
        return None


def _spotify_metadata(track):
    """Normalize the top Spotify track match into the Song schema shape."""
    album = track.get("album") or {}
    artists = track.get("artists") or []
    artist_names = [artist.get("name") for artist in artists if artist.get("name")]

    return {
        "spotify_id": track.get("id"),
        "title": track.get("name"),
        "artist_name": ", ".join(artist_names) or "Unknown",
        "album_name": album.get("name"),
        "release_year": _extract_release_year(album.get("release_date")),
        "duration_ms": track.get("duration_ms"),
    }


def _build_catalog_lookup(title, artist_name):
    """Collect metadata and features from the configured catalog providers."""
    provider_errors = {}
    provider_matches = {}

    musicbrainz_match = None
    acousticbrainz_features = {}
    deezer_match = None

    try:
        musicbrainz_candidates = search_recording_candidates(title, artist_name, limit=5)
    except Exception as exc:
        provider_errors["musicbrainz"] = str(exc)
        musicbrainz_candidates = []

    provider_matches["musicbrainz"] = bool(musicbrainz_candidates)

    if musicbrainz_candidates:
        musicbrainz_match = musicbrainz_candidates[0]
        for candidate in musicbrainz_candidates:
            try:
                acousticbrainz_features = get_recording_features(
                    candidate["musicbrainz_recording_id"]
                ) or {}
            except Exception as exc:
                provider_errors["acousticbrainz"] = str(exc)
                acousticbrainz_features = {}

            if acousticbrainz_features:
                musicbrainz_match = candidate
                break

    provider_matches["acousticbrainz"] = bool(acousticbrainz_features)

    try:
        deezer_match = lookup_track(title, artist_name)
    except Exception as exc:
        provider_errors["deezer"] = str(exc)

    provider_matches["deezer"] = bool(deezer_match)

    payload = build_catalog_payload(
        musicbrainz_match=musicbrainz_match,
        acousticbrainz_features=acousticbrainz_features,
        deezer_match=deezer_match,
    )

    return payload, provider_matches, provider_errors


def _build_spotify_enriched_lookup(query):
    """Use Spotify for exact identity, then enrich with catalog providers."""
    spotify_track = search_track(query)
    if not spotify_track:
        return None, {"spotify": False}, {}

    spotify_match = _spotify_metadata(spotify_track)
    payload, provider_matches, provider_errors = _build_catalog_lookup(
        spotify_match["title"],
        spotify_match["artist_name"],
    )

    provider_matches["spotify"] = True
    payload.update({
        "spotify_id": spotify_match["spotify_id"],
        "title": spotify_match["title"],
        "artist_name": spotify_match["artist_name"],
        "album_name": spotify_match["album_name"] or payload.get("album_name"),
        "release_year": spotify_match["release_year"] or payload.get("release_year"),
        "duration_ms": spotify_match["duration_ms"] or payload.get("duration_ms"),
    })

    return payload, provider_matches, provider_errors


@imports_bp.post("/spotify")
def import_song_from_spotify():
    """Import a song using Spotify for identity and catalog providers for enrichment."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    try:
        payload, provider_matches, provider_errors = _build_spotify_enriched_lookup(query)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Spotify lookup failed: {exc}"}), 502

    if not payload:
        return jsonify({"error": "No Spotify track match found for this query"}), 404

    title = payload.get("title") or query
    artist_name = payload.get("artist_name") or "Unknown"
    existing_song = _find_existing_song_by_provider(
        payload.get("spotify_id"),
        payload.get("musicbrainz_recording_id"),
        payload.get("deezer_id"),
        title,
        artist_name,
    )

    warnings = summarize_provider_status(provider_matches, provider_errors)

    if existing_song:
        apply_catalog_payload(existing_song, payload)
        db.session.commit()

        response = {
            "message": "Song already exists",
            "song": existing_song.to_dict(),
            "source": "spotify",
            "provider_matches": provider_matches,
        }
        if warnings:
            response["warnings"] = warnings
        if provider_errors:
            response["provider_errors"] = provider_errors
        return jsonify(response), 200

    new_song = Song(
        title=title,
        artist_name=artist_name,
    )
    apply_catalog_payload(new_song, payload)

    db.session.add(new_song)
    db.session.commit()

    response = {
        "message": "Song imported successfully",
        "song": new_song.to_dict(),
        "source": "spotify",
        "provider_matches": provider_matches,
    }
    if warnings:
        response["warnings"] = warnings
    if provider_errors:
        response["provider_errors"] = provider_errors

    return jsonify(response), 201


@imports_bp.post("/catalog")
def import_song_from_catalog():
    """Import a song using MusicBrainz, AcousticBrainz, and Deezer."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    title, artist_name = _parse_song_query(query)
    payload, provider_matches, provider_errors = _build_catalog_lookup(title, artist_name)

    existing_song = _find_existing_song_by_provider(
        payload.get("spotify_id"),
        payload.get("musicbrainz_recording_id"),
        payload.get("deezer_id"),
        title,
        artist_name,
    )

    warnings = summarize_provider_status(provider_matches, provider_errors)

    if existing_song:
        apply_catalog_payload(existing_song, payload)
        db.session.commit()

        response = {
            "message": "Song already exists",
            "song": existing_song.to_dict(),
            "source": "catalog",
            "provider_matches": provider_matches,
        }
        if warnings:
            response["warnings"] = warnings
        if provider_errors:
            response["provider_errors"] = provider_errors
        return jsonify(response), 200

    new_song = Song(
        title=payload.get("title") or title,
        artist_name=payload.get("artist_name") or artist_name,
    )
    apply_catalog_payload(new_song, payload)

    db.session.add(new_song)
    db.session.commit()

    response = {
        "message": "Song imported successfully",
        "song": new_song.to_dict(),
        "source": "catalog",
        "provider_matches": provider_matches,
    }
    if warnings:
        response["warnings"] = warnings
    if provider_errors:
        response["provider_errors"] = provider_errors

    return jsonify(response), 201
