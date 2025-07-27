from flask_login import current_user

from app.model.balance import Balance
from app.split.constants import OWED, PAYED, TOTAL
from app.expense import ExpenseData
from app.expense.forms import ExpenseForm


def map_form_to_expense_data(form: ExpenseForm) -> ExpenseData:
    return ExpenseData(
        amount=form.amount.data,
        description=form.description.data,
        category=form.category.data,
        payers_split=form.payers_split.data,
        owers_split=form.owers_split.data,
        payers={p.user_id.data: p.amount.data for p in form.payers},
        owers={o.user_id.data: o.amount.data for o in form.owers},
        group_id=form.group_id.data,
        creator_id=int(current_user.get_id()),
    )


def map_balances_to_model(balances: dict[int, dict[str, float]]) -> list[Balance]:
    return [
        Balance.create(user_id=uid, owed=bal[OWED], payed=bal[PAYED], total=bal[TOTAL])
        for uid, bal in balances.items()
    ]
