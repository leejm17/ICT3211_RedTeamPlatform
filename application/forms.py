from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, DataRequired, ValidationError, Regexp, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadForm(FlaskForm):
        upload = FileField('Only .exe and .sh files are accepted.', validators=[FileRequired(), FileAllowed(['exe', 'sh'], 'Only .exe and .sh files are accepted.')])
