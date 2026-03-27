"""Network endpoint tests for the stricter mutual-neighbor graph."""

import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.song import Song


class NetworkApiTests(unittest.TestCase):
    """Validate network graph filtering and fallback behavior."""

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
                    Song(title="Song 1", artist_name="Artist 1"),
                    Song(title="Song 2", artist_name="Artist 2"),
                    Song(title="Song 3", artist_name="Artist 3"),
                    Song(title="Song 4", artist_name="Artist 4"),
                ]
            )
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def fake_similarity(self, song_a, song_b, allow_descriptor_fallback=True):
        pair = tuple(sorted((song_a.id, song_b.id)))
        similarities = {
            (1, 2): (0.93, "essentia"),
            (1, 3): (0.89, "essentia"),
            (2, 3): (0.95, "essentia"),
        }

        if pair in similarities:
            return similarities[pair]

        if pair == (3, 4) and allow_descriptor_fallback:
            return 0.99, "descriptor"

        return None, None

    def test_network_defaults_to_mutual_essentia_neighbors(self):
        with patch(
            "app.routes.network.compute_similarity_details",
            side_effect=self.fake_similarity,
        ):
            response = self.client.get("/api/network/?top_k=1")

        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload["meta"]["include_descriptor_fallback"])
        self.assertEqual(payload["meta"]["top_k"], 1)
        self.assertEqual(len(payload["links"]), 1)
        self.assertEqual(payload["links"][0]["source"], 2)
        self.assertEqual(payload["links"][0]["target"], 3)
        self.assertEqual(payload["links"][0]["mode"], "essentia")

    def test_network_descriptor_fallback_is_only_used_when_enabled(self):
        with patch(
            "app.routes.network.compute_similarity_details",
            side_effect=self.fake_similarity,
        ):
            response = self.client.get("/api/network/?top_k=1&include_descriptor_fallback=1")

        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["meta"]["include_descriptor_fallback"])
        self.assertEqual(len(payload["links"]), 1)
        self.assertEqual(payload["links"][0]["source"], 3)
        self.assertEqual(payload["links"][0]["target"], 4)
        self.assertEqual(payload["links"][0]["mode"], "descriptor")


if __name__ == "__main__":
    unittest.main()
