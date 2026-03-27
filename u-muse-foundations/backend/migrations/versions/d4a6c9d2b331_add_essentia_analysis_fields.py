"""add essentia analysis fields

Revision ID: d4a6c9d2b331
Revises: 2f8d4f9aef31
Create Date: 2026-03-26 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4a6c9d2b331"
down_revision = "2f8d4f9aef31"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("songs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("essentia_bpm", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_beats", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("essentia_beat_confidence", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_key", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("essentia_scale", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("essentia_key_strength", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_loudness", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_energy", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_spectral_centroid", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("essentia_mfcc_mean", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("essentia_chords", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("essentia_hpcp", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("songs", schema=None) as batch_op:
        batch_op.drop_column("essentia_hpcp")
        batch_op.drop_column("essentia_chords")
        batch_op.drop_column("essentia_mfcc_mean")
        batch_op.drop_column("essentia_spectral_centroid")
        batch_op.drop_column("essentia_energy")
        batch_op.drop_column("essentia_loudness")
        batch_op.drop_column("essentia_key_strength")
        batch_op.drop_column("essentia_scale")
        batch_op.drop_column("essentia_key")
        batch_op.drop_column("essentia_beat_confidence")
        batch_op.drop_column("essentia_beats")
        batch_op.drop_column("essentia_bpm")
