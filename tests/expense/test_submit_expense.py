from app.expense import ExpenseData
from app.expense.submit import submit_expense
from app.split import SplitType
from app.model.user import User
from app.model.expense import ExpenseCategory


def test_submit_expense(db_session, logged_in_user):
    # Arrange
    ## Create 3 users
    user1 = User.create(username="user1", email="1@email.com", password="password1")
    user2 = User.create(username="user2", email="2@email.com", password="password2")
    user3 = User.create(username="user3", email="3@email.com", password="password3")

    ## Create mock expense data
    expense_data = ExpenseData(
        amount=100.0,
        description="Test Expense",
        category=ExpenseCategory.FOOD,
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        payers={user1.id: 50.0, user2.id: 50.0},
        owers={user3.id: 100.0},
        group_id=None,
        creator_id=logged_in_user.id,
    )

    # Act
    expense = submit_expense(expense_data)

    # Assert
    assert expense.amount == 100.0
    assert expense.description == "Test Expense"
    assert expense.category == ExpenseCategory.FOOD
    assert expense.creator_id == logged_in_user.id
    assert expense.payers_split == SplitType.EQUALLY
    assert expense.owers_split == SplitType.EQUALLY
    assert expense.group_id == "no-group"
    assert expense.creator_id == logged_in_user.id
