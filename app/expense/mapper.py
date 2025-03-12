from flask_login import current_user

from app.model.balance import Balance
from app.split.constants import OWED, PAYED, TOTAL
from app.expense import ExpenseData
from app.expense.forms import ExpenseForm


def map_form_to_expense_data(form: ExpenseForm) -> ExpenseData:
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


def map_balances_to_model(balances: dict[int, dict[str, float]]) -> list[Balance]:
    return [
        Balance.create(
            user_id=user_id,
            owed=balance[OWED],
            payed=balance[PAYED],
            total=balance[TOTAL],
        )
        for user_id, balance in balances.items()
    ]
