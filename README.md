# AutoUi

## Description

A python lib to help you generate UI for your functions

UI actually availables are:

- command line interface, using build-in [argparse module](https://docs.python.org/3/library/argparse.html)
- json interface, using build-in [json module](https://docs.python.org/fr/3/library/json.html)
- gui interface, using [eel](https://github.com/ChrisKnott/Eel), [bootstrap 5](https://getbootstrap.com/) and [vuejs 2](https://vuejs.org/)

> Written for python 3.6

## Installation

```sh
python setup.py bdist_wheel  # create a .whl file from sources
pip install dist/autoui*.whl  # install .whl file to your environment
```

## Usage

The library is based on the [google docstring format](https://google.github.io/styleguide/pyguide.html) to display usefull information to your users. Docstring parsing is done by [docstring_parser](https://github.com/rr-/docstring_parser)

The google format has been enhanced with two specific pieces of synthax, used exclusivly for the gui mode:

- `::type typename endtype::`: allows to defined a custom type (here `typename`) of HTML input (url, number, paswword and so on, but also textarea, checkbox, select)
    > checkbox type is automatically set when a parameter type is bool
- `::values values endvalues::`: used to populate the option list with specific values. `values` should be split by `;`
    > only (and mandatory) for the input type select

### Basic Usage

Considering you have a file named for instance `main.py`

```python
from autoui import launch
import logging

logger = logging.getLogger()

def function1(a: str, b: int, c: bool = True):
    """function1 short description

    function1 long description

    Args:
        a (str): param a description ::type url endtype::
        b (int): param b description ::type select endtype:: ::values 1;2;3;4 endvalues::
        c (bool, optional): param c description. Defaults to True.
    """
    logger.info(f"called function1 using {a, b, c}")

launch(
    {"custom_name1": function1},  # define the functions you wish to expose. key are the name you wish to display and values are the actual functions
    logger=logger  # logger param is mandatory if you want to use the gui mode, see above
)
```

You then can call `main.py` from command line

The program expose by default differents sub command for accessing the functions you defined in launcher.launch:

- `main.py gui` => starts a web app on a page listing your functions. On each function page, when you submit the form, logger messages are displayed on the page
- `main.py cli function_name args` => starts the function `function_name` with the arguments `args`
- `main.py json function_name json_file_path` => read the json file located in `json_file_path` and pass content to the function `function_name`

### Advanced Usage

The following optionnal parameters are available for the `launcher.launch` function:

- `modes_function_list`: used to generated interface where you ask the user which function he wish to launch. Defaults to (gui_laucher,)
- `modes_target_function`: used to generated interface where a specific function is launched directly . Defaults to (json_laucher, cli_laucher)

Thoses two parameters can be altered with custom functions of your own or even to remove specific launch mode.

See types definitions for more informations.
