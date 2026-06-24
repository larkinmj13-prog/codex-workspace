from stockgod.data.edgar import (
    classify_form4_transaction_code,
    is_potential_form4_purchase,
    is_qualifying_purchase_code,
)


def test_p_is_potential_purchase_and_qualifying_code_only():
    assert classify_form4_transaction_code("P") == "potential_purchase"
    assert is_potential_form4_purchase("P") is True
    assert is_qualifying_purchase_code("P") is True


def test_award_exercise_and_tax_codes_are_not_qualifying_purchases():
    expected = {
        "A": "grant_or_award",
        "M": "option_exercise_or_conversion",
        "F": "tax_or_payment_related",
    }
    for code, label in expected.items():
        assert classify_form4_transaction_code(code) == label
        assert is_qualifying_purchase_code(code) is False


def test_unknown_or_missing_code_is_unverified():
    assert classify_form4_transaction_code(None) == "unknown_or_unverified"
    assert classify_form4_transaction_code("?") == "unknown_or_unverified"
