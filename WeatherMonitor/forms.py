from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from firebase_db import FirebaseUser, get_user_by_username, get_user_by_email

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number (Optional)', validators=[Optional(), Length(min=10, max=20)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class SettingsForm(FlaskForm):
    email_alerts = BooleanField('Enable Email Alerts')
    sms_alerts = BooleanField('Enable SMS Alerts')
    phone_number = StringField('Phone Number')
    temperature_alert_min = FloatField('Min Temperature Alert (°C)')
    temperature_alert_max = FloatField('Max Temperature Alert (°C)')
    humidity_alert_min = FloatField('Min Humidity Alert (%)')
    humidity_alert_max = FloatField('Max Humidity Alert (%)')
    air_quality_alert = FloatField('Air Quality Alert Threshold (ppm)')
    language = SelectField(
        'Langue du site',
        choices=[('fr', 'Français'), ('en', 'English'), ('ar', 'العربية')],
        default='fr'
    )
    submit = SubmitField('Save Settings')

class PredictionForm(FlaskForm):
    hours = SelectField('Prediction Horizon', choices=[
        (6, '6 hours'),
        (12, '12 hours'),
        (24, '24 hours'),
        (48, '48 hours')
    ], coerce=int)
    submit = SubmitField('Generate Prediction')
