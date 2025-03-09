from flask_login import current_user
from dataclasses import dataclass
from app.expense.forms import ExpenseForm
from app.model.expense import ExpenseCategory
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


def expense_data_from(form: ExpenseForm) -> ExpenseData:
    return ExpenseData(
        amount=form.amount.data,  # type: ignore
        description=form.description.data,  # type: ignore
        category=form.category.data,
        payers_split=form.payers_split.data,
        owers_split=form.owers_split.data,
        payers={payer.user_id.data: payer.amount.data for payer in form.payers},
        owers={ower.user_id.data: ower.amount.data for ower in form.owers},
        group_id=form.group_id.data,
        creator_id=int(current_user.get_id()),
    )
