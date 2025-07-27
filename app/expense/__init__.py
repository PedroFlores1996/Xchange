from dataclasses import dataclass
from flask_login import login_required, current_user
from app.model.expense import Expense, ExpenseCategory
from app.model.debt import Debt
from app.split import SplitType


@dataclass
class ExpenseData:
    amount: float
    description: str
    category: ExpenseCategory
    payers_split: SplitType
    owers_split: SplitType
    payers: dict[int, float | None]
    owers: dict[int, float | None]
    group_id: int | None
    creator_id: int



def get_authorized_expense(expense_id: int, user) -> Expense | None:
    """Returns expense if user has access, None otherwise."""
    try:
        expense = Expense.query.filter_by(id=expense_id).first()
        if not expense:
            return None
        
        has_access = (
            user.id == expense.creator_id
            or any(u.id == user.id for u in expense.users)
            or any(expense.group_id == group.id for group in user.groups)
        )
        
        return expense if has_access else None
    except Exception:
        return None




def prepare_all_debts_data() -> dict:
    """Prepares debts overview data."""
    try:
        all_debts = Debt.query.all()
        active_debts = [d for d in all_debts if d.amount > 0]
        return {
            "success": True,
            "debts": all_debts,
            "active_debts": active_debts,
            "total_debts": len(all_debts),
            "total_amount": sum(d.amount for d in active_debts),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error loading debts: {str(e)}",
            "debts": [],
            "active_debts": [],
            "total_debts": 0,
            "total_amount": 0,
        }



@login_required
def get_allowed_expense(expense_id: int) -> Expense | None:
    """Fetches expense if user has access."""
    expense = Expense.query.filter_by(id=expense_id).first_or_404()
    has_access = (
        current_user.id == expense.creator_id
        or any(u.id == current_user.id for u in expense.users)
        or any(expense.group_id == g.id for g in current_user.groups)
    )
    return expense if has_access else None
