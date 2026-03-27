"""add catalog metadata fields

Revision ID: 2f8d4f9aef31
Revises: 6f6933463d9f
Create Date: 2026-03-24 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f8d4f9aef31"
down_revision = "6f6933463d9f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("songs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("musicbrainz_recording_id", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("deezer_id", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("gain", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("mood_happy", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("mood_sad", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("mood_relaxed", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("mood_party", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("preview_url", sa.String(length=1024), nullable=True))
        batch_op.create_unique_constraint("uq_songs_musicbrainz_recording_id", ["musicbrainz_recording_id"])
        batch_op.create_unique_constraint("uq_songs_deezer_id", ["deezer_id"])


def downgrade():
    with op.batch_alter_table("songs", schema=None) as batch_op:
        batch_op.drop_constraint("uq_songs_deezer_id", type_="unique")
        batch_op.drop_constraint("uq_songs_musicbrainz_recording_id", type_="unique")
        batch_op.drop_column("preview_url")
        batch_op.drop_column("mood_party")
        batch_op.drop_column("mood_relaxed")
        batch_op.drop_column("mood_sad")
        batch_op.drop_column("mood_happy")
        batch_op.drop_column("gain")
        batch_op.drop_column("deezer_id")
        batch_op.drop_column("musicbrainz_recording_id")
