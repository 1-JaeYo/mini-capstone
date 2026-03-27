"""SQLAlchemy model definitions for songs."""

from app.extensions import db
from app.services.feature_service import dominant_mood


class Song(db.Model):
    """Persisted song record with catalog metadata and derived feature fields."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    spotify_id = db.Column(db.String(100), unique=True, nullable=True)
    musicbrainz_recording_id = db.Column(db.String(36), unique=True, nullable=True)
    deezer_id = db.Column(db.String(32), unique=True, nullable=True)
    album_name = db.Column(db.String(255), nullable=True)
    release_year = db.Column(db.Integer, nullable=True)

    tempo = db.Column(db.Float, nullable=True)
    energy = db.Column(db.Float, nullable=True)
    danceability = db.Column(db.Float, nullable=True)
    valence = db.Column(db.Float, nullable=True)
    acousticness = db.Column(db.Float, nullable=True)
    instrumentalness = db.Column(db.Float, nullable=True)
    loudness = db.Column(db.Float, nullable=True)
    speechiness = db.Column(db.Float, nullable=True)
    liveness = db.Column(db.Float, nullable=True)
    gain = db.Column(db.Float, nullable=True)
    mood_happy = db.Column(db.Float, nullable=True)
    mood_sad = db.Column(db.Float, nullable=True)
    mood_relaxed = db.Column(db.Float, nullable=True)
    mood_party = db.Column(db.Float, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    preview_url = db.Column(db.String(1024), nullable=True)
    essentia_bpm = db.Column(db.Float, nullable=True)
    essentia_beats = db.Column(db.JSON, nullable=True)
    essentia_beat_confidence = db.Column(db.Float, nullable=True)
    essentia_key = db.Column(db.String(16), nullable=True)
    essentia_scale = db.Column(db.String(16), nullable=True)
    essentia_key_strength = db.Column(db.Float, nullable=True)
    essentia_loudness = db.Column(db.Float, nullable=True)
    essentia_energy = db.Column(db.Float, nullable=True)
    essentia_spectral_centroid = db.Column(db.Float, nullable=True)
    essentia_mfcc_mean = db.Column(db.JSON, nullable=True)
    essentia_chords = db.Column(db.JSON, nullable=True)
    essentia_hpcp = db.Column(db.JSON, nullable=True)

    @property
    def has_essentia_features(self):
        """Return True when the core Essentia similarity vector is present."""
        return all(
            value is not None
            for value in (
                self.essentia_bpm,
                self.essentia_energy,
                self.essentia_loudness,
                self.essentia_spectral_centroid,
                self.essentia_mfcc_mean,
            )
        )

    def to_dict(self):
        """Serialize the model for JSON API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "artist_name": self.artist_name,
            "spotify_id": self.spotify_id,
            "musicbrainz_recording_id": self.musicbrainz_recording_id,
            "deezer_id": self.deezer_id,
            "album_name": self.album_name,
            "release_year": self.release_year,
            "tempo": self.tempo,
            "energy": self.energy,
            "danceability": self.danceability,
            "valence": self.valence,
            "acousticness": self.acousticness,
            "instrumentalness": self.instrumentalness,
            "loudness": self.loudness,
            "speechiness": self.speechiness,
            "liveness": self.liveness,
            "gain": self.gain,
            "mood_happy": self.mood_happy,
            "mood_sad": self.mood_sad,
            "mood_relaxed": self.mood_relaxed,
            "mood_party": self.mood_party,
            "duration_ms": self.duration_ms,
            "preview_url": self.preview_url,
            "dominant_mood": dominant_mood(self),
            "has_essentia_features": self.has_essentia_features,
            "essentia": {
                "bpm": self.essentia_bpm,
                "beats": self.essentia_beats,
                "beat_confidence": self.essentia_beat_confidence,
                "key": self.essentia_key,
                "scale": self.essentia_scale,
                "key_strength": self.essentia_key_strength,
                "loudness": self.essentia_loudness,
                "energy": self.essentia_energy,
                "spectral_centroid": self.essentia_spectral_centroid,
                "mfcc_mean": self.essentia_mfcc_mean,
                "chords": self.essentia_chords,
                "hpcp": self.essentia_hpcp,
            },
        }
