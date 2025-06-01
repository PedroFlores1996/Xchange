from dataclasses import dataclass
from flask import flash
from flask_login import login_required, current_user
from app.model.expense import Expense, ExpenseCategory
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


@login_required
def get_allowed_expense(expense_id: int) -> Expense | None:
    """
    Fetches the allowed expense for the given expense ID and user ID.
    Returns None if the expense is not found or does not belong to the user.
    """
    expense = Expense.query.filter_by(id=expense_id).first_or_404()
    if (  # Check if the current user is allowed to access the expense
        current_user.id == expense.creator_id  # As creator of the expense
        or any(
            user.id == current_user.id for user in expense.users
        )  # Participant in the expense
        or any(
            expense.group_id == group.id for group in current_user.groups
        )  # Belongs to group of the expense
    ):
        return expense
