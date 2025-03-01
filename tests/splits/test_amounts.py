from app.splits.amounts import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    payers = {id1: TOTAL_AMOUNT}
    owers = {id2: 200, id3: 300, id4: 250, id5: 250}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    assert balances[id1] == TOTAL_AMOUNT
    for ower, amount in owers.items():
        assert balances[ower] == -amount


def test_single_payer_that_owes():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    payers = {id1: TOTAL_AMOUNT}
    owers = {id1: 200, id2: 100, id3: 250, id4: 250, id5: 200}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    assert balances[id1] == TOTAL_AMOUNT - owers[id1]
    for ower, amount in owers.items():
        if ower not in payers:
            assert balances[ower] == -amount


def test_multiple_payers_that_do_not_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    payers = {id1: 600, id2: 400}
    owers = {id3: 200, id4: 300, id5: 50}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    for payer, amount in payers.items():
        assert balances[payer] == amount
    for ower, amount in owers.items():
        assert balances[ower] == -amount


def test_multiple_payers_that_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    payers = {id1: 600, id2: 400}
    owers = {id1: 100, id2: 200, id3: 300, id4: 200, id5: 200}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    for id, amount in payers.items():
        assert balances[id] == amount - owers[id]
    for id, amount in owers.items():
        if id not in payers:
            assert balances[id] == -amount
