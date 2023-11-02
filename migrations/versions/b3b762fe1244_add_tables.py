"""add tables

Revision ID: b3b762fe1244
Revises: 
Create Date: 2023-11-02 05:29:05.247680

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b3b762fe1244'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('charge_point',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('charging_error_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=False),
    sa.Column('errors', sa.JSON(), nullable=False),
    sa.Column('type', sa.Enum('payload_validation', 'missing_resource', name='errortype'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('charging_session',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehicle',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('battery_capacity', sa.Float(), nullable=False),
    sa.Column('max_charging_power', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('charging_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('current_progress', sa.Float(), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=False),
    sa.Column('charge_point_id', sa.Uuid(), nullable=False),
    sa.Column('vehicle_id', sa.Uuid(), nullable=False),
    sa.Column('charging_session_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['charge_point_id'], ['charge_point.id'], ),
    sa.ForeignKeyConstraint(['charging_session_id'], ['charging_session.id'], ),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicle.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('charging_status')
    op.drop_table('vehicle')
    op.drop_table('charging_session')
    op.drop_table('charging_error_log')
    op.drop_table('charge_point')
    # ### end Alembic commands ###