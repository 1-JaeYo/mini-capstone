"""Song similarity scoring helpers."""

from math import sqrt

import numpy as np

from app.extensions import db
from app.models.song import Song
from app.services.analysis_service import normalized_essentia_similarity_vector
from app.services.feature_service import (
    SIMILARITY_FEATURE_KEYS,
    format_feature_labels,
    get_shared_feature_keys,
    normalize_feature_value,
)


def get_song_feature_vector(song):
    """Extract the normalized comparison vector from a song instance."""
    return {
        key: normalize_feature_value(key, getattr(song, key, None))
        for key in SIMILARITY_FEATURE_KEYS
    }


def compute_similarity_details(song_a, song_b, allow_descriptor_fallback=True):
    """Return similarity plus the feature mode used for the comparison."""
    essentia_vector_a = normalized_essentia_similarity_vector(song_a)
    essentia_vector_b = normalized_essentia_similarity_vector(song_b)
    if essentia_vector_a is not None and essentia_vector_b is not None:
        similarity = float(np.dot(essentia_vector_a, essentia_vector_b))
        return round(max(-1.0, min(1.0, similarity)), 4), "essentia"

    if not allow_descriptor_fallback:
        return None, None

    vector_a = get_song_feature_vector(song_a)
    vector_b = get_song_feature_vector(song_b)

    shared_keys = [
        key for key in SIMILARITY_FEATURE_KEYS
        if vector_a[key] is not None and vector_b[key] is not None
    ]

    if not shared_keys:
        return None, None

    squared_distance = 0.0
    for key in shared_keys:
        squared_distance += (vector_a[key] - vector_b[key]) ** 2

    distance = sqrt(squared_distance)
    similarity = 1 / (1 + distance)
    return round(similarity, 4), "descriptor"


def compute_similarity(song_a, song_b, allow_descriptor_fallback=True):
    """Compute similarity using Essentia vectors when available, else descriptors."""
    similarity, _mode = compute_similarity_details(
        song_a,
        song_b,
        allow_descriptor_fallback=allow_descriptor_fallback,
    )
    return similarity


def get_similar_songs(song_id, limit=5):
    """Find top-N most similar songs for one base song ID."""
    base_song = db.session.get(Song, song_id)
    if not base_song:
        return None, []

    other_songs = Song.query.filter(Song.id != song_id).all()
    scored = []

    for song in other_songs:
        similarity = compute_similarity(base_song, song)
        if similarity is not None:
            if (
                normalized_essentia_similarity_vector(base_song) is not None
                and normalized_essentia_similarity_vector(song) is not None
            ):
                shared_feature_keys = [
                    "essentia bpm",
                    "essentia energy",
                    "essentia loudness",
                    "essentia spectral centroid",
                    "essentia mfcc",
                ]
            else:
                shared_feature_keys = get_shared_feature_keys(base_song, song)
            scored.append({
                "song_id": song.id,
                "title": song.title,
                "artist_name": song.artist_name,
                "similarity_score": similarity,
                "shared_features": (
                    shared_feature_keys
                    if shared_feature_keys and shared_feature_keys[0].startswith("essentia")
                    else format_feature_labels(shared_feature_keys)
                ),
            })

    scored.sort(key=lambda item: item["similarity_score"], reverse=True)
    return base_song, scored[:limit]
