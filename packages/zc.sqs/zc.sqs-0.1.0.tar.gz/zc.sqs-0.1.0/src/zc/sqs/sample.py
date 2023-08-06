
import zc.sqs

import time

def sample(conf):

    def handle(t, *args, **kw):
        print args, kw
        if t > time.time():
            raise zc.sqs.TransientError

    return handle


