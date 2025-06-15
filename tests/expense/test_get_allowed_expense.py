import pytest
from werkzeug.exceptions import NotFound
from app.expense import get_allowed_expense
from app.model.balance import Balance
from app.model.expense import Expense


def test_get_allowed_expense_current_user_is_creator(logged_in_user):
    expense = Expense.create(
        amount=100.0,
        balances=[],
        creator_id=logged_in_user.id,
    )

    allowed_expense = get_allowed_expense(expense.id)
    assert allowed_expense is not None
    assert allowed_expense.id == expense.id
    assert allowed_expense.creator_id == expense.creator_id


def test_get_allowed_expense_current_user_participates(db_session, logged_in_user):
    expense = Expense.create(
        amount=100.0,
        balances=[],
        creator_id=logged_in_user.id + 1,  # Creator is different user
    )
    logged_in_user.add_expense(expense)

    allowed_expense = get_allowed_expense(expense.id)
    assert allowed_expense is not None
    assert allowed_expense.id == expense.id
    assert allowed_expense.creator_id == expense.creator_id


def test_get_allowed_expense_non_existent(db_session, logged_in_user):
    MOCK_ID = 9999
    assert db_session.query(Expense).filter_by(id=MOCK_ID).first() is None
    # Assert that abort(404) is raised for non-existent expense
    with pytest.raises(NotFound):
        get_allowed_expense(MOCK_ID)


def test_get_allowed_expense_not_allowed(db_session, logged_in_user):
    expense = Expense.create(
        amount=100.0,
        balances=[],
        creator_id=logged_in_user.id + 1,  # Logged in user is not the creator
    )

    # Assert that None is returned for an expense not allowed for the user
    allowed_expense = get_allowed_expense(expense.id)
    assert allowed_expense is None
