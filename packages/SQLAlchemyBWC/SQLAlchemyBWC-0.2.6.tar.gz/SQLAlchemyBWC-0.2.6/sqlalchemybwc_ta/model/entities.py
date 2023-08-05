import sqlalchemy as sa

from blazeutils.strings import randchars

from compstack.sqlalchemy.lib.declarative import declarative_base, DefaultMixin

Base = declarative_base()

class Blog(Base, DefaultMixin):
    __tablename__ = 'blogs'

    title = sa.Column(sa.Unicode(255), nullable=False)
    # use this, instead of id, so we can do tests on updating it without
    # running into problems on the db side by trying to update an identity
    # or PK column
    ident = sa.Column(sa.String(12), unique=True, nullable=False, default=lambda: randchars())

class Comment(Base, DefaultMixin):
    __tablename__ = 'comments'

    blog_ident = sa.Column(sa.String(12), sa.ForeignKey('blogs.ident'), nullable=False)
