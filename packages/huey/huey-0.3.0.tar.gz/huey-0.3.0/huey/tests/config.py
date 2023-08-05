import logging
from huey import BaseConfiguration, Invoker
from huey.backends.dummy import DummyQueue, DummyDataStore


test_queue = DummyQueue('test-queue')
test_result_store = DummyDataStore('test-results')

test_invoker = Invoker(test_queue, test_result_store)

class Config(BaseConfiguration):
    QUEUE = test_queue
    RESULT_STORE = test_result_store
    LOGFILE = None
    LOGLEVEL = logging.INFO
    PERIODIC = True
    MAX_DELAY = 60
    BACKOFF = 2
