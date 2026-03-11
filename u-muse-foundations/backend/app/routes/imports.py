"""Song import endpoints (Spotify-first, local fallback)."""

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.extensions import db
from app.models.song import Song
from app.services.spotify_service import get_track_audio_features, search_track

imports_bp = Blueprint("imports", __name__)

FEATURE_FIELDS = [
    "tempo",
    "energy",
    "danceability",
    "valence",
    "acousticness",
    "instrumentalness",
    "loudness",
    "speechiness",
    "liveness",
]


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


def _song_has_audio_features(song):
    """Return True if any tracked audio feature is already present."""
    return any(getattr(song, key) is not None for key in FEATURE_FIELDS)


def _apply_audio_features(song, features):
    """Copy available Spotify audio feature values onto a Song model."""
    for key in FEATURE_FIELDS:
        if key in features and features.get(key) is not None:
            setattr(song, key, features.get(key))


@imports_bp.post("/spotify")
def import_song_from_spotify():
    """Import a song from Spotify search and store it in the local database.

    Behavior:
    - Prefer Spotify track search + optional audio features.
    - If a track already exists, optionally backfill missing audio features.
    - If Spotify search fails, create a minimal local song from the raw query.
    """
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    track = None
    spotify_error = None
    try:
        track = search_track(query)
    except Exception as exc:
        spotify_error = str(exc)

    if track:
        spotify_id = track.get("id")

        if spotify_id:
            existing_song = Song.query.filter_by(spotify_id=spotify_id).first()
            if existing_song:
                feature_error = None
                features_updated = False

                if not _song_has_audio_features(existing_song):
                    try:
                        # Backfill features when the record exists but was imported
                        # before feature collection was implemented/available.
                        features = get_track_audio_features(spotify_id) or {}
                        if features:
                            _apply_audio_features(existing_song, features)
                            db.session.commit()
                            features_updated = True
                    except Exception as exc:
                        feature_error = str(exc)

                message = "Song already exists"
                if features_updated:
                    message = "Song already exists (audio features updated)"

                response = {
                    "message": message,
                    "song": existing_song.to_dict(),
                    "source": "spotify",
                }
                if feature_error:
                    response["feature_error"] = feature_error

                return jsonify({
                    **response
                }), 200

        artist_name = track["artists"][0]["name"] if track.get("artists") else "Unknown"
        album_name = track["album"]["name"] if track.get("album") else None

        release_year = None
        release_date = track.get("album", {}).get("release_date")
        if release_date:
            try:
                release_year = int(release_date[:4])
            except ValueError:
                release_year = None

        features = {}
        feature_error = None
        try:
            features = get_track_audio_features(spotify_id) or {}
        except Exception as exc:
            feature_error = str(exc)
            features = {}

        new_song = Song(
            title=track.get("name"),
            artist_name=artist_name,
            spotify_id=spotify_id,
            album_name=album_name,
            release_year=release_year,
            duration_ms=track.get("duration_ms"),
            tempo=features.get("tempo"),
            energy=features.get("energy"),
            danceability=features.get("danceability"),
            valence=features.get("valence"),
            acousticness=features.get("acousticness"),
            instrumentalness=features.get("instrumentalness"),
            loudness=features.get("loudness"),
            speechiness=features.get("speechiness"),
            liveness=features.get("liveness"),
        )

        db.session.add(new_song)
        db.session.commit()

        response = {
            "message": "Song imported successfully",
            "song": new_song.to_dict(),
            "source": "spotify",
        }
        if feature_error:
            response["feature_error"] = feature_error

        return jsonify(response), 201

    title, artist_name = _parse_song_query(query)
    existing_song = _find_existing_song(title, artist_name)
    if existing_song:
        return jsonify({
            "message": "Song already exists",
            "song": existing_song.to_dict(),
            "source": "local",
        }), 200

    fallback_song = Song(
        title=title,
        artist_name=artist_name,
    )

    db.session.add(fallback_song)
    db.session.commit()

    response = {
        "message": "Song saved from query",
        "song": fallback_song.to_dict(),
        "source": "local",
    }
    if spotify_error:
        response["spotify_error"] = spotify_error

    return jsonify(response), 201
