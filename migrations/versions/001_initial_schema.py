"""Initial tables and Hypertables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-02-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable TimescaleDB Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # 2. Create Users Table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Create Buildings Table
    op.create_table('buildings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('building_type', sa.String(), nullable=True),
        sa.Column('area_sqft', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=False),
        sa.Column('occupancy_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # 4. Create Meter Readings Table (Standard Table first)
    op.create_table('meter_readings',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('building_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value_kwh', sa.Float(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ),
        # No Primary Key constraint because Hypertable chunks might differ
    )

    # 5. Convert to Hypertable
    op.execute("SELECT create_hypertable('meter_readings', 'time');")


def downgrade() -> None:
    op.drop_table('meter_readings')
    op.drop_table('buildings')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # Use cascade to drop extension if needed, but usually safe to leave or:
    # op.execute("DROP EXTENSION IF EXISTS timescaledb CASCADE;")
