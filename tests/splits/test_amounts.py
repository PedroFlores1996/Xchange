from app.splits.amounts import single_payer, multiple_payers


def test_single_payer_that_does_not_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payer = id1
    owers = {id2: 20, id3: 30, id4: 25, id5: 25}
    balances = single_payer(total_amount, payer, owers)
    assert len(balances.items()) == 5
    assert balances[payer] == total_amount
    for ower, amount in owers.items():
        assert balances[ower] == -amount


def test_single_payer_that_owes():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payer = id1
    owers = {id1: 20, id2: 10, id3: 25, id4: 25, id5: 20}
    balances = single_payer(total_amount, payer, owers)
    assert len(balances.items()) == 5
    assert balances[payer] == total_amount - owers[payer]
    for ower, amount in owers.items():
        if ower != payer:
            assert balances[ower] == -amount


def test_add_expense_multiple_payers_that_do_not_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    payers = {id1: 60, id2: 40}
    owers = {id3: 20, id4: 30, id5: 50}
    balances = multiple_payers(payers, owers)
    assert len(balances.items()) == 5
    for payer, amount in payers.items():
        assert balances[payer] == amount
    for ower, amount in owers.items():
        assert balances[ower] == -amount


def test_add_expense_multiple_payers_that_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    payers = {id1: 60, id2: 40}
    owers = {id1: 10, id2: 20, id3: 30, id4: 20, id5: 20}
    balances = multiple_payers(payers, owers)
    assert len(balances.items()) == 5
    for id, amount in payers.items():
        assert balances[id] == amount - owers[id]
    for id, amount in owers.items():
        if id not in payers:
            assert balances[id] == -amount
