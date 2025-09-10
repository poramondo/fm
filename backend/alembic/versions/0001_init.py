from alembic import op
import sqlalchemy as sa
import uuid

# ревизия
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("currency", sa.String(16), nullable=False),
        sa.Column("address", sa.String(128), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("is_reserved", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_addresses_currency", "addresses", ["currency"])

    op.create_table(
        "requests",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("currency", sa.String(16), nullable=False),
        sa.Column("destination_address", sa.String(256), nullable=False),
        sa.Column("contact", sa.String(256), nullable=True),
        sa.Column("payin_address", sa.String(128), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="CREATED"),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_requests_currency", "requests", ["currency"])
    op.create_index("ix_requests_status", "requests", ["status"])
    op.create_index("ix_requests_payin", "requests", ["payin_address"])

def downgrade():
    op.drop_index("ix_requests_payin", table_name="requests")
    op.drop_index("ix_requests_status", table_name="requests")
    op.drop_index("ix_requests_currency", table_name="requests")
    op.drop_table("requests")

    op.drop_index("ix_addresses_currency", table_name="addresses")
    op.drop_table("addresses")
