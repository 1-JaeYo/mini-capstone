"""SQLAlchemy model definitions for songs."""

from app.extensions import db


class Song(db.Model):
    """Persisted song record with optional Spotify-derived audio features."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    spotify_id = db.Column(db.String(100), unique=True, nullable=True)
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
    duration_ms = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        """Serialize the model for JSON API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "artist_name": self.artist_name,
            "spotify_id": self.spotify_id,
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
            "duration_ms": self.duration_ms,
        }
