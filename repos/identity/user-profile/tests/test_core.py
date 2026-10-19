from user_profile.core import add


def test_add():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, 1) == 0


def test_loop():
    from user_profile.core import LOOP
    assert LOOP is not None
