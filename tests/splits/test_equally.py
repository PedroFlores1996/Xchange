from app.split.equally import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    users = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, users)

    equal_balance = equal_amounts_between(users)
    for balance in balances.values():
        assert balance == equal_balance


def equal_amounts_between(users: dict[int, float]) -> float:
    return TOTAL_AMOUNT / len(users)
