from app.split import split
from app.split import SplitType
from app.split.constants import OWED, PAYED, TOTAL
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5
from tests.splits.test_amounts import validate_amounts
from tests.splits.test_equally import equal_amounts_between
from tests.splits.test_percentage import amount_from


def test_split_payers_amounts_owers_amounts():
    payers = {id1: 500, id2: 500}
    owers = {id2: 200, id3: 300, id4: 250, id5: 250}

    balances = split(TOTAL_AMOUNT, payers, owers, SplitType.AMOUNT, SplitType.AMOUNT)

    validate_amounts(payers, owers, balances)


def test_split_payers_equally_owers_amounts():
    payers = {id1: 0, id2: 0}
    owers = {id2: 200, id3: 300, id4: 250, id5: 250}

    balances = split(TOTAL_AMOUNT, payers, owers, SplitType.EQUALLY, SplitType.AMOUNT)

    payers_amount = equal_amounts_between(payers)
    for user_id in payers:
        payed = payers_amount
        owed = owers.get(user_id, 0)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id in owers:
        payed = payers_amount if user_id in payers else 0
        owed = owers[user_id]
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_percentage_owers_amounts():
    payers = {id1: 15, id2: 20, id3: 30, id4: 15, id5: 20}
    owers = {id2: 200, id3: 300, id4: 250, id5: 250}

    balances = split(
        TOTAL_AMOUNT, payers, owers, SplitType.PERCENTAGE, SplitType.AMOUNT
    )

    for user_id, percentage in payers.items():
        payed = amount_from(percentage)
        owed = owers.get(user_id, 0)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id in owers:
        payed = amount_from(payers.get(user_id, 0))
        owed = owers[user_id]
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_amounts_owers_equally():
    payers = {id1: 500, id2: 500}
    owers = {id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers, SplitType.AMOUNT, SplitType.EQUALLY)

    equal_balance = equal_amounts_between(owers)
    for user_id in payers:
        payed = payers[user_id]
        owed = equal_balance if user_id in owers else 0
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id in owers:
        payed = payers.get(user_id, 0)
        owed = equal_balance
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_amounts_owers_percentage():
    payers = {id1: 500, id2: 500}
    owers = {id2: 15, id3: 35, id4: 35, id5: 15}

    balances = split(
        TOTAL_AMOUNT, payers, owers, SplitType.AMOUNT, SplitType.PERCENTAGE
    )

    for user_id in payers:
        payed = payers[user_id]
        owed = amount_from(owers.get(user_id, 0))
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id, percentage in owers.items():
        payed = payers.get(user_id, 0)
        owed = amount_from(percentage)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_equally_owers_equally():
    payers = {id1: 0, id2: 0}
    owers = {id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, payers, owers, SplitType.EQUALLY, SplitType.EQUALLY)

    payers_amount = equal_amounts_between(payers)
    owers_amount = equal_amounts_between(owers)
    for user_id in payers:
        payed = payers_amount
        owed = owers_amount if user_id in owers else 0
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id in owers:
        payed = payers_amount if user_id in payers else 0
        owed = owers_amount
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_equally_owers_percentage():
    payers = {id1: 0, id2: 0}
    owers = {id2: 15, id3: 35, id4: 35, id5: 15}

    balances = split(
        TOTAL_AMOUNT, payers, owers, SplitType.EQUALLY, SplitType.PERCENTAGE
    )

    payers_amount = equal_amounts_between(payers)
    for user_id in payers:
        payed = payers_amount
        owed = amount_from(owers.get(user_id, 0))
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id, percentage in owers.items():
        payed = payers_amount if user_id in payers else 0
        owed = amount_from(percentage)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_percentage_owers_equally():
    payers = {id1: 15, id2: 20, id3: 30, id4: 15, id5: 20}
    owers = {id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(
        TOTAL_AMOUNT, payers, owers, SplitType.PERCENTAGE, SplitType.EQUALLY
    )

    for user_id, percentage in payers.items():
        payed = amount_from(percentage)
        owed = equal_amounts_between(owers) if user_id in owers else 0
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id in owers:
        payed = amount_from(payers.get(user_id, 0))
        owed = equal_amounts_between(owers)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed


def test_split_payers_percentage_owers_percentage():
    payers = {id1: 15, id2: 20, id3: 30, id4: 15, id5: 20}
    owers = {id2: 15, id3: 35, id4: 35, id5: 15}

    balances = split(
        TOTAL_AMOUNT, payers, owers, SplitType.PERCENTAGE, SplitType.PERCENTAGE
    )

    for user_id, percentage in payers.items():
        payed = amount_from(percentage)
        owed = amount_from(owers.get(user_id, 0))
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
    for user_id, percentage in owers.items():
        payed = amount_from(payers.get(user_id, 0))
        owed = amount_from(percentage)
        assert balances[user_id][PAYED] == payed
        assert balances[user_id][OWED] == owed
        assert balances[user_id][TOTAL] == payed - owed
