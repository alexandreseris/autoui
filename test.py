import logging
from autoui.launcher import launch


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_params(a: str, b: bool = True):
    """test_params function

    long descr test_params

    Args:
        a (str): descr a
        b (bool, optional): descr b. Defaults to True.
    """
    logger.info(f"called test_params using {a, b}")


def test_noparam():
    """test_noparam function

    long descr test_noparam
    """
    logger.info("called test_noparam")


def test_err():
    """test_err function

    long descr test_err
    """
    logger.info("called test_err")
    raise ValueError("exception on test_err")


launch({"test_params": test_params, "test_noparam": test_noparam, "test_err": test_err}, logger=logger)
