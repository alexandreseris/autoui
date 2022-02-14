import eel
import os
import logging
from traceback import format_stack
from sys import exit
from autoui.lib.utils import exception_detail
from autoui.lib.web_logger import LogHandlerWeb
from typing import TYPE_CHECKING, Dict, Callable
if TYPE_CHECKING:
    from docstring_parser import Docstring
    from logging import Logger

current_dir = os.path.realpath(os.path.dirname(__file__))
web_dir = os.path.join(current_dir, "web")


def start_web_app(program_list: Dict[str, Callable], functions_doc: Dict[str, "Docstring"], logger: "Logger"):
    eel.init(web_dir, allowed_extensions=['.js', '.html'])

    @eel.expose
    def launch_function(*args, **kwargs):
        # eel.logcallback is defined on the client side
        LogHandlerWeb(eel.logcallback).add_to_logger(logger)  # type: ignore
        function = program_list[args[0]]
        args = args[1:]
        try:
            function(*args, **kwargs)
        except Exception as err:
            if logger.level == logging.DEBUG:
                logger.fatal(exception_detail(err))
            else:
                logger.fatal(f"ERROR {type(err)}\n{err}")

    @eel.expose()
    def get_function_doc(function_name):
        function_doc = functions_doc[function_name]
        res = {}
        res["short_description"] = function_doc.short_description
        res["long_description"] = function_doc.long_description
        res["params"] = []
        for param in function_doc.params:
            param_obj = {
                "arg_name": param.arg_name,
                "description": param.description,
                "is_optional": param.is_optional,
                "type_name": param.type_name,
                "input_type": param.input_type,  # type: ignore
                "values": param.values,  # type: ignore
            }
            if param.default is not None:
                param_obj["default"] = eval(param.default)
            res["params"].append(param_obj)
        return res

    @eel.expose
    def function_list():
        program_list_render = []
        for program_name in program_list:
            program_list_render.append([program_name, functions_doc[program_name].short_description])
        return program_list_render

    print_stack_on_exit = False

    def close_callback(page: str, sockets: list):
        print("closing web app")
        print(f"page: {page}")
        print(f"sockets: {sockets}")
        if print_stack_on_exit:
            for line in format_stack():
                print(line)
        print("bye!")
        exit()

    eel.start(
        "main.html",
        close_callback=close_callback,
        # cmdline_args=["--auto-open-devtools-for-tabs"],
    )
