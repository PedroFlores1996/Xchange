from app.split.percentage import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_split():
    users = {id1: 15, id2: 20, id3: 30, id4: 15, id5: 20}
    balances = split(TOTAL_AMOUNT, users)

    for id, percentage in users.items():
        assert balances[id] == amount_from(percentage)


def amount_from(float_percentage: float) -> float:
    return TOTAL_AMOUNT * float_percentage / 100
