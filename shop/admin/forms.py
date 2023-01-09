from wtforms import Form, BooleanField, StringField, PasswordField, validators

class RegistrationForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    email = StringField('Email Address', [validators.DataRequired(), validators.Length(min=4, max=45), validators.Email()])
    password = PasswordField('New Password', [
        validators.Length(min=8),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = StringField('Email Address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])