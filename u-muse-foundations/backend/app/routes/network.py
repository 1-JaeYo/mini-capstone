"""Network graph endpoints for song similarity visualization."""

from flask import Blueprint, jsonify
from app.models.song import Song
from app.services.similarity_service import compute_similarity

network_bp = Blueprint("network", __name__)


@network_bp.get("/")
def get_network():
    """Build a graph payload with nodes (songs) and weighted similarity links."""
    songs = Song.query.all()

    nodes = [
        {
            "id": song.id,
            "label": song.title,
            "artist_name": song.artist_name,
        }
        for song in songs
    ]

    links = []
    threshold = 0.75

    # O(n^2) pairwise comparison keeps implementation simple for small datasets.
    for i in range(len(songs)):
        for j in range(i + 1, len(songs)):
            similarity = compute_similarity(songs[i], songs[j])

            if similarity is not None and similarity >= threshold:
                links.append({
                    "source": songs[i].id,
                    "target": songs[j].id,
                    "weight": similarity,
                })

    return jsonify({
        "nodes": nodes,
        "links": links,
    })
