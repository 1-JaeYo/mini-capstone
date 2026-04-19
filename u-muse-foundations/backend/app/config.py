"""Runtime configuration for the Flask backend."""

import os
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration values loaded from environment variables."""

    # Use Postgres in hosted/serverless environments and SQLite locally.
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        if os.getenv("VERCEL"):
            raise RuntimeError(
                "DATABASE_URL is required in the Vercel environment. "
                "Configure it in Vercel Project Settings -> Environment Variables."
            )
        DATABASE_URL = "sqlite:///u_muse.db"

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    elif "://" in DATABASE_URL and not DATABASE_URL.startswith(("sqlite://", "postgresql://")):
        raise RuntimeError(
            "DATABASE_URL must start with sqlite:// or postgresql://. "
            "Check for a typo in the configured connection string."
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Supabase transaction-pooler / serverless deployments should not use
    # SQLAlchemy's default connection pool on top of the provider pooler.
    if (
        "pooler.supabase.com" in DATABASE_URL
        or os.getenv("VERCEL")
    ):
        SQLALCHEMY_ENGINE_OPTIONS["poolclass"] = NullPool

    # Spotify credentials are optional but required for live imports.
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

    # MusicBrainz asks clients to send a descriptive user agent.
    MUSIC_METADATA_USER_AGENT = os.getenv(
        "MUSIC_METADATA_USER_AGENT",
        "U-Muse Foundations/1.0 (local metadata lookup)",
    )
    MUSIC_METADATA_CONTACT = os.getenv("MUSIC_METADATA_CONTACT")
