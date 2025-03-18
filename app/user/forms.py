from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class AddFriendForm(FlaskForm):
    email = StringField("Friend's Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Add Friend")
