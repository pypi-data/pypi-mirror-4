from settings import Test

class TestPostgres(Test):
    """ default profile when running tests """
    def init(self):
        # call parent init to setup default settings
        Test.init(self)
        self.db.url = 'postgresql://postgres:postgres@rcsserver/test'
        #self.db.echo = True
testpgsql = TestPostgres

class TestPYMSSQL(Test):
    """ default profile when running tests """
    def init(self):
        # call parent init to setup default settings
        Test.init(self)
        self.db.url = 'mssql+pymssql://sa:sa@192.168.200.254:1435/temp'
        #self.db.echo = True
testpymssql = TestPYMSSQL
