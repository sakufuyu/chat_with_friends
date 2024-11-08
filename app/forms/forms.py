# forms.py
from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField, 
    TextAreaField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from flask import flash

from app.models.models import User
from app.utils.password import confirm_password


# Login form
class LoginForm(FlaskForm):
    email = StringField("E-mail: ", validators=[DataRequired(), Email()])
    password = PasswordField("Password: ", validators=[DataRequired(), EqualTo("confirm_password", message="Password does not match.")])
    confirm_password = PasswordField("Confirm password: ", validators=[DataRequired()])
    submit = SubmitField("Log in")


# Register form
class RegisterForm(FlaskForm):
    email = StringField("E-mail: ", validators=[DataRequired(), Email("Wrong e-mail address")])
    username = StringField("Name: ", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if (User.get_user_by_email(field.data)):
            raise ValidationError("You cannot use this e-mail address")


# Password setting form
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password: ", validators=[DataRequired(), EqualTo("confirm_password", message="Password does not match.")]
    )
    confirm_password = PasswordField(
        "Confirm password: ", validators=[DataRequired()]
    )
    submit = SubmitField("Update password")

    def validate_password(self, field):
        if (len(field.data) < 8):
            raise ValidationError("Set password more than 8 characters.")


# Forgot password form
class ForgotPasswordForm(FlaskForm):
    email = StringField("E-mail: ", validators=[DataRequired(), Email("Wrong e-mail address")])
    submit = SubmitField("Reset Password")

    def validate_email(self, field):
        if (not User.get_user_by_email(field.data)):
            raise ValidationError("E-mail does not exist.")


class UserForm(FlaskForm):
    email = StringField("E-mail: ", validators=[DataRequired(), Email("Wrong e-mail address")])
    username = StringField("Name: ", validators=[DataRequired()])
    picture_path = FileField("Upload picture")
    submit = SubmitField("Update user info")

    def validate(self):
        if (not super(FlaskForm, self).validate()):
            return False
        user = User.get_user_by_email(self.email.data)
        if (user):
            if (user.id != current_user.get_id()):
                flash("Error, you cannot use the e-mail address")
                return False
        return True


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        "Password: ",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Password does not match.")
        ]
    )
    confirm_password = PasswordField(
        "Confirm password: ",
        validators=[DataRequired()]
    )
    submit = SubmitField("Update password")

    def validate_password(self, field):
        if (confirm_password(current_user.password, field.data)):
            raise ValidationError("Same password.")
        elif (len(field.data) < 8):
            raise ValidationError("Set password more than 8 characters.")


class MessageForm(FlaskForm):
    message = TextAreaField()
    submit = SubmitField("Send")

    def validate_message(self, field):
        if (len(field.data) > 500):
            raise ValidationError("Message is too long.")