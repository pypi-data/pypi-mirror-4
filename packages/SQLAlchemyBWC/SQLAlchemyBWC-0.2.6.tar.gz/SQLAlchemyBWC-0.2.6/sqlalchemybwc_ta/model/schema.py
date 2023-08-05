import sqlalchemy as sa

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin

Base = declarative_base()

colors = sa.Table('colors', db.meta,
    sa.Column('id', sa.Integer, primary_key = True),
    sa.Column('name', sa.String, nullable = False),
)
