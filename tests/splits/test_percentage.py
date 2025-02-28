from app.splits.percentage import single_payer, multiple_payers


TOTAL_AMOUNT: float = 1000.0
id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5


def amount_from(float_percentage: float) -> float:
    return TOTAL_AMOUNT * float_percentage / 100


def test_single_payer_that_does_not_owe():
    payer_id = id1
    owed_percentages = {id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = single_payer(TOTAL_AMOUNT, payer_id, owed_percentages)

    assert len(balances) == 5
    assert balances[payer_id] == TOTAL_AMOUNT
    for ower_id, percentage in owed_percentages.items():
        assert balances[ower_id] == -amount_from(percentage)
    print(balances)


def test_single_payer_that_owes():
    payer_id = id1
    owed_percentages = {id1: 15, id2: 20.0, id3: 15.0, id4: 25.0, id5: 25.0}
    balances = single_payer(TOTAL_AMOUNT, payer_id, owed_percentages)

    assert len(balances) == 5
    assert balances[payer_id] == TOTAL_AMOUNT - amount_from(owed_percentages[payer_id])
    for ower_id, percentage in owed_percentages.items():
        if ower_id is not payer_id:
            assert balances[ower_id] == -amount_from(percentage)
    print(balances)


def test_multiple_payers_that_do_not_owe():
    payed_percentages = {id1: 55.0, id2: 45.0}
    owed_amounts = {id3: 50.0, id4: 25.0, id5: 25.0}
    balances = multiple_payers(TOTAL_AMOUNT, payed_percentages, owed_amounts)

    assert len(balances) == 5
    for id, percentage in payed_percentages.items():
        assert balances[id] == amount_from(percentage)
    for id, percentage in owed_amounts.items():
        assert balances[id] == -amount_from(percentage)
    print(balances)


def test_multiple_payers_that_owe():
    payed_percentages = {id1: 55.0, id2: 45.0}
    owed_amounts = {id1: 10, id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = multiple_payers(TOTAL_AMOUNT, payed_percentages, owed_amounts)

    assert len(balances) == 5
    for id, percentage in payed_percentages.items():
        assert balances[id] == amount_from(percentage) - amount_from(owed_amounts[id])
    for id, percentage in owed_amounts.items():
        if id not in payed_percentages:
            assert balances[id] == -amount_from(percentage)
    print(balances)


def test_multiple_payers_all_owe():
    payed_percentages = {id1: 15.0, id2: 5.0, id3: 50.0, id4: 20.0, id5: 10.0}
    owed_amounts = {id1: 10, id2: 20.0, id3: 30.0, id4: 25.0, id5: 25.0}
    balances = multiple_payers(TOTAL_AMOUNT, payed_percentages, owed_amounts)

    assert len(balances) == 5
    for id, percentage in payed_percentages.items():
        assert balances[id] == amount_from(percentage) - amount_from(owed_amounts[id])
    print(balances)
