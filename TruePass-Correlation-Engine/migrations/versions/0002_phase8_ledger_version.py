"""phase 8 ledger canonicalization version
Revision ID: 0002_phase8
Revises: 0001_phase3
"""
from alembic import op
import sqlalchemy as sa
revision="0002_phase8"; down_revision="0001_phase3"; branch_labels=None; depends_on=None
def upgrade()->None:
    op.add_column("evidence_records",sa.Column("canonicalization_version",sa.String(length=16),nullable=False,server_default="1"))
def downgrade()->None:
    op.drop_column("evidence_records","canonicalization_version")
