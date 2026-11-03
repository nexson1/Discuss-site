from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField,URLField
from wtforms.validators import DataRequired, Email , Length
from flask_ckeditor import CKEditorField


class DiscussRegistrationForm(FlaskForm):
 surname = StringField(
     'Surname',
     validators=[DataRequired()]
 )
 firstname = StringField(
     'Firstname',
    validators=[DataRequired()]
 )
 username = StringField(
     'Username',
    validators=[DataRequired()]
 )
 email = StringField(
     'Email',
     validators= [DataRequired(message='PLease enter a valid email')]
 )
 password = PasswordField(
     "Password",
     validators= [DataRequired(message='PLease enter a password')]
 )
 submit = SubmitField("Register")

class DiscussCommentForm(FlaskForm):
    body = CKEditorField("Comments", validators=[DataRequired()])
    submit = SubmitField("Comment")


class DiscussLoginForm(FlaskForm):
 email = StringField(
     'Email',
     validators= [DataRequired(message='PLease enter your email')]
 )
 password = PasswordField(
     'Password',
     validators= [DataRequired(message='PLease enter a your password')],

 )
 submit = SubmitField('Login')

class DiscussForm(FlaskForm):
    title = StringField(
        'Title of Discuss',
        validators=[DataRequired()]
    )
    subtitle = StringField(
        'subtitle',
        validators=[DataRequired()]
    )
    post = CKEditorField(
         'Start a Discuss',
     )
    submit = SubmitField(
         'Discuss',
     )



class ContactForm(FlaskForm):
 name = StringField(
     'Name',
     validators= [DataRequired(message='PLease enter your name')]
 )
 email = StringField(
     'Email',
     validators= [DataRequired(message='PLease enter a valid email'), Email()]
 )
 phone = StringField(
     'Password',
     validators= [DataRequired(message='PLease enter a valid phone number')]
 )
 message = TextAreaField(
     'Message',
     validators= [DataRequired()]
 )
 submit = SubmitField(
     'Send'
 )