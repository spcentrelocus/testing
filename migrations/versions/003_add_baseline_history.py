"""Add baseline history

Revision ID: 003_baseline_history
Revises: 002_emission_factors
Create Date: 2024-02-02 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_baseline_history'
down_revision: Union[str, None] = '002_emission_factors'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('baseline_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('building_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period', sa.String(), nullable=False),
        sa.Column('raw_kwh', sa.Float(), nullable=False),
        sa.Column('adjusted_kwh', sa.Float(), nullable=False),
        sa.Column('weather_factor', sa.Float(), nullable=False),
        sa.Column('occupancy_factor', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], )
    )


def downgrade() -> None:
    op.drop_table('baseline_history')
