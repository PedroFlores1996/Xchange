from app.model import Debt
from app.model.group_balance import GroupBalance
from app.split.constants import TOTAL


def simplify_debts(balances: dict[int, float]) -> list[tuple[int, int, float]]:
    """
    Simplifies debts in a group to minimize the number of transactions.

    :param balances: A dictionary where the key is the user ID and the value is the net balance.
                     Positive values indicate the user is owed money, and negative values indicate the user owes money.
    :return: A list of transactions in the form (debtor_id, creditor_id, amount).
    """
    # Filter out users with a net balance of 0
    net_balances = {
        user_id: balance for user_id, balance in balances.items() if balance != 0
    }

    # List to store the transactions
    transactions = []

    # While there are unsettled balances
    while net_balances:
        # Find the person who owes the most (most negative balance)
        debtor_id = min(net_balances, key=net_balances.get)
        debtor_amount = net_balances[debtor_id]

        # Find the person who is owed the most (most positive balance)
        creditor_id = max(net_balances, key=net_balances.get)
        creditor_amount = net_balances[creditor_id]

        # Determine the amount to transfer
        transaction_amount = min(-debtor_amount, creditor_amount)

        # Record the transaction
        transactions.append((debtor_id, creditor_id, transaction_amount))

        # Update the balances
        net_balances[debtor_id] += transaction_amount
        net_balances[creditor_id] -= transaction_amount

        # Remove users with a settled balance (balance == 0)
        if net_balances[debtor_id] == 0:
            del net_balances[debtor_id]
        if net_balances[creditor_id] == 0:
            del net_balances[creditor_id]

    return transactions


def update_debts(
    balances: dict[int, dict[str, float]], group_id: int | None = None
) -> None:
    total_balances = {id: balance[TOTAL] for id, balance in balances.items()}
    
    if group_id is not None:
        # For group expenses, update GroupBalance records instead of creating individual debts
        for user_id, balance in total_balances.items():
            if balance != 0:  # Only update if there's a non-zero balance
                GroupBalance.update_balance(user_id, group_id, balance)
    else:
        # For individual expenses (non-group), create individual debts as before
        transactions = simplify_debts(total_balances)
        for debtor_id, creditor_id, amount in transactions:
            Debt.update(debtor_id, creditor_id, amount)


def get_debts_total_balance(
    lender_debts: list[Debt], borrower_debts: list[Debt]
) -> float:
    return sum(debt.amount for debt in lender_debts) - sum(
        debt.amount for debt in borrower_debts
    )
