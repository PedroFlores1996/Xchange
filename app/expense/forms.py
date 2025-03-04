from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SelectField,
    FieldList,
    FormField,
    IntegerField,
)
from wtforms import ValidationError
from wtforms.validators import DataRequired, NumberRange, Optional
from app.model.expense import ExpenseCategory
from app.splits.types import SplitType


def coerce_for(enum):
    def coerce(name):
        if isinstance(name, enum):
            return name
        try:
            return enum[name]
        except KeyError:
            raise enum(name)

    return coerce


class PayerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class OwerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class ExpenseForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=[(category, category.value) for category in ExpenseCategory],
        validators=[DataRequired()],
        coerce=coerce_for(ExpenseCategory),
    )
    split = SelectField(
        "Split",
        choices=[(split_type, split_type.value) for split_type in SplitType],
        validators=[DataRequired()],
        coerce=coerce_for(SplitType),
    )
    payers = FieldList(
        FormField(PayerForm),
        "Payers",
        validators=[DataRequired()],
    )
    owers = FieldList(
        FormField(OwerForm),
        "Owers",
        validators=[DataRequired()],
    )
    group_id = IntegerField("Group ID", validators=[Optional()])

    def single_ower_not_payer(self) -> None:
        if len(self.owers.data) == 1 and len(self.payers.data) == 1:
            if self.payers.data[0]["user_id"] == self.owers.data[0]["user_id"]:
                error = "Single user cannot be both a payer and an ower."
                self.payers.errors += (error,)
                self.owers.errors += (error,)
                raise ValidationError(
                    "A single user cannot be both a payer and an ower."
                )

    def validate_amounts_sum_equals_total(self, users: FieldList) -> None:
        total = sum([user.amount.data for user in users])
        if total != self.amount.data:
            error = f"{users.label.text} total must equal to the expense total."
            users.errors += (error,)
            raise ValidationError(error)

    def validate_amounts_sum(self) -> None:
        if self.split.data == SplitType.AMOUNT:
            self.validate_amounts_sum_equals_total(self.payers)
            self.validate_amounts_sum_equals_total(self.owers)

    def validate_percentages_sum_is_100(self, users: FieldList) -> None:
        total = sum([user.amount.data for user in users])
        if total != 100:
            error = f"{users.label.text} percentages must sum to 100."
            users.errors += (error,)
            raise ValidationError(error)

    def validate_percentages_sum(self) -> None:
        if self.split.data == SplitType.PERCENTAGE:
            self.validate_percentages_sum_is_100(self.payers)
            self.validate_percentages_sum_is_100(self.owers)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        try:
            self.single_ower_not_payer()
            self.validate_amounts_sum()
            self.validate_percentages_sum()
            return True
        except ValidationError:
            return False
