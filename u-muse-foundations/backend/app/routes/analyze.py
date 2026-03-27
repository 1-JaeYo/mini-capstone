"""Routes for Essentia-based audio analysis of Deezer preview clips."""

from flask import Blueprint, jsonify

from app.extensions import db
from app.models.song import Song
from app.services.analysis_service import (
    AnalysisUnavailableError,
    analyze_song,
    ensure_analysis_runtime_available,
    has_complete_essentia_vector,
)

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.post("/<int:song_id>")
def analyze_one(song_id):
    """Analyze one song preview clip and persist Essentia features."""
    song = Song.query.get_or_404(song_id)

    try:
        ensure_analysis_runtime_available()
        payload = analyze_song(song)
    except AnalysisUnavailableError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"Audio analysis failed: {exc}"}), 502

    return jsonify(
        {
            "message": "Song analyzed successfully",
            "song": song.to_dict(),
            "analysis": payload,
        }
    )


@analyze_bp.post("/batch")
def analyze_batch():
    """Analyze all songs that do not yet have Essentia features."""
    songs = Song.query.all()
    analyzed = []
    skipped = []
    failed = []

    try:
        ensure_analysis_runtime_available()

        for song in songs:
            if has_complete_essentia_vector(song):
                skipped.append({"song_id": song.id, "title": song.title})
                continue

            try:
                analyze_song(song)
                analyzed.append({"song_id": song.id, "title": song.title})
            except AnalysisUnavailableError as exc:
                db.session.rollback()
                return jsonify({"error": str(exc)}), 503
            except Exception as exc:
                db.session.rollback()
                failed.append(
                    {
                        "song_id": song.id,
                        "title": song.title,
                        "error": str(exc),
                    }
                )
    except AnalysisUnavailableError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 503

    return jsonify(
        {
            "message": "Batch analysis completed",
            "analyzed": analyzed,
            "skipped": skipped,
            "failed": failed,
            "summary": {
                "analyzed": len(analyzed),
                "skipped": len(skipped),
                "failed": len(failed),
            },
        }
    )
