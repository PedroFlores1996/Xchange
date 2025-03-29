from app.debt import simplify_debts


def test_simplify_debts():
    balances = {
        2: -30,
        1: -70,
        3: 50,
        5: 20,
        4: 30,
    }

    expected_transactions = [
        (1, 3, 50),
        (2, 4, 30),
        (1, 5, 20),
    ]

    transactions = simplify_debts(balances)
    assert transactions == expected_transactions
