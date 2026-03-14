from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from fintelligent.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    # Relationship to Gamification Profile
    gamification_profile = db.relationship('GamificationProfile', backref='user', uselist=False, lazy=True)

    # Monetization & Growth
    is_premium = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=True) # Default to student for target audience
    plan = db.Column(db.String(20), default='FREE') # FREE, STUDENT, PRO
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    referral_code = db.Column(db.String(10), unique=True, nullable=True)
    referred_by = db.Column(db.String(10), nullable=True)
    upi_id = db.Column(db.String(100), nullable=True)
    monthly_budget = db.Column(db.Float, default=20000.0)

    def generate_referral_code(self):
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=8))
        # Ensure uniqueness (simple check)
        while User.query.filter_by(referral_code=code).first():
             code = ''.join(random.choices(chars, k=8))
        self.referral_code = code

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    merchant = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_verified = db.Column(db.Boolean, default=True) # Scanned receipts are verified
    source = db.Column(db.String(50), default='receipt') # receipt, bank_statement
    matched_with_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=True)
    
    # Bill Management
    is_bill = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    is_paid = db.Column(db.Boolean, default=True) # Default to True for old receipts

    user = db.relationship('User', backref=db.backref('expenses', lazy=True))
    matched_with = db.relationship('Expense', remote_side=[id], post_update=True)

class Transaction(db.Model):
    __tablename__ = 'payment_transaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=False)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True)
    razorpay_signature = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='PENDING') # PENDING, SUCCESS, FAILED
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('transactions', lazy=True))