from construct import FlaskForm
from construct import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from construct.models import User
from wtforms import IntegerField, DateField, SelectField

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


class DelayForm(FlaskForm):

    type = SelectField(u'Category', choices=[('Workforce', 'Workforce'), ('Financial', 'Financial'), ('Weather', 'Weather'), ('Logistics', 'Logistics'), (' Miscellaneous', ' Miscellaneous')])
    description = StringField(label='Description', validators=[
                                DataRequired()])

    severity = SelectField(u'Severity', choices=[('Minor', 'Minor'), ('Medium', 'Medium'), ('Major', 'Major')])
    phase = SelectField(u'Phase', choices=[('Foundation', 'Foundation'), ('Interior', 'Interior'), ('Electrical', 'Electrical'), ('Plumbing', 'Plumbing'), ('Safety', 'Safety')])
    extended_days = IntegerField(label='Request for EOT in Days', validators=[
                             DataRequired()])
    date = DateField('Date', format='%Y-%m-%d') 
    submit = SubmitField(label='Submit Delay!')


class TaskForm(FlaskForm):
    Name = StringField(label='Name', validators=[
                                DataRequired()])
    Description = StringField(label='Description', validators=[
                                DataRequired()])

    phase = SelectField(u'Phase', choices=[('Foundation', 'Foundation'), ('Interior', 'Interior'), ('Electrical', 'Electrical'), ('Plumbing', 'Plumbing'), ('Safety', 'Safety')])
    percentage = IntegerField(label='Percentage in weight', validators=[
                             DataRequired()])

    start_date = DateField('Start Date', format='%Y-%m-%d') 
    end_date = DateField('End Date', format='%Y-%m-%d') 

    total_estimated_cost = IntegerField(label='Total estimated cost', validators=[
                             DataRequired()])

    submit = SubmitField(label='Submit Task')
    






    

   
 