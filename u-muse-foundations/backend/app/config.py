"""Runtime configuration for the Flask backend."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration values loaded from environment variables."""

    # Database defaults to the local SQLite file in backend/instance.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///u_muse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Spotify credentials are optional but required for live imports.
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

    # MusicBrainz asks clients to send a descriptive user agent.
    MUSIC_METADATA_USER_AGENT = os.getenv(
        "MUSIC_METADATA_USER_AGENT",
        "U-Muse Foundations/1.0 (local metadata lookup)",
    )
    MUSIC_METADATA_CONTACT = os.getenv("MUSIC_METADATA_CONTACT")
