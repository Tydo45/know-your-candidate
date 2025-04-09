"""Add source-linked fields to candidates

Revision ID: 80aaf377b0f9
Revises: 
Create Date: 2025-04-09 11:41:11.323798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '80aaf377b0f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Convert flat string fields to JSON-compatible structures
    op.execute("UPDATE candidates SET party = jsonb_build_object('value', party, 'source_url', '')")
    op.execute("UPDATE candidates SET bio_text = jsonb_build_object('value', bio_text, 'source_url', '')")

    # Step 2: Convert past_positions (VARCHAR[]) to JSONB array of objects
    op.execute("ALTER TABLE candidates ALTER COLUMN past_positions TYPE TEXT")
    op.execute("""
        UPDATE candidates
        SET past_positions = (
            SELECT jsonb_agg(jsonb_build_object('value', val, 'source_url', ''))
            FROM unnest(string_to_array(past_positions, ',')) AS val
        )::text
    """)
    op.execute("ALTER TABLE candidates ALTER COLUMN past_positions TYPE JSONB USING past_positions::jsonb")

    # Step 3: Convert social_links (VARCHAR[]) to JSONB array of strings
    op.execute("ALTER TABLE candidates ALTER COLUMN social_links TYPE TEXT")
    op.execute("UPDATE candidates SET social_links = to_jsonb(string_to_array(social_links, ','))::text")
    op.execute("ALTER TABLE candidates ALTER COLUMN social_links TYPE JSONB USING social_links::jsonb")

    # Step 4: Final casts for remaining converted fields
    op.execute("ALTER TABLE candidates ALTER COLUMN party TYPE JSONB USING party::jsonb")
    op.execute("ALTER TABLE candidates ALTER COLUMN bio_text TYPE JSONB USING bio_text::jsonb")

    # Step 5: Re-create foreign key for versions table
    op.create_foreign_key(None, 'versions', 'candidates', ['candidate_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'versions', type_='foreignkey')
    op.alter_column('candidates', 'social_links',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.ARRAY(sa.VARCHAR()),
               existing_nullable=True)
    op.alter_column('candidates', 'past_positions',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.ARRAY(sa.VARCHAR()),
               existing_nullable=True)
    op.alter_column('candidates', 'bio_text',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('candidates', 'party',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###
