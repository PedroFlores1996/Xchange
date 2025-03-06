from app.model.balance import Balance
from app.model.user import User
from app.model.expense import Expense


def test_create_balance_positive(db_session):
    user = User.create("username", "password")
    balance = Balance(
        user_id=user.id,
        owed=10.0,
        payed=20.0,
        total=10.0,
    )
    expense = Expense(creator_id=user.id, amount=10.0, balances=[balance])
    db_session.add(expense)
    db_session.flush()

    assert Balance.query.count() == 1
    assert Balance.query.first() == balance
    assert balance.user == user
    assert balance.expense == expense
    assert balance.owed == 10.0
    assert balance.payed == 20.0
    assert balance.total == 10.0
    assert balance.user_id == user.id
    assert balance.expense_id == expense.id
    assert balance in expense.balances
