"""Unit tests for similarity scoring with the new catalog feature set."""

import unittest
from types import SimpleNamespace

from app.services.similarity_service import compute_similarity, compute_similarity_details


def make_song(**overrides):
    """Build a minimal song-like object for similarity tests."""
    defaults = {
        "tempo": None,
        "danceability": None,
        "gain": None,
        "mood_happy": None,
        "mood_sad": None,
        "mood_relaxed": None,
        "mood_party": None,
        "has_essentia_features": False,
        "essentia_bpm": None,
        "essentia_energy": None,
        "essentia_loudness": None,
        "essentia_spectral_centroid": None,
        "essentia_mfcc_mean": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class SimilarityTests(unittest.TestCase):
    """Validate the normalized similarity model."""

    def test_similarity_returns_none_without_shared_features(self):
        song_a = make_song(tempo=120)
        song_b = make_song(mood_party=0.9)

        self.assertIsNone(compute_similarity(song_a, song_b))

    def test_similarity_details_can_disable_descriptor_fallback(self):
        song_a = make_song(tempo=120, danceability=0.82, mood_party=0.78)
        song_b = make_song(tempo=123, danceability=0.79, mood_party=0.74)

        similarity, mode = compute_similarity_details(
            song_a,
            song_b,
            allow_descriptor_fallback=False,
        )

        self.assertIsNone(similarity)
        self.assertIsNone(mode)

    def test_similarity_scores_close_matches_higher(self):
        song_a = make_song(
            tempo=120,
            danceability=0.82,
            gain=-7.5,
            mood_happy=0.66,
            mood_sad=0.11,
            mood_relaxed=0.20,
            mood_party=0.78,
        )
        song_b = make_song(
            tempo=123,
            danceability=0.79,
            gain=-7.2,
            mood_happy=0.61,
            mood_sad=0.09,
            mood_relaxed=0.18,
            mood_party=0.74,
        )
        song_c = make_song(
            tempo=74,
            danceability=0.22,
            gain=-15.8,
            mood_happy=0.12,
            mood_sad=0.78,
            mood_relaxed=0.66,
            mood_party=0.08,
        )

        similar_score = compute_similarity(song_a, song_b)
        distant_score = compute_similarity(song_a, song_c)

        self.assertIsNotNone(similar_score)
        self.assertIsNotNone(distant_score)
        self.assertGreater(similar_score, distant_score)

    def test_similarity_uses_essentia_vector_when_available(self):
        base = make_song(
            has_essentia_features=True,
            essentia_bpm=120.0,
            essentia_energy=100.0,
            essentia_loudness=40.0,
            essentia_spectral_centroid=2500.0,
            essentia_mfcc_mean=[10.0] * 13,
        )
        close = make_song(
            has_essentia_features=True,
            essentia_bpm=122.0,
            essentia_energy=99.0,
            essentia_loudness=41.0,
            essentia_spectral_centroid=2520.0,
            essentia_mfcc_mean=[10.5] * 13,
        )
        far = make_song(
            has_essentia_features=True,
            essentia_bpm=70.0,
            essentia_energy=5.0,
            essentia_loudness=2.0,
            essentia_spectral_centroid=500.0,
            essentia_mfcc_mean=[-40.0] * 13,
        )

        self.assertGreater(compute_similarity(base, close), compute_similarity(base, far))


if __name__ == "__main__":
    unittest.main()
