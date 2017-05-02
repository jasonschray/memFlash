from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators

class loginForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    password     = PasswordField('Password')
    submit       = SubmitField ('Submit')


class signupForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    password     = PasswordField('Password')
    passwordRepeat     = PasswordField('Repeat Password')
    email = StringField('Email', [validators.Length(min=4, max=100)])
    submit       = SubmitField ('Submit')

