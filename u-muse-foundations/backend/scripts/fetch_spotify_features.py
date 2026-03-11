"""Backfill missing Spotify audio features for existing songs."""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db
from app.models.song import Song
from app.services.spotify_service import get_track_audio_features


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


def has_audio_features(song):
    """Return True if any target feature is already set."""
    return any(getattr(song, key) is not None for key in FEATURE_FIELDS)


def apply_features(song, features):
    """Copy feature values from Spotify payload onto a Song model."""
    for key in FEATURE_FIELDS:
        value = features.get(key)
        if value is not None:
            setattr(song, key, value)


def main():
    """Run one-time feature enrichment for songs that have spotify_id values."""
    app = create_app()

    with app.app_context():
        songs = Song.query.filter(Song.spotify_id.isnot(None)).all()

        updated = 0
        skipped = 0
        failed = 0

        for song in songs:
            if has_audio_features(song):
                skipped += 1
                continue

            try:
                features = get_track_audio_features(song.spotify_id) or {}
                if not features:
                    failed += 1
                    print(f"[FAILED] {song.id} {song.title} (no feature payload)")
                    continue

                apply_features(song, features)
                updated += 1
                print(f"[UPDATED] {song.id} {song.title}")
            except Exception as exc:
                failed += 1
                print(f"[FAILED] {song.id} {song.title}: {exc}")

        db.session.commit()

        print("\nDone.")
        print(f"Updated: {updated}")
        print(f"Skipped (already had features): {skipped}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
