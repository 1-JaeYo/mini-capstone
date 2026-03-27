"""Song CRUD/read endpoints."""

from flask import Blueprint, jsonify, redirect
from app.extensions import db
from app.models.song import Song
from app.services.deezer_service import get_track_by_id

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


@songs_bp.get("/<int:song_id>/preview")
def get_song_preview(song_id):
    """Refresh the Deezer preview URL on demand and redirect to it."""
    song = Song.query.get_or_404(song_id)
    if not song.deezer_id:
        return jsonify({"error": "No preview clip is available for this song"}), 404

    try:
        deezer_track = get_track_by_id(song.deezer_id)
    except Exception as exc:
        return jsonify({"error": f"Failed to refresh preview clip: {exc}"}), 502

    fresh_preview_url = (deezer_track or {}).get("preview_url")
    if not fresh_preview_url:
        return jsonify({"error": "No preview clip is available for this song"}), 404

    song.preview_url = fresh_preview_url
    if deezer_track.get("gain") is not None:
        song.gain = deezer_track["gain"]
    if song.tempo is None and deezer_track.get("tempo") is not None:
        song.tempo = deezer_track["tempo"]
    db.session.commit()

    return redirect(fresh_preview_url, code=302)


@songs_bp.delete("/<int:song_id>")
def delete_song(song_id):
    """Delete one song from the dataset."""
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": "Song removed from dataset", "song_id": song_id})
