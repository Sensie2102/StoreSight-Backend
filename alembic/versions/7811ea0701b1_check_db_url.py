"""Check DB URL

Revision ID: 7811ea0701b1
Revises: aceb687f22d5
Create Date: 2025-03-30 16:56:30.139861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = '7811ea0701b1'
down_revision: Union[str, None] = 'aceb687f22d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Drop the existing primary key constraint
    op.drop_constraint('users_pkey', 'users', type_='primary')

    # Step 2: Add new 'id' column with UUID
    # op.add_column('users', sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4))

    # Step 3: Set 'id' as the new primary key
    op.create_primary_key('users_pkey', 'users', ['id'])

    # Step 4: Add unique constraint to email (if not already)
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

def downgrade():
    # Reverse everything step-by-step
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('users', 'id')
    op.create_primary_key('users_pkey', 'users', ['email'])
