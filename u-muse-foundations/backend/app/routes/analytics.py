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
            "tempo": base_song.tempo,
            "danceability": base_song.danceability,
            "gain": base_song.gain,
            "mood_happy": base_song.mood_happy,
            "mood_sad": base_song.mood_sad,
            "mood_relaxed": base_song.mood_relaxed,
            "mood_party": base_song.mood_party,
        },
        "similar_songs": similar_songs,
    })
