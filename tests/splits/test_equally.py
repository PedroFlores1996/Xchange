from app.splits.equally import single_payer, multiple_payers


def test_add_expense_equally_one_payer_that_does_not_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payer = id1
    owers = [id2, id3, id4, id5]
    balances = single_payer(total_amount, payer, owers)

    assert len(balances.items()) == 5
    assert balances[payer] == total_amount
    for ower in owers:
        assert balances[ower] == -total_amount / len(owers)


def test_add_expense_equally_one_payer_that_owes():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payer = id1
    owers = [id1, id2, id3, id4, id5]
    balances = single_payer(total_amount, payer, owers)

    assert len(balances.items()) == 5
    assert balances[payer] == total_amount - total_amount / len(owers)
    for ower in owers[1:]:
        assert balances[ower] == -total_amount / len(owers)


def test_add_expense_multiple_payers_that_do_not_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payers = [id1, id2]
    owers = [id3, id4, id5]
    balances = multiple_payers(total_amount, payers, owers)

    assert len(balances.items()) == 5
    for payer in payers:
        assert balances[payer] == total_amount / len(payers)
    for ower in owers:
        assert balances[ower] == -total_amount / len(owers)


def test_add_expense_multiple_payers_that_owe():
    id1, id2, id3, id4, id5 = 1, 2, 3, 4, 5
    total_amount = 100
    payers = [id1, id2]
    owers = [id1, id2, id3, id4, id5]
    balances = multiple_payers(total_amount, payers, owers)

    assert len(balances.items()) == 5
    for payer in payers:
        assert balances[payer] == total_amount / len(payers) - total_amount / len(owers)
    for ower in owers[2:]:
        assert balances[ower] == -total_amount / len(owers)
