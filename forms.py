from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, URL
from flask_ckeditor import CKEditorField

# Classes for the WTF-Forms
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField("Google Maps (URL)", validators=[DataRequired(), URL()])
    submit = SubmitField(label="Submit")

class ProjectForm(FlaskForm):
    # id = IntegerField('Project ID num', validators=[DataRequired()])
    projectName = StringField('Project Name', validators=[DataRequired()])
    technologiesUsed = StringField('Technologies Used', validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()]) # The description is using a CKEditorField and not a StringField
    difficultyRating = SelectField("Difficulty Rating", choices=["🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"], validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label="Submit")