from app.splits.equally import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    payers = {id1: TOTAL_AMOUNT}
    owers = {id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    assert balances[id1] == TOTAL_AMOUNT
    for ower in owers:
        assert balances[ower] == -TOTAL_AMOUNT / len(owers)


def test_single_payer_that_owes():
    payers = {id1: TOTAL_AMOUNT}
    owers = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    assert balances[id1] == TOTAL_AMOUNT - TOTAL_AMOUNT / len(owers)
    for ower in owers:
        if ower not in payers:
            assert balances[ower] == -TOTAL_AMOUNT / len(owers)


def test_multiple_payers_that_do_not_owe():
    payers = {id1: 0, id2: 0}
    owers = {id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    for payer in payers:
        assert balances[payer] == TOTAL_AMOUNT / len(payers)
    for ower in owers:
        assert balances[ower] == -TOTAL_AMOUNT / len(owers)


def test_multiple_payers_that_owe():
    payers = {id1: 0, id2: 0}
    owers = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    assert len(balances.items()) == 5
    for payer in payers:
        assert balances[payer] == TOTAL_AMOUNT / len(payers) - TOTAL_AMOUNT / len(owers)
    for ower in owers:
        if ower not in payers:
            assert balances[ower] == -TOTAL_AMOUNT / len(owers)
