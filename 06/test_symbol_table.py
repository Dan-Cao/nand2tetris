from symbol_table import SymbolTable


def test_symbol_table():
    table = SymbolTable()

    assert table.contains("foo") is False

    table.add_entry("foo", 12)
    assert table.contains("foo") is True
    assert table.get_address("foo") == 12
