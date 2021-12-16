from construct import FlaskForm
from construct import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from construct.models import User
from wtforms import IntegerField, DateField

class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('The username is taken already. Sorry Son')

    def validate_email_address(self, email_to_check):
        email_add = User.query.filter_by(
            email_address=email_to_check.data).first()
        if email_add:
            raise ValidationError(
                'The email address is taken already. Sorry Son')

    username = StringField(label='User Name', validators=[
                           Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[
                                Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[
                              Length(min=6), DataRequired()])
    password2 = PasswordField(label='Password Confirmation', validators=[
                              EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account!')


class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired()])
    login_password = StringField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='purchase item!')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='sell item!')


class DelayForm(FlaskForm):

    type = StringField(label='Delay Type', validators=[
                           Length(min=2, max=30), DataRequired()])

    description = StringField(label='Description', validators=[
                                DataRequired()])

    severity = StringField(label='Severity', validators=[
                                DataRequired()])

    phase = StringField(label='Phase', validators=[
                                DataRequired()])

    delayedDays = IntegerField(label='Days Delayed', validators=[
                                DataRequired()])

    date = StringField(label='Date', validators=[
                                DataRequired()])
    
    submit = SubmitField(label='Submit Delay!')

    