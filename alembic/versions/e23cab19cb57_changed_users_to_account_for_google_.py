"""Changed users to account for google oauth

Revision ID: e23cab19cb57
Revises: 7811ea0701b1
Create Date: 2025-04-01 15:12:38.510498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e23cab19cb57'
down_revision: Union[str, None] = '7811ea0701b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.execute("""
                ALTER TABLE users 
                ALTER COLUMN google_oauth_token 
                TYPE BOOLEAN 
                USING google_oauth_token::BOOLEAN
                """)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'google_oauth_token',
               existing_type=sa.Boolean(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
