from app.split.equally import split
from app.split.constants import OWED, PAYED, TOTAL
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    payers = {id1: TOTAL_AMOUNT}
    owers = {id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_single_payer_that_owes():
    payers = {id1: TOTAL_AMOUNT}
    owers = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_multiple_payers_that_do_not_owe():
    payers = {id1: 0, id2: 0}
    owers = {id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def test_multiple_payers_that_owe():
    payers = {id1: 0, id2: 0}
    owers = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers)

    validate_balances(payers, owers, balances)


def validate_balances(payers, owers, balances):
    assert len(balances.items()) == 5
    for payer in payers:
        owed = TOTAL_AMOUNT / len(owers) if payer in owers else 0
        payed = TOTAL_AMOUNT / len(payers)
        assert balances[payer][OWED] == owed
        assert balances[payer][PAYED] == payed
        assert balances[payer][TOTAL] == payed - owed
    for ower in owers:
        owed = TOTAL_AMOUNT / len(owers)
        payed = TOTAL_AMOUNT / len(payers) if ower in payers else 0
        assert balances[ower][OWED] == owed
        assert balances[ower][PAYED] == payed
        assert balances[ower][TOTAL] == payed - owed
