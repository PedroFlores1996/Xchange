from app.splits.percentage import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def amount_from(float_percentage: float) -> float:
    return TOTAL_AMOUNT * float_percentage / 100


def test_single_payer_that_does_not_owe():
    payers = {id1: 100}
    owed_percentages = {id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = split(TOTAL_AMOUNT, payers, owed_percentages)

    assert len(balances) == 5
    assert balances[id1] == TOTAL_AMOUNT
    for ower_id, percentage in owed_percentages.items():
        assert balances[ower_id] == -amount_from(percentage)


def test_single_payer_that_owes():
    payers = {id1: 100}
    owers = {id1: 15, id2: 20.0, id3: 15.0, id4: 25.0, id5: 25.0}
    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances) == 5
    assert balances[id1] == TOTAL_AMOUNT - amount_from(owers[id1])
    for ower_id, percentage in owers.items():
        if ower_id not in payers:
            assert balances[ower_id] == -amount_from(percentage)


def test_multiple_payers_that_do_not_owe():
    payers = {id1: 55.0, id2: 45.0}
    owers = {id3: 50.0, id4: 25.0, id5: 25.0}
    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances) == 5
    for id, percentage in payers.items():
        assert balances[id] == amount_from(percentage)
    for id, percentage in owers.items():
        assert balances[id] == -amount_from(percentage)


def test_multiple_payers_that_owe():
    payers = {id1: 55.0, id2: 45.0}
    owers = {id1: 10, id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances) == 5
    for id, percentage in payers.items():
        assert balances[id] == amount_from(percentage) - amount_from(owers[id])
    for id, percentage in owers.items():
        if id not in payers:
            assert balances[id] == -amount_from(percentage)


def test_multiple_payers_all_owe():
    payers = {id1: 15.0, id2: 5.0, id3: 50.0, id4: 20.0, id5: 10.0}
    owers = {id1: 10, id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances) == 5
    for id, percentage in payers.items():
        assert balances[id] == amount_from(percentage) - amount_from(owers[id])
