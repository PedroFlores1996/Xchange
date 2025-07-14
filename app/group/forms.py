from flask_wtf import FlaskForm
from wtforms import (
    FieldList,
    StringField,
    SubmitField,
    ValidationError,
    IntegerField,
    HiddenField,
)
from wtforms.validators import DataRequired, Optional


class GroupForm(FlaskForm):
    name = StringField(
        "Group Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Group Name"},
    )
    description = StringField(
        "Group Description (Optional)",
        validators=[Optional()],
        render_kw={"placeholder": "Group Description (Optional)"},
    )
    users = FieldList(IntegerField("UserID", validators=[Optional()]))
    friend_ids = HiddenField("Friend IDs")
    submit = SubmitField("Create Group")

    def validate_name(self, field):
        if len(field.data) > 72:
            raise ValidationError("Group name must not exceed 72 characters.")


class AddUserToGroupForm(FlaskForm):
    friend_ids = HiddenField("Friend IDs")
    submit = SubmitField("Add Selected Users")
