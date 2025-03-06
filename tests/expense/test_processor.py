from app.expense.processor import minimum_transactions
from app.model.user import User


def test_update_debts(db_session):
    user1 = User.create("username1", "password")
    user2 = User.create("username2", "password")
    user3 = User.create("username3", "password")
    user4 = User.create("username4", "password")
    user5 = User.create("username5", "password")

    balances = {
        user1.id: {"owed": 0, "payed": 10, "total": 10},
        user2.id: {"owed": 10, "payed": 0, "total": -10},
        user3.id: {"owed": 0, "payed": 20, "total": 20},
        user4.id: {"owed": 30, "payed": 0, "total": -30},
        user5.id: {"owed": 0, "payed": 10, "total": 10},
    }

    transactions = minimum_transactions(balances)
    print(transactions)
