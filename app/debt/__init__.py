from app.model import Debt
from app.split.constants import TOTAL


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


def update_debts(balances: dict[int, dict[str, float]]):
    transactions = minimum_transactions(balances)
    for debtor_id, creditor_id, amount in transactions:
        Debt.update(debtor_id, creditor_id, amount)


def get_debts_balance(lender_debts: list[Debt], borrower_debts: list[Debt]) -> float:
    return sum(debt.amount for debt in lender_debts) - sum(
        debt.amount for debt in borrower_debts
    )
