from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField
from wtforms.validators import DataRequired, Email


class AddFriendForm(FlaskForm):
    email = EmailField("Friend's Email", validators=[DataRequired()])
    submit = SubmitField("Add Friend")
