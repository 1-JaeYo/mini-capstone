"""Vercel entrypoint for the Flask backend."""

from app import create_app

app = create_app()
