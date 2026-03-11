"""Shared Flask extension instances."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemy database handle used across models/routes/services.
db = SQLAlchemy()

# Flask-Migrate integration for Alembic database migrations.
migrate = Migrate()
