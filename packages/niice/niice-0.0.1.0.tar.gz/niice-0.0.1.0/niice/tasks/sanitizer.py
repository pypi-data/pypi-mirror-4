from datetime import datetime
from time import sleep
import pytz
from niice.tasks.basetask import BaseTask
from niice.utils import median, flatten

def flatten_complex_median(x, y):
    if type(x) is dict:
        result = {}
        for key in x.keys():
            result[key] = flatten(x[key], y[key])
        return result
    elif type(x) is list:
        result = []
        for i, item in enumerate(x):
            result.append(flatten(x[i], y[i]))
        return result
    else:
        return flatten(x, y)

class Sanitizer(BaseTask):
    def __init__(self, realtime_db, timezone):
        super(Sanitizer, self).__init__(realtime_db)
        self.timezone = timezone
        self.interval = 3600
        self.drop_after = 3600*24

    def drop_data(self):
        now = datetime.now(tz=self.timezone)
        now_unix = now.astimezone(pytz.utc).strftime("%s")
        end_key = int(now_unix) - self.drop_after

        results = self.realtimedb.view(
            '_design/niice_couch/_view/data_by_time',
            limit = 1
        )
        if len(results) == 1:
            start_key = results.rows[0].key
        else:
            print "sanitizer: no data"
            return

        if start_key > end_key:
            print "sanitizer: nothing to do start_key: %s > end_key: %s" % (start_key, end_key)
            return

        results = self.realtimedb.view(
            '_design/niice_couch/_view/data_by_time',
            startkey = start_key,
            endkey = end_key,
            limit = 100
        )

        ids = map(lambda x: x.value, results)
        if not len(ids):
            return

        for id in ids:
            doc = self.realtimedb[id]
            self.realtimedb.delete(doc)

        sleep(0.1)
        self.drop_data()

    def run(self):
        while True:
            self.drop_data()
            sleep(self.interval)
