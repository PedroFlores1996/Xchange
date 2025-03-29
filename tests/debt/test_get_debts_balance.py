import pytest
from app.debt import get_debts_total_balance
from app.model.debt import Debt
from app.model.user import User


@pytest.fixture(scope="function")
def test_user(db_session):
    # Create users
    user = User.create("user", "user@example.com", "password")
    friend1 = User.create("friend1", "friend1@example.com", "password")
    friend2 = User.create("friend2", "friend2@example.com", "password")
    friend3 = User.create("friend3", "friend3@example.com", "password")
    friend4 = User.create("friend4", "friend4@example.com", "password")

    # Update lender debts
    Debt.update(lender_id=user.id, borrower_id=friend1.id, amount=100)
    Debt.update(lender_id=user.id, borrower_id=friend2.id, amount=50)
    Debt.update(lender_id=user.id, borrower_id=friend3.id, amount=50)

    # Update borrower debts
    Debt.update(lender_id=friend1.id, borrower_id=user.id, amount=30)
    Debt.update(lender_id=friend2.id, borrower_id=user.id, amount=50)
    Debt.update(lender_id=friend4.id, borrower_id=user.id, amount=20)

    return user


def test_get_debts_balance(test_user):

    # Expected balance: (100 + 50 + 50) - (30 + 20) = 150 - 50 = 100
    expected_balance = 100

    # Calculate the balance
    balance = get_debts_total_balance(test_user.lender_debts, test_user.borrower_debts)

    # Assert the balance is as expected
    assert balance == expected_balance


def test_get_debts_balance_no_lender_debts(test_user):

    expected_balance = -20

    balance = get_debts_total_balance([], test_user.borrower_debts)

    # Assert the balance is as expected
    assert balance == expected_balance


def test_get_debts_balance_no_borrower_debts(test_user):

    expected_balance = 120

    # Calculate the balance
    balance = get_debts_total_balance(test_user.lender_debts, [])

    # Assert the balance is as expected
    assert balance == expected_balance


def test_get_debts_balance_no_debts():
    # No lender debts
    lender_debts = []

    # No borrower debts
    borrower_debts = []

    # Expected balance: 0 - 0 = 0
    expected_balance = 0

    # Calculate the balance
    balance = get_debts_total_balance(lender_debts, borrower_debts)

    # Assert the balance is as expected
    assert balance == expected_balance
