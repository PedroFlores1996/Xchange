import pytest
from wtforms import ValidationError, FormField, FieldList
from app.expense.forms import ExpenseForm, ExpenseUserForm
from app.split import SplitType
from app.model.expense import ExpenseCategory


def test_single_ower_not_payer(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 2, "amount": 50.0})

    form.validate_single_ower_not_payer()

    assert not form.payers.errors
    assert not form.owers.errors


def test_single_ower_is_also_payer_raises_validation_error(request_context):
    form = ExpenseForm()
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 1, "amount": 50.0})

    with pytest.raises(ValidationError):
        form.validate_single_ower_not_payer()
    assert form.payers.errors == ("Single user cannot be both a payer and an ower.",)
    assert form.owers.errors == ("Single user cannot be both a payer and an ower.",)
    assert form.errors["payers"][0] == "Single user cannot be both a payer and an ower."
    assert form.errors["payers"][0] == form.payers.errors[0]


def test_validate_sum_valid(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0

    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 0})
    form.owers.append_entry({"user_id": 4, "amount": 0})
    form.validate_sum(form.payers, SplitType.AMOUNT)
    form.validate_sum(form.payers, SplitType.PERCENTAGE)
    form.validate_sum(form.owers, SplitType.EQUALLY)

    assert not form.payers.errors
    assert not form.owers.errors


def test_validate_sum_invalid(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    with pytest.raises(ValidationError):
        form.validate_sum(form.payers, SplitType.EQUALLY)
    with pytest.raises(ValidationError):
        form.validate_sum(form.owers, SplitType.AMOUNT)
    with pytest.raises(ValidationError):
        form.validate_sum(form.owers, SplitType.PERCENTAGE)

    assert form.payers.errors == ("Payers total must be 0.",)
    assert form.owers.errors == (
        "Owers total must equal to the expense total.",
        "Owers percentages must sum to 100.",
    )


def test_validate_valid_form(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers_split.data = SplitType.AMOUNT
    form.owers_split.data = SplitType.PERCENTAGE
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


def test_validate_invalid_single_ower_is_payer(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers_split.data = SplitType.AMOUNT
    form.owers_split.data = SplitType.PERCENTAGE
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.owers.append_entry({"user_id": 1, "amount": 50.0})

    assert not form.validate()
    assert form.errors["payers"] == ["Single user cannot be both a payer and an ower."]
    assert form.errors["owers"] == ["Single user cannot be both a payer and an ower."]
    assert form.payers.errors == ["Single user cannot be both a payer and an ower."]
    assert form.owers.errors == ["Single user cannot be both a payer and an ower."]


def test_validate_invalid_sum_payers_first(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers_split.data = SplitType.AMOUNT
    form.owers_split.data = SplitType.AMOUNT
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    assert not form.validate()
    assert form.errors["payers"] == ["Payers total must equal to the expense total."]
    assert form.payers.errors == ["Payers total must equal to the expense total."]
    assert "owers" not in form.errors


def test_validate_invalid_sum_owers_after_payers(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers_split.data = SplitType.AMOUNT
    form.owers_split.data = SplitType.PERCENTAGE
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 50.0})
    form.owers.append_entry({"user_id": 3, "amount": 50.0})
    form.owers.append_entry({"user_id": 4, "amount": 40.0})

    assert not form.validate()
    assert form.errors["owers"] == ["Owers percentages must sum to 100."]
    assert form.owers.errors == ["Owers percentages must sum to 100."]
    assert "payers" not in form.errors
