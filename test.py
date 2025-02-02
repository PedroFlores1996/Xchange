from app import create_app
from app.config import TestConfig
from app.model.user import User
from app.model.group import Group, GroupDebt
from app.model.debt import Debt

def test():
    pedro = User.create_user("pedro", "1234")
    juan = User.create_user("juan", "1234")
    group1 = Group.create_group("group1")
    pedro.add_to_group(group1)
    juan.add_to_group(group1)
    debt1 = Debt.update_debt(pedro, juan, 100)
    debt2 = Debt.update_debt(juan, pedro, 50)
    debts = Debt.query.all()
    for debt in debts:
        print(f"Debtor: {debt.borrower.username}, Creditor: {debt.lender.username}, Amount: {debt.amount}")

if __name__ == '__main__':
    app = create_app(config=TestConfig)
    with app.app_context():
        test()