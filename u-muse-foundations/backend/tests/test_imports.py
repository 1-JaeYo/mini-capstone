"""API tests for the Spotify-first import flow."""

import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.song import Song


class ImportApiTests(unittest.TestCase):
    """Exercise the import endpoints with mocked providers."""

    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_CLIENT_SECRET": "test-client-secret",
            }
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_spotify_import_uses_spotify_identity_and_catalog_enrichment(self):
        spotify_track = {
            "id": "spotify-123",
            "name": "Exact Song Title",
            "artists": [{"name": "Exact Artist"}],
            "album": {
                "name": "Exact Album",
                "release_date": "2024-04-12",
            },
            "duration_ms": 210000,
        }
        musicbrainz_candidates = [
            {
                "musicbrainz_recording_id": "mbid-1",
                "title": "Exact Song Title (Live)",
                "artist_name": "Exact Artist",
                "release_year": 2023,
                "duration_ms": 205000,
            }
        ]
        acousticbrainz_features = {
            "tempo": 118.4,
            "danceability": 0.73,
            "mood_happy": 0.66,
            "mood_party": 0.61,
        }
        deezer_match = {
            "deezer_id": "deezer-99",
            "title": "Exact Song Title",
            "artist_name": "Exact Artist",
            "album_name": "Deezer Album",
            "release_year": 2022,
            "duration_ms": 208000,
            "preview_url": "https://example.com/clip.mp3",
            "gain": -7.3,
            "tempo": 117.0,
        }

        with patch("app.routes.imports.search_track", return_value=spotify_track), patch(
            "app.routes.imports.search_recording_candidates",
            return_value=musicbrainz_candidates,
        ), patch(
            "app.routes.imports.get_recording_features",
            return_value=acousticbrainz_features,
        ), patch("app.routes.imports.lookup_track", return_value=deezer_match):
            response = self.client.post(
                "/api/imports/spotify",
                json={"query": "Exact Song Title - Exact Artist"},
            )

        payload = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(payload["source"], "spotify")
        self.assertTrue(payload["provider_matches"]["spotify"])
        self.assertEqual(payload["song"]["spotify_id"], "spotify-123")
        self.assertEqual(payload["song"]["title"], "Exact Song Title")
        self.assertEqual(payload["song"]["artist_name"], "Exact Artist")
        self.assertEqual(payload["song"]["album_name"], "Exact Album")
        self.assertEqual(payload["song"]["release_year"], 2024)
        self.assertEqual(payload["song"]["musicbrainz_recording_id"], "mbid-1")
        self.assertEqual(payload["song"]["deezer_id"], "deezer-99")
        self.assertEqual(payload["song"]["preview_url"], "https://example.com/clip.mp3")
        self.assertEqual(payload["song"]["tempo"], 118.4)
        self.assertEqual(payload["song"]["gain"], -7.3)

    def test_spotify_import_returns_404_when_no_spotify_match_exists(self):
        with patch("app.routes.imports.search_track", return_value=None):
            response = self.client.post(
                "/api/imports/spotify",
                json={"query": "Song That Does Not Exist"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["error"],
            "No Spotify track match found for this query",
        )

    def test_spotify_import_reuses_existing_song_by_spotify_id(self):
        with self.app.app_context():
            existing_song = Song(
                title="Old Title",
                artist_name="Old Artist",
                spotify_id="spotify-123",
            )
            db.session.add(existing_song)
            db.session.commit()

        spotify_track = {
            "id": "spotify-123",
            "name": "Exact Song Title",
            "artists": [{"name": "Exact Artist"}],
            "album": {"name": "Exact Album", "release_date": "2024-04-12"},
            "duration_ms": 210000,
        }

        with patch("app.routes.imports.search_track", return_value=spotify_track), patch(
            "app.routes.imports.search_recording_candidates",
            return_value=[],
        ), patch("app.routes.imports.lookup_track", return_value=None):
            response = self.client.post(
                "/api/imports/spotify",
                json={"query": "Exact Song Title - Exact Artist"},
            )

        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["message"], "Song already exists")
        self.assertEqual(payload["song"]["spotify_id"], "spotify-123")
        self.assertEqual(payload["song"]["title"], "Exact Song Title")


if __name__ == "__main__":
    unittest.main()
