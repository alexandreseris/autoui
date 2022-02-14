from docstring_parser import parse
from docstring_parser.common import DocstringStyle
from inspect import getfullargspec
from re import search, compile, sub
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docstring_parser import Docstring


def parse_function_doc(function, remove_default_text=False) -> "Docstring":
    function_doc = parse(function.__doc__, style=DocstringStyle.GOOGLE)
    function_args = getfullargspec(function).args
    function_doc_args = list(map(lambda x: x.arg_name, function_doc.params))
    if function_args != function_doc_args:
        missing = [x for x in function_args if x not in function_doc_args]
        excess = [x for x in function_doc_args if x not in function_args]
        order_compare = [
            (actual, doc)
            for actual, doc in zip(function_args, function_doc_args)
            if actual != doc
        ]
        raise ValueError(
            f"The function documentation for {function} is invalid. Details:\n"
            + f"- args not documented: {missing}\n"
            + f"- args documented while not defined in the function: {excess}\n"
            + f"- invalid order: {order_compare}\n"
        )
    # property added on the fly are kinda ugly. used for web launch
    # also functions in the re lib can't get correctly treated by mypy currently
    input_type_reg = compile(r" *::type (.+) endtype:: *")
    values_reg = compile(r" *::values (.+) endvalues:: *")
    description_default_text_reg = compile(r"\. Defaults to (.+)\.$")
    for param in function_doc.params:
        if remove_default_text:
            param.description = sub(description_default_text_reg, "", param.description)  # type: ignore
        param.values = None  # type: ignore
        param.input_type = "text"  # type: ignore
        type_search = search(input_type_reg, param.description)  # type: ignore
        if type_search is not None:
            param.description = sub(input_type_reg, "", param.description)  # type: ignore
            param.input_type = type_search.groups()[0]  # type: ignore
            if param.input_type in ("select"):  # type: ignore
                values_search = search(values_reg, param.description)  # type: ignore
                if values_search is None:
                    raise ValueError(
                        f"parameter {param.arg_name} is defined as select type but has no value defined (reg: ' *::values (.+) endvalues:: *')"
                    )
                param.description = sub(values_reg, "", param.description)  # type: ignore
                values = values_search.groups()[0]
                param.values = values.split(";")  # type: ignore
        elif param.type_name == "bool":
            param.input_type = "checkbox"  # type: ignore
    return function_doc
