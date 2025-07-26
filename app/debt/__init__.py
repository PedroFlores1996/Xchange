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

        # Determine the amount to transfer with proper rounding
        transaction_amount = round(min(-debtor_amount, creditor_amount), 2)

        # Record the transaction
        transactions.append((debtor_id, creditor_id, transaction_amount))

        # Update the balances with proper rounding for monetary amounts
        net_balances[debtor_id] = round(net_balances[debtor_id] + transaction_amount, 2)
        net_balances[creditor_id] = round(
            net_balances[creditor_id] - transaction_amount, 2
        )

        # Remove users with settled balances (use epsilon comparison for floating point rounding errors)
        if abs(net_balances[debtor_id]) < 0.01:
            del net_balances[debtor_id]
        if abs(net_balances[creditor_id]) < 0.01:
            del net_balances[creditor_id]

    return transactions


def update_debts(
    balances: dict[int, dict[str, float]], group_id: int | None = None
) -> None:
    # Extract total balances and apply balanced rounding
    total_balances = {id: round(balance[TOTAL], 2) for id, balance in balances.items()}

    # Check for rounding errors and fix them
    total_sum = sum(total_balances.values())
    rounding_error = round(total_sum, 2)

    print(f"        📊 Pre-balanced totals: {total_balances}")
    print(f"        📊 Sum: {total_sum:.15f}, Rounding error: {rounding_error:.2f}")

    if abs(rounding_error) >= 0.005:  # More than half a cent error
        # Find someone with a non-zero balance to absorb the rounding error
        # Prefer someone who owes money (negative balance) to pay the extra cent(s)
        candidates = [
            (user_id, balance)
            for user_id, balance in total_balances.items()
            if abs(balance) >= 0.005
        ]

        if candidates:
            # Sort by balance (negative first, then by magnitude)
            candidates.sort(key=lambda x: (x[1] >= 0, abs(x[1])))
            chosen_user_id = candidates[0][0]

            print(
                f"        🎯 Assigning rounding error of {rounding_error:.2f} to user {chosen_user_id}"
            )
            print(
                f"        ⚖️  User {chosen_user_id}: {total_balances[chosen_user_id]:.2f} -> {total_balances[chosen_user_id] - rounding_error:.2f}"
            )

            total_balances[chosen_user_id] = round(
                total_balances[chosen_user_id] - rounding_error, 2
            )

        print(f"        🎉 Final balanced totals: {total_balances}")
        print(f"        🎉 Final sum: {sum(total_balances.values()):.15f}")
    else:
        print(f"        ✅ No significant rounding error detected")

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
