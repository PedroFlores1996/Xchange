from app.expense.mapper import map_form_to_expense_data, map_balances_to_model
from app.model.expense import ExpenseCategory
from app.split.constants import OWED, PAYED, TOTAL
from app.model.balance import Balance
from app.expense.forms import ExpenseForm, ExpenseUserForm
from app.split import SplitType


def test_map_form_to_expense_data(request_context, logged_in_user):
    # Add payers and owers using ExpenseUserForm
    payer_form = ExpenseUserForm(user_id=1, amount=50.0)
    ower_form = ExpenseUserForm(user_id=2, amount=50.0)

    # Build the form with actual fields
    form = ExpenseForm(
        amount=50.0,
        description="Lunch",
        category=ExpenseCategory.FOOD,
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        group_id=10,
        payers=[payer_form.data],
        owers=[ower_form.data],
    )

    data = map_form_to_expense_data(form)
    assert data.amount == 50.0
    assert data.description == "Lunch"
    assert data.category == ExpenseCategory.FOOD
    assert data.payers_split == SplitType.EQUALLY
    assert data.owers_split == SplitType.EQUALLY
    assert data.payers == {1: 50.0}
    assert data.owers == {2: 50.0}
    assert data.group_id == 10
    assert data.creator_id == logged_in_user.id


def test_map_balances_to_model():
    balances = {
        1: {OWED: 10.0, PAYED: 5.0, TOTAL: 5.0},
        2: {OWED: 0.0, PAYED: 20.0, TOTAL: -20.0},
    }
    result = map_balances_to_model(balances)
    assert isinstance(result, list)
    assert all(isinstance(b, Balance) for b in result)
    assert result[0].user_id == 1
    assert result[0].owed == 10.0
    assert result[0].payed == 5.0
    assert result[0].total == 5.0
    assert result[1].user_id == 2
    assert result[1].owed == 0.0
    assert result[1].payed == 20.0
    assert result[1].total == -20.0
