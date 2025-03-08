import pytest
from wtforms import ValidationError
from app.expense.forms import ExpenseForm
from app.splits import SplitType
from app.model.expense import ExpenseCategory


def test_single_ower_not_payer(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 2, "amount": 50.0})

    form.single_ower_not_payer(form.owers)

    assert not form.errors
    assert not form.payers.errors
    assert not form.owers.errors


def test_single_ower_is_also_payer_raises_validation_error(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 1, "amount": 50.0})

    with pytest.raises(ValidationError):
        form.single_ower_not_payer(form.owers)


def test_validate_amounts_payers_and_owers_sum_equals_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    form.validate_sum(form.payers)
    form.validate_sum(form.owers)


def test_validate_payers_nor_owers_sum_equals_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_sum(form.payers)
    with pytest.raises(ValidationError):
        form.validate_sum(form.owers)

    assert form.errors["payers"][0] == "Payers total must equal to the expense total."
    assert form.errors["owers"][0] == "Owers total must equal to the expense total."


def test_validate_percentages_payers_and_owers_sum_equals_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    form.validate_sum(form.payers)
    form.validate_sum(form.owers)


def test_validate_payers_nor_owers_percentages_equals_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_sum(form.payers)
    with pytest.raises(ValidationError):
        form.validate_sum(form.owers)

    assert form.errors["payers"][0] == "Payers percentages must sum to 100."
    assert form.errors["owers"][0] == "Owers percentages must sum to 100."


def test_validate_single_ower_is_payer(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 100.0})
    form.owers.append_entry({"user_id": 1, "amount": 100.0})

    form.validate()
    assert form.owers.errors[0] == "Single user cannot be both a payer and an ower."
    assert form.errors["owers"][0] == form.owers.errors[0]


def test_validate_amounts_sum_does_not_equal_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    form.validate()
    assert form.errors["payers"][0] == "Payers total must equal to the expense total."
    assert form.errors["owers"][0] == "Owers total must equal to the expense total."
    assert form.errors["payers"][0] == form.payers.errors[0]
    assert form.errors["owers"][0] == form.owers.errors[0]


def test_validate_percentages_sum_does_not_equal_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 50, "amount": 40.0})

    form.validate()
    assert form.errors["payers"][0] == "Payers percentages must sum to 100."
    assert form.errors["owers"][0] == "Owers percentages must sum to 100."
    assert form.errors["payers"][0] == form.payers.errors[0]
    assert form.errors["owers"][0] == form.owers.errors[0]


def test_validate_valid_form(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    assert form.validate()
    assert not form.errors
    assert not form.payers.errors
    assert not form.owers.errors
