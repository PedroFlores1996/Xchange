import pytest
from wtforms import ValidationError, FloatField
from flask_wtf import FlaskForm
from app.expense.forms import ExpenseForm, max_decimals
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

    form.validate_sum(form.payers, SplitType.AMOUNT)
    form.validate_sum(form.payers, SplitType.EQUALLY)
    form.validate_sum(form.payers, SplitType.PERCENTAGE)

    assert not form.payers.errors
    assert not form.owers.errors


def test_validate_sum_invalid(request_context):
    form = ExpenseForm()
    form.amount.data = 100.0
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})

    form.validate_sum(form.payers, SplitType.EQUALLY)
    with pytest.raises(ValidationError):
        form.validate_sum(form.payers, SplitType.AMOUNT)
    with pytest.raises(ValidationError):
        form.validate_sum(form.payers, SplitType.PERCENTAGE)

    assert form.payers.errors == (
        "Payers total must equal to the expense total.",
        "Payers percentages must sum to 100.",
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


def test_validate_invalidated_by_super_first_on_negative_amount(request_context):
    form = ExpenseForm()
    form.amount.data = -100.0
    form.payers_split.data = SplitType.AMOUNT
    form.owers_split.data = SplitType.PERCENTAGE
    form.category.data = ExpenseCategory.OTHER
    form.description.data = "Test"
    form.payers.append_entry({"user_id": 1, "amount": 50.0})
    form.payers.append_entry({"user_id": 2, "amount": 40.0})

    assert not form.validate()
    assert form.errors["amount"] == ["Number must be at least 0."]
    assert "payers" not in form.errors
    assert form.payers.errors == []


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


class TestForm(FlaskForm):
    amount = FloatField(validators=[max_decimals(2)])


def test_max_decimals_valid(request_context):
    form = TestForm(amount=10.12)
    assert form.validate() is True


def test_max_decimals_valid_no_value(request_context):
    form = TestForm(amount=None)
    assert form.validate() is True


def test_max_decimals_invalid(request_context):
    form = TestForm(amount=10.123)
    form.validate()

    assert form.errors["amount"] == ["Amount must have at most 2 decimal places."]
    assert form.amount.errors == ["Amount must have at most 2 decimal places."]


def test_max_decimals_negative_value(request_context):
    form = TestForm(amount=-10.12)
    assert form.validate() is True


def test_max_decimals_invalid_negative(request_context):
    form = TestForm(amount=-10.123)
    form.validate()
    assert form.errors["amount"] == ["Amount must have at most 2 decimal places."]
    assert form.amount.errors == ["Amount must have at most 2 decimal places."]
