import threading

class BaseTask(threading.Thread):
    def __init__(self, realtime_db):
        super(BaseTask, self).__init__()
        self.realtimedb = realtime_db

    @property
    def metrics(self):
        results = self.realtimedb.view('_design/niice_couch/_view/dashboard')
        for r in results :
            yield r.key
