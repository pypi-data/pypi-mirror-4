from os import path

from blazeweb.config import DefaultSettings

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)

class Default(DefaultSettings):
    def init(self):
        self.dirs.base = basedir
        self.app_package = app_package
        DefaultSettings.init(self)

        self.add_component(app_package, 'foo')
        self.add_component(app_package, 'sqlalchemy', 'sqlalchemybwc')

        self.add_route('/', 'Index')

class Dev(Default):
    def init(self):
        Default.init(self)
        self.apply_dev_settings()

        self.db.url = 'sqlite://'

class Test(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.db.url = 'sqlite://'

        # uncomment this if you want to use a database you can inspect
        #from os import path
        #self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')

class SplitSessionsTest(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        self.db.url = 'sqlite://'

        self.components.sqlalchemy.use_split_sessions = True

try:
    from site_settings import *
except ImportError, e:
    if 'No module named site_settings' not in str(e):
        raise
