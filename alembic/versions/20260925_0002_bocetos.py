"""Tablas para registrar y consultar bocetos."""

from alembic import op
import sqlalchemy as sa

revision = "20260925_0002"
down_revision = "20260924_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bocetos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("identificador", sa.String(100), nullable=False, unique=True),
        sa.Column("descripcion", sa.String(500), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=True),
        sa.Column(
            "archivo_id",
            sa.Integer(),
            sa.ForeignKey("archivos.id"),
            unique=True,
            nullable=True,
        ),
    )
    op.create_table(
        "boceto_tags",
        sa.Column(
            "boceto_id", sa.Integer(), sa.ForeignKey("bocetos.id"), primary_key=True
        ),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id"), primary_key=True),
    )
    op.create_table(
        "boceto_filminas",
        sa.Column(
            "boceto_id", sa.Integer(), sa.ForeignKey("bocetos.id"), primary_key=True
        ),
        sa.Column(
            "filmina_id", sa.Integer(), sa.ForeignKey("filminas.id"), primary_key=True
        ),
    )


def downgrade():
    op.drop_table("boceto_filminas")
    op.drop_table("boceto_tags")
    op.drop_table("bocetos")
