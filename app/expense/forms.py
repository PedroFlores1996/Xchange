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
from app.splits import SplitType


class PayerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class OwerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class ExpenseForm(FlaskForm):
    def single_ower_not_payer(self, owers: FieldList) -> None:
        if len(owers.data) == 1 and len(self.payers.data) == 1:
            if self.payers.data[0]["user_id"] == owers.data[0]["user_id"]:
                error = "Single user cannot be both a payer and an ower."
                self.payers.errors += (error,)
                owers.errors += (error,)
                raise ValidationError(
                    "A single user cannot be both a payer and an ower."
                )

    def validate_amounts_sum_equals_total(self, users: FieldList) -> None:
        total = sum([user.amount.data for user in users])
        if total != self.amount.data:
            error = f"{users.label.text} total must equal to the expense total."
            users.errors += (error,)
            raise ValidationError(error)

    def validate_percentages_sum_is_100(self, users: FieldList) -> None:
        total = sum([user.amount.data for user in users])
        if total != 100:
            error = f"{users.label.text} percentages must sum to 100."
            users.errors += (error,)
            raise ValidationError(error)

    def validate_sum(self, users: FieldList) -> None:
        if self.split.data == SplitType.AMOUNT:
            self.validate_amounts_sum_equals_total(users)
        elif self.split.data == SplitType.PERCENTAGE:
            self.validate_percentages_sum_is_100(users)

    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=ExpenseCategory.choices(),
        coerce=ExpenseCategory.coerce,
    )
    split = SelectField(
        "Split",
        choices=SplitType.choices(),
        validators=[DataRequired()],
        coerce=SplitType.coerce,
    )
    payers = FieldList(
        FormField(PayerForm),
        "Payers",
        validators=[DataRequired(), validate_sum],
    )
    owers = FieldList(
        FormField(OwerForm),
        "Owers",
        validators=[DataRequired(), validate_sum, single_ower_not_payer],
    )
    group_id = IntegerField("Group ID", validators=[Optional()])
