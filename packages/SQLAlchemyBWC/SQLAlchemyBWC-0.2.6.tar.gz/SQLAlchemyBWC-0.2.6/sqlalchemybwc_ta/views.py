from blazeweb.views import View

from sqlalchemybwc_ta.model.orm import Car

class Index(View):
    def default(self):
        # need to do something with the DB so that our Session gets removed
        # and any instances bound to it can not refresh
        Car.add(**{
            'make': u'ford',
            'model': u'taurus',
            'year': 2010
        })
        return 'Index Page'
