import argparse
from autoui.lib.doc_function import parse_function_doc
from typing import TYPE_CHECKING, Optional, Callable, Dict, Tuple
from logging import Logger

if TYPE_CHECKING:
    from docstring_parser import Docstring


def _pop_namespace_item(obj: object, prop: str):
    value = None
    try:
        value = obj.__dict__[prop]
        del obj.__dict__[prop]
    except KeyError:
        pass
    return value


def gui_launcher(subparser: argparse._SubParsersAction):
    mode_name = "gui"
    subparser.add_parser(
        mode_name, description="start a GUI where you can launch your functions"
    )

    def callback(
        program_list: Dict[str, Callable],
        functions_doc: Dict[str, "Docstring"],
        logger: Optional["Logger"],
    ):
        from autoui.lib.web_launcher import start_web_app  # noqa

        if not isinstance(logger, Logger):
            raise ValueError("logger arg must be Logger typed if web mode is used")
        start_web_app(program_list, functions_doc, logger)
        return

    return (mode_name, callback)


def cli_launcher(
    subparser: argparse._SubParsersAction,
    program_list: Dict[str, Callable],
    functions_doc: Dict[str, "Docstring"],
):
    mode_name = "cli"
    mode_parser = subparser.add_parser(mode_name, description="command line interface")
    program_command_parsers = mode_parser.add_subparsers(
        help="program", dest="program_name"
    )
    program_command_parsers.required = True
    for program in program_list:
        function_doc = functions_doc[program]
        programm_command = program_command_parsers.add_parser(
            program, description=function_doc.long_description
        )
        for param in function_doc.params:
            if not param.is_optional:
                programm_command.add_argument(
                    param.arg_name, help=param.description
                )
            else:
                arg_name_opt = f"-{param.arg_name.replace('_', '-')}"
                if param.type_name == "bool" and param.default == "False":
                    programm_command.add_argument(
                        arg_name_opt, action="store_true", help=param.description
                    )
                elif param.type_name == "bool" and param.default == "True":
                    programm_command.add_argument(
                        arg_name_opt, action="store_false", help=param.description
                    )
                else:
                    programm_command.add_argument(
                        arg_name_opt,
                        action="store",
                        help=param.description,
                        default=None if param.default is None else eval(param.default),
                    )

    def callback(program_function: Callable, args_parsed: argparse.Namespace):
        program_function(**vars(args_parsed))
        return

    return (mode_name, callback)


def json_launcher(
    subparser: argparse._SubParsersAction,
    program_list: Dict[str, Callable],
    functions_doc: Dict[str, "Docstring"],
):
    mode_name = "json"
    mode_parser = subparser.add_parser(
        mode_name, description="pass arguments for the function using a json file"
    )
    program_command_parsers = mode_parser.add_subparsers(
        help="program", dest="program_name"
    )
    program_command_parsers.required = True
    for program in program_list:
        programm_command = program_command_parsers.add_parser(
            program, description=functions_doc[program].long_description
        )
        programm_command.add_argument(
            "json_path",
            help="path of the json file with function arguments. file must be encoded using utf8 and using \\n as line ending",
        )

    def callback(program_function: Callable, args_parsed: argparse.Namespace):
        from json import loads  # noqa

        with open(args_parsed.json_path, "r", encoding="utf8", newline="\n") as fh:
            params: dict = loads(fh.read())
        params = {k: v for k, v in params.items() if v != ""}
        program_function(**params)
        return

    return (mode_name, callback)


def launch(
    program_list: Dict[str, Callable],
    modes_function_list: Tuple[
        Callable[
            [argparse._SubParsersAction],
            Tuple[str, Callable[
                [Dict[str, Callable], Dict[str, "Docstring"], Optional["Logger"]], None
            ]],
        ],
        ...,
    ] = (gui_launcher,),
    modes_target_function: Tuple[
        Callable[
            [
                argparse._SubParsersAction,
                Dict[str, Callable],
                Dict[str, "Docstring"],
            ],
            Tuple[str, Callable[[Callable, argparse.Namespace], None]],
        ],
        ...,
    ] = (cli_launcher, json_launcher),
    logger: Optional["Logger"] = None,
):
    """main function of the package. allow to generate user interface for your custom function

    Args:
        program_list (Dict[str, Callable]): dictionnary of function you wish to expose. Keys are displayed names, values are actual functions
        modes_function_list (Tuple[Callable, ...], optional): tuple of function where user can interactively choose a function. Defaults to (gui_launcher,).
        modes_target_function (Tuple[Callable, ...], optional): tuple of function launching immediatly a function in program_list. Defaults to (cli_launcher, json_launcher).
        logger (Logger, optional): logger used for the gui launch mode. Defaults to None.
    """
    parser = argparse.ArgumentParser(
        description=(
            "launcher script for running your custom functions.\n"
            + f"{len(modes_function_list) + len(modes_target_function)} interfaces: {', '.join([x.__name__ for x in (modes_function_list + modes_target_function)])}"
        )
    )
    mode_parsers = parser.add_subparsers(help="mode", dest="mode_name")
    mode_parsers.required = True

    functions_doc: Dict[str, "Docstring"] = {}
    for program, program_func in program_list.items():
        functions_doc[program] = parse_function_doc(program_func)

    modes_function_list_dict: Dict[str, Callable] = {}
    for mode_function_list in modes_function_list:
        mode_name, callback = mode_function_list(mode_parsers)
        modes_function_list_dict[mode_name] = callback
    modes_target_function_dict: Dict[str, Callable] = {}
    for mode_target_function in modes_target_function:
        mode_name, callback2 = mode_target_function(mode_parsers, program_list, functions_doc)
        modes_target_function_dict[mode_name] = callback2

    args_parsed = parser.parse_args()
    launch_mode = _pop_namespace_item(args_parsed, "mode_name")
    if type(launch_mode) is not str:
        raise ValueError("mode_name should be str typed")
    program_name = _pop_namespace_item(args_parsed, "program_name")
    mode_function_list_callback = modes_function_list_dict.get(launch_mode)
    if mode_function_list_callback is not None:
        mode_function_list_callback(program_list, functions_doc, logger)
        return

    if type(program_name) is not str:
        raise ValueError("program_name should be str typed")
    mode_target_function_callback = modes_target_function_dict.get(launch_mode)
    if mode_target_function_callback is not None:
        mode_target_function_callback(program_list[program_name], args_parsed)
        return
