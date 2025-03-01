from app.splits.percentage import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    payers = {id1: 100}
    owed_percentages = {id2: 20, id3: 30, id4: 25, id5: 25}
    balances = split(TOTAL_AMOUNT, payers, owed_percentages)

    validate_balances(payers, owed_percentages, balances)


def test_single_payer_that_owes():
    payers = {id1: 100}
    owers = {id1: 15, id2: 20, id3: 15, id4: 25, id5: 25}
    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_multiple_payers_that_do_not_owe():
    payers = {id1: 55, id2: 45}
    owers = {id3: 50, id4: 25, id5: 25}
    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_multiple_payers_that_owe():
    payers = {id1: 55, id2: 45}
    owers = {id1: 10, id2: 20, id3: 30, id4: 25, id5: 25}
    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_multiple_payers_all_owe():
    payers = {id1: 15, id2: 5, id3: 50, id4: 20, id5: 10}
    owers = {id1: 10, id2: 20, id3: 30, id4: 25, id5: 25}
    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def validate_balances(payers, owers, balances):
    assert len(balances) == 5
    for id, percentage in payers.items():
        owed = amount_from(owers.get(id, 0))
        payed = amount_from(percentage)
        assert balances[id]["owed"] == owed
        assert balances[id]["payed"] == payed
        assert balances[id]["total"] == payed - owed
    for id, percentage in owers.items():
        owed = amount_from(percentage)
        payed = amount_from(payers.get(id, 0))
        assert balances[id]["owed"] == owed
        assert balances[id]["payed"] == payed
        assert balances[id]["total"] == payed - owed


def amount_from(float_percentage: float) -> float:
    return TOTAL_AMOUNT * float_percentage / 100
