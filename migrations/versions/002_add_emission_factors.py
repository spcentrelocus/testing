"""Add emission factors table

Revision ID: 002_emission_factors
Revises: 001_initial_schema
Create Date: 2024-02-02 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_emission_factors'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('emission_factors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region_id', sa.String(), nullable=False),
        sa.Column('region_name', sa.String(), nullable=False),
        sa.Column('factor_kg_per_kwh', sa.Float(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emission_factors_region_id'), 'emission_factors', ['region_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_emission_factors_region_id'), table_name='emission_factors')
    op.drop_table('emission_factors')
