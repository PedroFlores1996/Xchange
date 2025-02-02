from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt

def test_debts(db_session):
    pedro = User.create_user("pedro", "1234")
    juan = User.create_user("juan", "1234")
    group1 = Group.create_group("group1")
    group2 = Group.create_group("group2")
    pedro.add_to_group(group1)
    pedro.add_to_group(group2)
    juan.add_to_group(group1)
    debt1 = Debt.update_debt(pedro, juan, 100)
    debt2 = Debt.update_debt(juan, pedro, 150)
    debt3 = Debt.update_debt(pedro, juan, 25, group=group1)

    debts = Debt.query.all()
    for debt in debts:
        print(f"Debtor: {debt.borrower.username}, Creditor: {debt.lender.username}, Amount: {debt.amount}, Group: {debt.group.name if debt.group else 'No group'}")

    pedro_groups = pedro.groups
    for group in pedro_groups:
        print(f"Pedro is in group: {group.name}")

    group1_members = group1.users
    for member in group1_members:
        print(f"Member of group1: {member.username}")

    pedro_lender_debts = pedro.lender_debts
    for debt in pedro_lender_debts:
        print(f"Pedro is lender in debt with {debt.borrower.username} for {debt.amount} in group {debt.group.name if debt.group else 'No group'}")

    pedro_borrower_debts = pedro.borrower_debts
    for debt in pedro_borrower_debts:
        print(f"Pedro is borrower in debt with {debt.lender.username} for {debt.amount} in group {debt.group.name if debt.group else 'No group'}")

    assert len(debts) == 2
