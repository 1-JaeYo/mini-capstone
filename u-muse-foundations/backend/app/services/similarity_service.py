"""Song similarity scoring helpers."""

from math import sqrt
from app.models.song import Song


FEATURE_KEYS = [
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


def get_song_feature_vector(song):
    """Extract the configured numeric features from a song instance."""
    return {key: getattr(song, key, None) for key in FEATURE_KEYS}


def compute_similarity(song_a, song_b):
    """Compute similarity with inverse Euclidean distance.

    Returns:
        float | None: Rounded similarity score in [0, 1], or None when the
        two songs do not share any comparable feature values.
    """
    vector_a = get_song_feature_vector(song_a)
    vector_b = get_song_feature_vector(song_b)

    shared_keys = [
        key for key in FEATURE_KEYS
        if vector_a[key] is not None and vector_b[key] is not None
    ]

    if not shared_keys:
        return None

    squared_distance = 0
    for key in shared_keys:
        squared_distance += (vector_a[key] - vector_b[key]) ** 2

    distance = sqrt(squared_distance)

    similarity = 1 / (1 + distance)
    return round(similarity, 4)


def get_similar_songs(song_id, limit=5):
    """Find top-N most similar songs for one base song ID."""
    base_song = Song.query.get(song_id)
    if not base_song:
        return None, []

    other_songs = Song.query.filter(Song.id != song_id).all()
    scored = []

    for song in other_songs:
        similarity = compute_similarity(base_song, song)
        if similarity is not None:
            scored.append({
                "song_id": song.id,
                "title": song.title,
                "artist_name": song.artist_name,
                "similarity_score": similarity,
            })

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return base_song, scored[:limit]
