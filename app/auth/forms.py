from flask_wtf import FlaskForm  #
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField  #
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class SigninForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")
