from code_ import Code


def test_comp():
    assert Code().comp("D+1") == "0011111"


def test_dest():
    assert Code().dest("MD") == "011"


def test_jump():
    assert Code().jump("JLT") == "100"
