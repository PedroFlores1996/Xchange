from dataclasses import dataclass
from flask import flash
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


def handle_expense_creation(form_data: dict) -> dict:
    """
    Handles the business logic for creating a new expense.
    Returns a dictionary with the result status and data.
    """
    from app.expense.mapper import map_form_to_expense_data
    from app.expense.submit import submit_expense

    data: ExpenseData = map_form_to_expense_data(form_data)
    expense: Expense = submit_expense(data)
    return prepare_expense_summary_data(expense)


def validate_expense_access(expense_id: int, user) -> dict:
    """
    Validates if the user has access to the specified expense.
    Returns a dictionary with validation result and expense data.
    """
    try:
        expense = Expense.query.filter_by(id=expense_id).first()

        if not expense:
            return {
                "valid": False,
                "message": "Expense not found.",
                "message_type": "danger",
                "redirect_to": "user.expenses",
            }

        # Check if the current user is allowed to access the expense
        if (
            user.id == expense.creator_id  # As creator of the expense
            or any(u.id == user.id for u in expense.users)  # Participant in the expense
            or any(expense.group_id == group.id for group in user.groups)
        ):  # Belongs to group of the expense

            return {"valid": True, "expense": expense}
        else:
            return {
                "valid": False,
                "message": "You do not have access to this expense.",
                "message_type": "danger",
                "redirect_to": "user.expenses",
            }

    except Exception:
        return {
            "valid": False,
            "message": "Error accessing expense.",
            "message_type": "danger",
            "redirect_to": "user.expenses",
        }


def prepare_expense_form_data(user) -> dict:
    """
    Prepares all data needed for the expense creation form.
    Returns a dictionary with organized data for the template.
    """
    from app.expense.forms import ExpenseForm

    form = ExpenseForm()

    return {
        "form": form,
        "current_user": user,
        "categories": ExpenseCategory.choices(),
        "split_types": SplitType.choices(),
    }


def prepare_expense_summary_data(expense: Expense) -> dict:
    """
    Prepares all data needed for the expense summary template.
    Returns a dictionary with organized expense data.
    """
    return {
        "expense": expense,
        "balances": expense.balances,
        "participants": expense.users,
        "group": expense.group if expense.group_id else None,
        "creator": expense.creator,
        "total_amount": expense.amount,
        "created_at": expense.created_at,
    }


def prepare_all_debts_data() -> dict:
    """
    Prepares all debts data for the debts overview page.
    Returns a dictionary with organized debts data.
    """
    try:
        all_debts = Debt.query.all()

        # Organize debts by status or other criteria if needed
        active_debts = [debt for debt in all_debts if debt.amount > 0]

        return {
            "success": True,
            "debts": all_debts,
            "active_debts": active_debts,
            "total_debts": len(all_debts),
            "total_amount": sum(debt.amount for debt in active_debts),
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


def handle_expense_form_validation(form) -> dict:
    """
    Handles expense form validation and returns structured result.
    Returns a dictionary with validation status and messages.
    """
    if form.validate_on_submit():
        return {"valid": True, "form": form}
    else:
        errors = []
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field_name}: {error}")

        return {
            "valid": False,
            "errors": errors,
            "message": "Please correct the form errors.",
            "message_type": "warning",
        }


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
