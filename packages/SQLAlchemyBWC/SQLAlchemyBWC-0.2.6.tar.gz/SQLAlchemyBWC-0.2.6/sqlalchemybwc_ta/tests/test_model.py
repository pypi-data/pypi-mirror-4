
from nose.plugins.skip import SkipTest

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.helpers import is_fk_exc, is_null_exc
from sqlalchemybwc_ta.model.entities import Blog, Comment
from sqlalchemybwc_ta.model.schema import colors

class TestBlog(object):

    def setUp(self):
        Blog.delete_all()

    def test_add(self):
        """ this test is just to make sure that middleware.py is auto loading
        model/schema.py.  If it wasn't, then the below would throw an exception. """
        b = Blog.add(title=u'foo')
        assert b.id > 0
        assert b.createdts

class TestColors(object):

    def test_add(self):
        """ this test is just to make sure that middleware.py is auto loading
        model/schema.py.  If it wasn't, then the below would throw an exception. """
        result = db.engine.execute(colors.select())
        assert result

class TestIntegrity(object):

    def setUp(self):
        Comment.delete_all()
        Blog.delete_all()
        self.bid = Blog.add(title=u'foo').ident

    def test_ok(self):
        assert Comment.add(blog_ident=self.bid)

    def test_fk_prevent_insert(self):
        try:
            Comment.add(blog_ident=10000)
            assert False, 'expected FK exception'
        except Exception, e:
            db.sess.rollback()
            if not is_fk_exc(e, 'blog_ident', 'ident'):
                raise

    def test_fk_prevent_update(self):
        c = Comment.add(blog_ident=self.bid)
        c.blog_ident = 10000
        try:
            db.sess.commit()
            assert False, 'expected FK exception'
        except Exception, e:
            db.sess.rollback()
            if not is_fk_exc(e, 'blog_ident', 'ident'):
                raise

    def test_fk_prevent_parent_delete(self):
        b = Blog.add(title=u'foo')
        Comment.add(blog_ident=b.ident)
        try:
            Blog.delete(b.id)
            assert False, 'expected FK exception'
        except Exception, e:
            db.sess.rollback()
            if not is_fk_exc(e, 'blog_ident', 'ident'):
                raise

    def test_fk_prevent_parent_update(self):
        if db.engine.dialect.name == 'sqlite':
            # not supported by SQLiteFKTG4SA
            # http://code.google.com/p/sqlitefktg4sa/issues/detail?id=3
            raise SkipTest
        b = Blog.add(title=u'foo')
        Comment.add(blog_ident=b.ident)
        b.ident = u'12345'
        try:
            db.sess.commit()
            assert False, 'expected FK exception'
        except Exception, e:
            db.sess.rollback()
            if not is_fk_exc(e, 'blog_ident', 'ident'):
                raise

    def test_not_nullable(self):
        try:
            Blog.add(title=None)
            assert False, 'expected not null exception'
        except Exception, e:
            db.sess.rollback()
            if not is_null_exc(e, 'title'):
                raise
