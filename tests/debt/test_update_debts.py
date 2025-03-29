from app.debt import update_debts
from app.model.user import User
from app.model.debt import Debt
from app.split.constants import TOTAL, OWED, PAYED


def test_update_debts(db_session):
    user1 = User.create("username1", "email1", "password")
    user2 = User.create("username2", "email2", "password")
    user3 = User.create("username3", "email3", "password")
    user4 = User.create("username4", "email4", "password")
    user5 = User.create("username5", "email5", "password")

    balances = {
        user1.id: {OWED: 0, PAYED: 10, TOTAL: 10},
        user2.id: {OWED: 10, PAYED: 0, TOTAL: -10},
        user3.id: {OWED: 0, PAYED: 20, TOTAL: 20},
        user4.id: {OWED: 30, PAYED: 0, TOTAL: -30},
        user5.id: {OWED: 0, PAYED: 10, TOTAL: 10},
    }

    update_debts(balances)

    # Check that the debts were updated correctly
    assert Debt.query.count() == 3
    assert (
        Debt.query.filter_by(borrower_id=user2.id, lender_id=user1.id).first().amount
        == 10
    )
    assert (
        Debt.query.filter_by(borrower_id=user4.id, lender_id=user3.id).first().amount
        == 20
    )
    assert (
        Debt.query.filter_by(borrower_id=user4.id, lender_id=user5.id).first().amount
        == 10
    )
