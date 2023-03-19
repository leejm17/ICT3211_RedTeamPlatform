from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, DataRequired, ValidationError, Regexp, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed



class SpyderForm(FlaskForm):
    gitHubUrl_1 = StringField(label='Github URL 1:', validators=[DataRequired()])
    gitHubUrl_2 = StringField(label='Github URL 2:', validators=[DataRequired()])
    gitHubUrl_3 = StringField(label='Github URL 3:', validators=[DataRequired()])
    gitHubUrl_4 = StringField(label='Github URL 4:', validators=[DataRequired()])
    gitHubUrl_5 = StringField(label='Github URL 5:', validators=[DataRequired()])
    submit = SubmitField(label='Submit URL')


class UploadForm(FlaskForm):
        upload = FileField('EXE and SH files only!', validators=[FileRequired(), FileAllowed(['exe', 'sh'], 'EXE and SH files only!!')])
