from typing import Self, List

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SelectField,
    FieldList,
    FormField,
    IntegerField,
)
from wtforms.validators import DataRequired, NumberRange, Optional
from app.model.expense import ExpenseCategory
from app.splits.types import SplitType


class PayerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class OwerForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class ExpenseForm(FlaskForm):

    def validate_owers(self: Self, field: FieldList) -> None:
        if len(field.data) == 1:
            if len(self.payers.data) == 1:
                if field.data[0]["user_id"] == self.payers.data[0]["user_id"]:
                    raise ValueError(
                        "The only payer and only ower cannot be the same person."
                    )

    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=[(category, category.value) for category in ExpenseCategory],
        validators=[DataRequired()],
    )
    split = SelectField(
        "Split",
        choices=[(split_type, split_type.value) for split_type in SplitType],
        validators=[DataRequired()],
    )
    payers = FieldList(FormField(PayerForm), min_entries=1, validators=[DataRequired()])
    owers = FieldList(
        FormField(OwerForm), min_entries=1, validators=[DataRequired(), validate_owers]
    )
    group_id = IntegerField("Group ID", validators=[Optional()])
