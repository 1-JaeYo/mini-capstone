"""Analytics endpoints derived from stored songs."""

from flask import Blueprint, jsonify
from app.services.similarity_service import get_similar_songs

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/similarity/<int:song_id>")
def similarity(song_id):
    """Return similarity matches for one base song."""
    base_song, similar_songs = get_similar_songs(song_id)

    if base_song is None:
        return jsonify({"error": "Song not found"}), 404

    return jsonify({
        "base_song": {
            "id": base_song.id,
            "title": base_song.title,
            "artist_name": base_song.artist_name,
        },
        "similar_songs": similar_songs,
    })
