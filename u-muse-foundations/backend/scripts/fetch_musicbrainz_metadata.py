"""Backfill catalog metadata/features using MusicBrainz, AcousticBrainz, and Deezer."""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db
from app.models.song import Song
from app.services.acousticbrainz_service import get_recording_features
from app.services.deezer_service import lookup_track
from app.services.feature_service import apply_catalog_payload, build_catalog_payload
from app.services.musicbrainz_service import search_recording_candidates


def _needs_backfill(song):
    """Return True when the song is still missing core catalog fields."""
    required_values = [
        song.musicbrainz_recording_id,
        song.deezer_id,
        song.tempo,
        song.danceability,
        song.gain,
    ]
    return not all(value is not None for value in required_values)


def main():
    """Enrich all stored songs with the new provider pipeline."""
    app = create_app()

    with app.app_context():
        songs = Song.query.all()

        updated = 0
        skipped = 0
        failed = 0

        for song in songs:
            if not _needs_backfill(song):
                skipped += 1
                continue

            try:
                musicbrainz_candidates = search_recording_candidates(
                    song.title,
                    song.artist_name,
                    limit=5,
                )
                musicbrainz_match = musicbrainz_candidates[0] if musicbrainz_candidates else None
                acousticbrainz_features = None
                for candidate in musicbrainz_candidates:
                    acousticbrainz_features = get_recording_features(
                        candidate["musicbrainz_recording_id"]
                    )
                    if acousticbrainz_features:
                        musicbrainz_match = candidate
                        break

                deezer_match = lookup_track(song.title, song.artist_name)
                payload = build_catalog_payload(
                    musicbrainz_match=musicbrainz_match,
                    acousticbrainz_features=acousticbrainz_features,
                    deezer_match=deezer_match,
                )

                if apply_catalog_payload(song, payload):
                    updated += 1
                    print(f"[UPDATED] {song.id} {song.title}")
                else:
                    skipped += 1
                    print(f"[SKIPPED] {song.id} {song.title}")
            except Exception as exc:
                failed += 1
                print(f"[FAILED] {song.id} {song.title}: {exc}")

        db.session.commit()

        print("\nDone.")
        print(f"Updated: {updated}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
