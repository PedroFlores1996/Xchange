from flask_login import current_user

from app.database import db
from app.model.expense import Expense
from app.model.debt import Debt
from app.expense.mapper import ExpenseData
from app.split import SplitType, amount, equally, percentage
from app.model.balance import Balance
from app.split.constants import OWED, PAYED, TOTAL


def split(
    total_amount: float, payers: list, owers: list, split_type: SplitType
) -> dict[int, dict[str, float]]:
    match split_type:
        case SplitType.EQUALLY:
            return equally.split(total_amount, payers, owers)
        case SplitType.AMOUNT:
            return amount.split(payers, owers)
        case SplitType.PERCENTAGE:
            return percentage.split(total_amount, payers, owers)
        case _:
            raise ValueError(f"Unknown split type: {split_type}")


def map_balances(balances: dict[int, dict[str, float]]) -> list[Balance]:
    return [
        Balance.create(
            user_id=user_id,
            owed=balance[OWED],
            payed=balance[PAYED],
            total=balance[TOTAL],
        )
        for user_id, balance in balances.items()
    ]


def create_expense(data: ExpenseData, balances: dict[int, dict[str, float]]) -> Expense:
    return Expense.create(
        amount=data.amount,
        description=data.description,
        creator_id=current_user.get_id(),
        category=data.category,
        split=data.split,
        balances=map_balances(balances),
    )


def minimum_transactions(
    balances: dict[int, dict[str, float]],
) -> list[tuple[int, int, float]]:
    debtors = {
        user_id: balance[TOTAL]
        for user_id, balance in balances.items()
        if balance[TOTAL] < 0
    }
    creditors = {
        user_id: balance[TOTAL]
        for user_id, balance in balances.items()
        if balance[TOTAL] > 0
    }

    sorted_debtors = sorted(debtors.items(), key=lambda x: x[1])
    sorted_creditors = sorted(creditors.items(), key=lambda x: x[1], reverse=True)

    transactions = []
    creditor_index = 0
    for debtor_id, debtor_amount in sorted_debtors:
        while debtor_amount < 0:
            creditor_id, creditor_amount = sorted_creditors[creditor_index]
            transaction_amount = min(-debtor_amount, creditor_amount)
            transactions.append((debtor_id, creditor_id, transaction_amount))

            debtor_amount += transaction_amount
            creditor_amount -= transaction_amount

            if creditor_amount == 0:
                creditor_index += 1

    return transactions


def update_debts(transactions: list[tuple[int, int, float]]):
    for debtor_id, creditor_id, amount in transactions:
        Debt.update(debtor_id, creditor_id, amount)


def create_expense_from(data: ExpenseData) -> Expense:
    balances = split(data.amount, data.payers, data.owers, data.split)
    transactions = minimum_transactions(balances)
    update_debts(transactions)
    expense = create_expense(data, balances)
    db.session.commit()
    return expense
