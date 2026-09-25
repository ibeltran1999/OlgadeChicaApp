"""Registro de recursos asociados a filminas y bocetos."""

from alembic import op
import sqlalchemy as sa

revision = "20260925_0003"
down_revision = "20260925_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recursos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("identificador", sa.String(100), nullable=False, unique=True),
        sa.Column("nombre", sa.String(500), nullable=False),
        sa.Column("tipo", sa.String(100), nullable=False),
        sa.Column(
            "archivo_id", sa.Integer(), sa.ForeignKey("archivos.id"), unique=True
        ),
        sa.Column("filmina_id", sa.Integer(), sa.ForeignKey("filminas.id")),
        sa.Column("boceto_id", sa.Integer(), sa.ForeignKey("bocetos.id")),
        sa.CheckConstraint(
            "filmina_id IS NOT NULL OR boceto_id IS NOT NULL",
            name="ck_recurso_asociado",
        ),
    )


def downgrade():
    op.drop_table("recursos")
