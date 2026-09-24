"""Create the initial Olga de Chica schema.

Revision ID: 20260924_0001
Revises:
Create Date: 2026-09-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260924_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "archivos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("ruta", sa.String(length=500), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "filminas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identificador", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("procedencia", sa.String(length=100), nullable=False),
        sa.Column("archivo_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["archivo_id"], ["archivos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("archivo_id"),
        sa.UniqueConstraint("identificador", name="uq_filminas_identificador"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identificador", sa.String(length=100), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identificador", name="uq_tags_identificador"),
    )
    op.create_table(
        "filmina_tags",
        sa.Column("filmina_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["filmina_id"], ["filminas.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("filmina_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("filmina_tags")
    op.drop_table("tags")
    op.drop_table("filminas")
    op.drop_table("archivos")
