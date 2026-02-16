from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .models import User
from fintelligent.extensions import db, login_manager, limiter

auth = Blueprint('auth', __name__)

# Setup Flask-Login
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        referral_code = request.form.get('referral_code')
        
        if User.get_by_username(username):
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('auth.register'))
            
        try:
            user = User(username=username)
            user.set_password(password)
            user.generate_referral_code()
            
            if referral_code:
                referrer = User.query.filter_by(referral_code=referral_code).first()
                if referrer:
                    user.referred_by = referral_code
            
            db.session.add(user)
            db.session.commit()
            
            # Login immediately after registration
            login_user(user)
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('auth.register'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/upgrade-premium', methods=['POST'])
@login_required
def upgrade_premium():
    try:
        current_user.is_premium = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Welcome to Fintelligent Pro!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home')) 