"""Song CRUD/read endpoints."""

from flask import Blueprint, jsonify
from app.models.song import Song

songs_bp = Blueprint("songs", __name__)


@songs_bp.get("/")
def get_songs():
    """Return all songs currently stored in the dataset."""
    songs = Song.query.all()
    return jsonify([song.to_dict() for song in songs])


@songs_bp.get("/<int:song_id>")
def get_song(song_id):
    """Return one song by numeric ID or 404 if it does not exist."""
    song = Song.query.get_or_404(song_id)
    return jsonify(song.to_dict())
