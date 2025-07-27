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
    # Convert to integer arithmetic (*100) to eliminate floating point precision issues
    print(f"DEBUG: Input balances: {balances}")
    net_balances_cents = {
        user_id: round(balance * 100) for user_id, balance in balances.items() if balance != 0
    }
    print(f"DEBUG: Balances in cents: {net_balances_cents}")
    print(f"DEBUG: Sum of balances in cents: {sum(net_balances_cents.values())}")

    # List to store the transactions
    transactions = []
    max_iterations = 100  # Prevent infinite loops and stdout overflow

    # While there are unsettled balances
    while net_balances_cents:
        if max_iterations <= 0:
            raise RuntimeError("Max iterations reached while simplifying debts.")
        max_iterations -= 1
        # Convert back to dollars for display
        net_balances_display = {user_id: cents / 100 for user_id, cents in net_balances_cents.items()}
        print(f"Current net balances: {net_balances_display}")
        print(f"DEBUG: Current balances in cents: {net_balances_cents}")
        print(f"DEBUG: Sum of current balances in cents: {sum(net_balances_cents.values())}")

        # Find the person who owes the most (most negative balance)
        debtor_id = min(net_balances_cents, key=net_balances_cents.get)
        debtor_amount_cents = net_balances_cents[debtor_id]

        # Find the person who is owed the most (most positive balance)
        creditor_id = max(net_balances_cents, key=net_balances_cents.get)
        creditor_amount_cents = net_balances_cents[creditor_id]

        # Determine the amount to transfer (in cents)
        transaction_amount_cents = min(-debtor_amount_cents, creditor_amount_cents)
        transaction_amount = transaction_amount_cents / 100

        # Record the transaction (in dollars)
        transactions.append((debtor_id, creditor_id, transaction_amount))

        # Update the balances (in cents for exact arithmetic)
        net_balances_cents[debtor_id] = (
            net_balances_cents[debtor_id] + transaction_amount_cents
        )
        net_balances_cents[creditor_id] = (
            net_balances_cents[creditor_id] - transaction_amount_cents
        )

        # Remove users with settled balances (should be exactly 0)
        if net_balances_cents[debtor_id] == 0:
            del net_balances_cents[debtor_id]
        if creditor_id in net_balances_cents and net_balances_cents[creditor_id] == 0:
            del net_balances_cents[creditor_id]

    return transactions


def update_debts(
    balances: dict[int, dict[str, float]], group_id: int | None = None
) -> None:
    # Extract total balances (should already be properly balanced from split functions)
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
