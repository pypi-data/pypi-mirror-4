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

class Median15Seconds(BaseTask):
    def __init__(self, realtime_db, timezone):
        super(Median15Seconds, self).__init__(realtime_db)
        self.timezone = timezone

    def metrics_update(self):
        for metric in self.metrics:
            now = datetime.now(tz=self.timezone)
            key_part = now.astimezone(pytz.utc).strftime("%s")
            results = self.realtimedb.view(
                '_design/niice_couch/_view/data',
                startkey = [metric, int(key_part) - 15],
                endkey = [metric, int(key_part)],
                reduce = True,
                group = True
            )

            values = map(lambda x: x.value, results)

            if not len(values):
                continue

            value = median(values, flatten_func=flatten_complex_median)
            doc = self.realtimedb[metric]
            doc["median_15_seconds"] = value
            self.realtimedb.save(doc)

    def run(self):
        while True:
            sleep(15)
            self.metrics_update()
