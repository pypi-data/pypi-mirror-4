from blazeweb.events import signal
from blazeweb.globals import settings
from blazeweb.tasks import run_tasks

def setup_db_structure(sender):
    if settings.components.sqlalchemy.pre_test_init_tasks:
        run_tasks(settings.components.sqlalchemy.pre_test_init_tasks)
signal('blazeweb.pre_test_init').connect(setup_db_structure)
