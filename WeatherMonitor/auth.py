from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm, SettingsForm
from datetime import datetime
import logging

# Ajout de l'import Firebase
from firebase_db import (
    get_user_by_username, get_user_by_email, create_user,
    get_sensor_data, get_alerts, get_user_settings, save_user_settings
)

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Context processor to add variables to all templates
@auth_bp.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Try to find the user by username
        user = get_user_by_username(form.username.data)
        
        # Check if user exists and password is correct
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            return redirect(url_for('auth.login'))
        
        # Log user in
        login_user(user, remember=form.remember_me.data)
        logger.info(f"User {user.username} logged in successfully")
        
        # Redirect to the requested page or dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists in Firestore
        existing_user = get_user_by_username(form.username.data)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_email = get_user_by_email(form.email.data)
        if existing_email:
            flash('Email already registered. Please use a different email or login.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new Firebase user
        user = create_user(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            phone_number=form.phone_number.data
        )
        if user:
            logger.info(f"New user registered in Firestore: {user.username}")
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            logger.error("Failed to register user in Firestore")
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Récupérer les paramètres utilisateur depuis Firebase
    user_settings = get_user_settings(current_user.id)
    form = SettingsForm(data=user_settings or {})
    if form.validate_on_submit():
        # Sauvegarder les paramètres dans Firebase
        settings_data = {
            'email_alerts': form.email_alerts.data,
            'sms_alerts': form.sms_alerts.data,
            'temperature_alert_min': form.temperature_alert_min.data,
            'temperature_alert_max': form.temperature_alert_max.data,
            'humidity_alert_min': form.humidity_alert_min.data,
            'humidity_alert_max': form.humidity_alert_max.data,
            'air_quality_alert': form.air_quality_alert.data,
            'phone_number': form.phone_number.data
        }
        save_user_settings(current_user.id, settings_data)
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))
    return render_template('settings.html', title='Settings', form=form)
