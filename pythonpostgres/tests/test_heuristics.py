from src.heuristics import try_heuristics

def test_simple_brand_dash():
    b, m, c = try_heuristics("Acme - Super Widget 16oz")
    assert b == "Acme"
    assert m == "Acme"
    assert c >= 0.6   # high confidence

def test_by_brand():
    b, m, c = try_heuristics("Super Widget by Globex")
    assert b == "Globex"
    assert m == "Globex"
    assert c >= 0.6

def test_generic_word_not_taken():
    b, m, c = try_heuristics("Premium Quality Cookies")
    assert b is None
    assert m is None
    assert c == 0.0

def test_short_token_as_brand():
    b, m, c = try_heuristics("Nestle Chocolate Bar")
    assert b == "Nestle"
    assert m == "Nestle"
    assert c >= 0.45
