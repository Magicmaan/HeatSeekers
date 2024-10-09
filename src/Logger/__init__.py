from logging import getLogger, Handler
class QueueHandler(Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)
        getLogger().info(record)
        print(record)

from .Logger import CustomLogger, LoggerUI


Logger = LoggerUI
__all__ = [
    "CustomLogger",
    "LoggerUI",
]