from traceback import format_exception
from datetime import datetime
from time import localtime, strftime


def exception_detail(exception):
    return "".join(format_exception(type(exception), exception, exception.__traceback__))


def convert_date_to_string(datetime_obj):
    format_str = "%Y-%m-%d %H:%M:%S"
    if type(datetime_obj) is float:
        return strftime("%Y-%m-%d %H:%M:%S", localtime(datetime_obj))
    elif type(datetime_obj) is datetime:
        return datetime_obj.strftime(format_str)
    else:
        raise ValueError("no valid type")
