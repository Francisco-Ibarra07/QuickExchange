# Sample/intro file to using pytest
def func(x):
    return x + 1


def test_answer():
    assert func(5) == 6
