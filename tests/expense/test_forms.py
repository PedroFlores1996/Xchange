import pytest
from wtforms import ValidationError
from app.expense.forms import ExpenseForm
from app.splits.types import SplitType
from app.model.expense import ExpenseCategory


def test_single_ower_not_payer(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 2, "amount": 50.0})

    form.single_ower_not_payer()


def test_single_ower_is_also_payer_raises_validation_error(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 1, "amount": 50.0})

    with pytest.raises(ValidationError):
        form.single_ower_not_payer()
    assert form.payers.errors[0] == "Single user cannot be both a payer and an ower."
    assert form.owers.errors[0] == "Single user cannot be both a payer and an ower."


def test_validate_amounts_payers_and_owers_sum_equals_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    form.validate_amounts_sum()
    form.validate_amounts_sum()


def test_validate_payers_amounts_first_sum_does_not_equal_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_amounts_sum()
    assert form.errors["payers"][0] == "Payers total must equal to the expense total."
    assert form.errors.get("owers") is None


def test_validate_owers_amounts_after_payers_sum_does_not_equal_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_amounts_sum()
    assert form.errors["owers"][0] == "Owers total must equal to the expense total."
    assert form.errors.get("payers") is None


def test_valisate_percentages_sum(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    form.validate_percentages_sum()
    form.validate_percentages_sum()


def test_validate_payers_percentages_do_not_equal_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_percentages_sum()
    assert form.errors["payers"][0] == "Payers percentages must sum to 100."
    assert form.errors.get("owers") is None


def test_validate_owers_percentages_do_not_equal_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_percentages_sum()
    assert form.errors["owers"][0] == "Owers percentages must sum to 100."
    assert form.errors.get("payers") is None


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
    assert form.errors == {}


def test_validate_invalid_built_in_validate(request_context):
    form = ExpenseForm()

    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    assert not form.validate()
    assert form.errors["amount"][0] == "This field is required."


def test_validate_single_ower_is_payer(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 1, "amount": 50.0})

    form.validate()
    assert form.errors["payers"][0] == "Single user cannot be both a payer and an ower."
    assert form.errors["owers"][0] == "Single user cannot be both a payer and an ower."


def test_validate_amounts_sum_does_not_equal_total(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 50.0})

    form.validate()
    assert form.errors["payers"][0] == "Payers total must equal to the expense total."


def test_validate_percentages_sum_does_not_equal_100(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.split.data = SplitType.PERCENTAGE
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 50, "amount": 50.0})

    form.validate()
    assert form.errors["payers"][0] == "Payers percentages must sum to 100."
