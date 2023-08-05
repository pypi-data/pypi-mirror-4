from blazeweb.config import ComponentSettings

class Settings(ComponentSettings):
    def init(self):
        self.for_me.pre_test_init_tasks = 'clear-db', 'init-db:~test'
        # set to true when you want different sessions for application level and
        # request level code.  Currently used for testing so that entity
        # objects returned from a session don't lose their session the next
        # time a request is ran through WSGI in functional testing.
        self.for_me.use_split_sessions = False
