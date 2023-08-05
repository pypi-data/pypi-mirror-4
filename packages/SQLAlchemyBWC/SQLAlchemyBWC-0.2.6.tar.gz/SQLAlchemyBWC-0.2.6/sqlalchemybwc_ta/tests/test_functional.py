from blazeweb.globals import ag
from blazeweb.tasks import run_tasks
from blazeweb.testing import TestApp
from nose.plugins.skip import SkipTest
from nose.tools import eq_
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemybwc import db

from sqlalchemybwc_ta.application import make_wsgi
from sqlalchemybwc_ta.model.orm import Car

class TestTemplates(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)
        Car.delete_all()
        Car.add(**{
            'make': u'chevy',
            'model': u'cav',
            'year': 2010
        })

    def test_index(self):
        r = self.ta.get('/')
        assert 'Index Page' in r

    def test_one_db_session(self):
        c = Car.first()
        assert c.make
        self.ta.get('/')
        try:
            assert c.make
            assert False, 'expected DetachedInstanceError'
        except DetachedInstanceError:
            pass

    def test_split_db_sessions(self):
        raise SkipTest
        """ something weird happens when this test runs in that
        test_model.py:TestFKs.test_fk_prevent_parent_update() fails
        when running against PGSQL (at least)
        """
        wsgiapp = make_wsgi('SplitSessionsTest')
        ta = TestApp(wsgiapp)
        run_tasks('clear-db')
        run_tasks('init-db:~test')
        r = ta.get('/')
        assert 'Index Page' in r

        c = Car.first()
        assert c.make
        ta.get('/')
        assert c.make
