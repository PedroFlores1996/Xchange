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
from app.split import SplitType


class ExpenseUserForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[DataRequired()])
    amount = FloatField("Amount", default=0.0, validators=[NumberRange(min=0)])


class ExpenseForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=ExpenseCategory.choices(),
        coerce=ExpenseCategory.coerce,
    )
    payers_split = SelectField(
        "Split",
        choices=SplitType.choices(),
        validators=[DataRequired()],
        coerce=SplitType.coerce,
    )
    owers_split = SelectField(
        "Split",
        choices=SplitType.choices(),
        validators=[DataRequired()],
        coerce=SplitType.coerce,
    )
    payers = FieldList(
        FormField(ExpenseUserForm),
        "Payers",
        validators=[DataRequired()],
    )
    owers = FieldList(
        FormField(ExpenseUserForm),
        "Owers",
        validators=[DataRequired()],
    )
    group_id = IntegerField("Group ID", validators=[Optional()])

    def validate_single_ower_not_payer(self) -> None:
        if len(self.owers.data) == 1 and len(self.payers.data) == 1:
            if self.payers.data[0]["user_id"] == self.owers.data[0]["user_id"]:
                error = "Single user cannot be both a payer and an ower."
                self.payers.errors += (error,)
                self.owers.errors += (error,)
                raise ValidationError(error)

    def _get_validation_error(self, users: FieldList, split: SplitType) -> str:
        total = sum([user.amount.data for user in users])
        if split == SplitType.AMOUNT and total != self.amount.data:
            return f"{users.label.text} total must equal to the expense total."
        elif split == SplitType.PERCENTAGE and total != 100:
            return f"{users.label.text} percentages must sum to 100."
        elif split == SplitType.EQUALLY and total != 0:
            return f"{users.label.text} total must be 0."

    def validate_sum(self, users: FieldList, split: SplitType) -> None:
        if error := self._get_validation_error(users, split):
            users.errors += (error,)
            raise ValidationError(error)

    def validate(self) -> bool:
        if not super().validate():
            return False

        try:
            self.validate_single_ower_not_payer()
            self.validate_sum(self.payers, self.payers_split.data)
            self.validate_sum(self.owers, self.owers_split.data)
        except ValidationError:
            return False

        return True
