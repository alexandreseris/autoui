import logging
from autoui.lib.utils import convert_date_to_string


class LogHandlerWeb(logging.Handler):
    def __init__(self, callback):
        logging.Handler.__init__(self)
        self.callback = callback

    def emit(self, record: logging.LogRecord):
        datetime = convert_date_to_string(record.created)
        is_error = True if record.levelno >= logging.ERROR else False
        self.callback(datetime, record.levelname, is_error, record.msg)

    def add_to_logger(self, logger: logging.Logger):
        found = False
        for handler in logger.handlers:
            if type(handler) is type(self):
                found = True
                break
        if not found:
            logger.addHandler(self)
