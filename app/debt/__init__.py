from app.model.debt import Debt
from app.model.group_balance import GroupBalance
from app.split.constants import TOTAL


def simplify_debts(balances: dict[int, float]) -> list[tuple[int, int, float]]:
    """Simplifies debts to minimize transactions."""
    cents = {uid: round(bal * 100) for uid, bal in balances.items() if bal != 0}
    transactions = []
    
    while cents:
        debtor = min(cents, key=cents.get)
        creditor = max(cents, key=cents.get)
        amount_cents = min(-cents[debtor], cents[creditor])
        
        transactions.append((debtor, creditor, amount_cents / 100))
        
        cents[debtor] += amount_cents
        cents[creditor] -= amount_cents
        
        if cents[debtor] == 0:
            del cents[debtor]
        if creditor in cents and cents[creditor] == 0:
            del cents[creditor]
    
    return transactions


def update_debts(balances: dict[int, dict[str, float]], group_id: int | None = None) -> None:
    totals = {uid: bal[TOTAL] for uid, bal in balances.items()}
    
    if group_id:
        for uid, bal in totals.items():
            if bal != 0:
                GroupBalance.update_balance(uid, group_id, bal)
    else:
        for debtor, creditor, amount in simplify_debts(totals):
            Debt.update(debtor, creditor, amount)


def get_debts_total_balance(lender_debts: list[Debt], borrower_debts: list[Debt]) -> float:
    return sum(d.amount for d in lender_debts) - sum(d.amount for d in borrower_debts)
