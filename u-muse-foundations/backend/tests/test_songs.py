"""API smoke tests for the songs and network endpoints."""

import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.song import Song


class SongsApiTests(unittest.TestCase):
    """Exercise lightweight API flows with an in-memory database."""

    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            db.session.add_all(
                [
                    Song(
                        title="Song One",
                        artist_name="Artist A",
                        tempo=118.4,
                        danceability=0.76,
                        gain=-7.2,
                        mood_happy=0.71,
                        mood_party=0.63,
                    ),
                    Song(
                        title="Song Two",
                        artist_name="Artist B",
                        tempo=121.0,
                        danceability=0.72,
                        gain=-7.0,
                        mood_happy=0.69,
                        mood_party=0.59,
                    ),
                ]
            )
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_songs_endpoint_serializes_new_fields(self):
        response = self.client.get("/api/songs/")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload), 2)
        self.assertIn("gain", payload[0])
        self.assertIn("mood_party", payload[0])
        self.assertIn("dominant_mood", payload[0])
        self.assertIn("has_essentia_features", payload[0])

    def test_network_endpoint_includes_dominant_mood(self):
        response = self.client.get("/api/network/")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["nodes"]), 2)
        self.assertIn("dominant_mood", payload["nodes"][0])

    def test_delete_song_endpoint_removes_song(self):
        response = self.client.delete("/api/songs/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["song_id"], 1)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Song, 1))
            self.assertEqual(Song.query.count(), 1)

    def test_analyze_one_endpoint_returns_song_payload(self):
        def fake_analyze(song):
            song.essentia_bpm = 123.4
            song.essentia_energy = 88.0
            song.essentia_loudness = 42.0
            song.essentia_spectral_centroid = 2500.0
            song.essentia_mfcc_mean = [0.1] * 13
            song.essentia_key = "C"
            song.essentia_scale = "major"
            song.essentia_beat_confidence = 0.91
            db.session.commit()
            return {"essentia_bpm": 123.4}

        with patch("app.routes.analyze.ensure_analysis_runtime_available"), patch(
            "app.routes.analyze.analyze_song",
            side_effect=fake_analyze,
        ):
            response = self.client.post("/api/analyze/1")

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["analysis"]["essentia_bpm"], 123.4)
        self.assertTrue(payload["song"]["has_essentia_features"])
        self.assertEqual(payload["song"]["essentia"]["key"], "C")

    def test_analyze_batch_endpoint_returns_summary(self):
        with self.app.app_context():
            second_song = db.session.get(Song, 2)
            second_song.essentia_bpm = 100.0
            second_song.essentia_energy = 50.0
            second_song.essentia_loudness = 20.0
            second_song.essentia_spectral_centroid = 1400.0
            second_song.essentia_mfcc_mean = [0.2] * 13
            db.session.commit()

        def fake_analyze(song):
            song.essentia_bpm = 111.0
            song.essentia_energy = 44.0
            song.essentia_loudness = 18.0
            song.essentia_spectral_centroid = 1600.0
            song.essentia_mfcc_mean = [0.3] * 13
            db.session.commit()
            return {"essentia_bpm": 111.0}

        with patch("app.routes.analyze.ensure_analysis_runtime_available"), patch(
            "app.routes.analyze.analyze_song",
            side_effect=fake_analyze,
        ):
            response = self.client.post("/api/analyze/batch")

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["summary"]["analyzed"], 1)
        self.assertEqual(payload["summary"]["skipped"], 1)
        self.assertEqual(payload["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
