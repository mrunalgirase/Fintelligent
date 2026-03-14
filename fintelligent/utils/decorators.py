from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def tier_required(tiers):
    """
    Decorator to restrict access based on user subscription tier.
    tiers: List of allowed tiers (e.g. ['STUDENT', 'PRO'])
    """
    if isinstance(tiers, str):
        tiers = [tiers]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Allow PRO to access anything
            if current_user.plan == 'PRO':
                return f(*args, **kwargs)
                
            if current_user.plan not in tiers:
                flash(f"This feature requires a {', '.join(tiers)} subscription.", "info")
                return redirect(url_for('main.pricing'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
