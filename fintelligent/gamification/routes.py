from flask import Blueprint, render_template, jsonify, current_app, request, redirect, url_for, flash
from flask_login import current_user, login_required
from fintelligent.extensions import db
from fintelligent.gamification.models import GamificationProfile, UserBadge, UserChallenge
import json
import os
from datetime import datetime

gamification = Blueprint('gamification', __name__)

# Daily Trivia Data (MVP)
TRIVIA_QUESTIONS = [
    {
        "q": "What is the full form of SIP?",
        "options": ["Systematic Investment Plan", "Simple Interest Part", "Safe Investment Process", "Stock Index Price"],
        "answer": "Systematic Investment Plan",
        "explanation": "SIP allows you to invest small amounts regularly in mutual funds."
    },
    {
        "q": "Which of these is a risk-free investment?",
        "options": ["Crypto", "Stocks", "Fixed Deposit (FD)", "Mutual Funds"],
        "answer": "Fixed Deposit (FD)",
        "explanation": "FDs are generally considered low-risk compared to market-linked instruments."
    },
    {
        "q": "What is the '50-30-20' rule?",
        "options": ["Eat 50, Sleep 30, Work 20", "Needs 50, Wants 30, Savings 20", "Stocks 50, Gold 30, Cash 20", "Spend 50, Save 30, Donate 20"],
        "answer": "Needs 50, Wants 30, Savings 20",
        "explanation": "A popular budgeting rule: 50% for needs, 30% for wants, and 20% for savings."
    },
    {
        "q": "Who regulates the stock market in India?",
        "options": ["RBI", "SEBI", "SBI", "LIC"],
        "answer": "SEBI",
        "explanation": "The Securities and Exchange Board of India (SEBI) regulates the securities market."
    },
     {
        "q": "What is the minimum age to open a Demat account in India?",
        "options": ["18", "21", "No minimum age (with guardian)", "25"],
        "answer": "No minimum age (with guardian)",
        "explanation": "A minor can open a Demat account with a guardian."
    }
]

def get_daily_trivia():
    """Get a trivia question based on the day of the year."""
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(TRIVIA_QUESTIONS)
    return TRIVIA_QUESTIONS[index]

def get_financial_kundali(user):
    """Generate a fun financial horoscope based on user data."""
    # This would ideally query the Expense model
    # For MVP, we'll randomize or use a placeholder if no data
    # implementing a simple specific logic:
    
    import random
    
    # Check if we can access expenses (avoid circular imports if possible, or do inside)
    from fintelligent.auth.models import Expense
    
    expenses = Expense.query.filter_by(user_id=user.id).all()
    
    if not expenses:
        return {
            "rashi": "Newbie Narcissus",
            "dosha": "Data Deficiency",
            "prediction": "Your financial future is a blank slate. Start logging expenses to reveal your destiny!",
            "lucky_color": "Green",
            "icon": "🌱"
        }
        
    total_spend = sum(e.amount for e in expenses)
    if total_spend == 0:
        return {
             "rashi": "Saintly Saver",
             "dosha": "None",
             "prediction": "You have spent nothing! Either you are a monk or you forgot to log.",
             "lucky_color": "White",
             "icon": "🧘"
        }
        
    category_spend = {}
    for e in expenses:
        cat = e.category.lower()
        category_spend[cat] = category_spend.get(cat, 0) + e.amount
        
    # Analyze
    food_spend = category_spend.get('food', 0) + category_spend.get('dining', 0) + category_spend.get('groceries', 0)
    shopping_spend = category_spend.get('shopping', 0) + category_spend.get('clothing', 0)
    
    food_ratio = food_spend / total_spend
    shopping_ratio = shopping_spend / total_spend
    
    if food_ratio > 0.4:
        return {
            "rashi": "Gastronomic Gemini",
            "dosha": "Zomato-Swiggy Linkage",
            "prediction": "Your wealth is being digested faster than it is earned. Cook at home to appease the wealth gods.",
            "lucky_color": "Orange",
            "icon": "🍔"
        }
    elif shopping_ratio > 0.3:
        return {
            "rashi": "Impulsive Indra",
            "dosha": "Sale Spirit",
            "prediction": "You possess the power to vanish money instantly. Beware of '50% Off' signs.",
            "lucky_color": "Red",
            "icon": "🛍️"
        }
    else:
        return {
            "rashi": "Balanced Buddha",
            "dosha": "None",
            "prediction": "You are walking the middle path. Nirvana (Financial Freedom) is within reach.",
            "lucky_color": "Blue",
            "icon": "⚖️"
        }


def load_gamification_config():
    """Load the gamification config JSON file."""
    try:
        config_path = os.path.join(current_app.root_path, 'gamification_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading gamification config: {e}")
        return None

def get_or_create_profile(user):
    """Ensure the user has a gamification profile."""
    profile = GamificationProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = GamificationProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
    return profile

@gamification.route('/gamification')
@login_required
def dashboard():
    """Render the gamification dashboard."""
    config = load_gamification_config()
    profile = get_or_create_profile(current_user)
    
    # Update Daily Streak
    update_streak(profile)
    
    # Auto-update any tracking-based challenges
    check_auto_challenges(profile)
    
    # Map DB objects to the format template expects
    earned_badges = [b.badge_id for b in profile.badges]
    
    # Create a dict of active challenges with their full DB object (for progress)
    active_challenges_map = {}
    for c in profile.challenges:
        if c.status == 'active':
            # Attach parsed progress for template
            try:
                c.progress = json.loads(c.progress_data)
            except:
                c.progress = {}
            active_challenges_map[c.challenge_id] = c
            
    active_challenge_ids = list(active_challenges_map.keys())

    user_state = {
        "level": profile.level,
        "xp": profile.xp,
        "next_level_xp": profile.next_level_xp(),
        "title": profile.get_title(),
        "streak_count": profile.streak_count,
        "badges_earned": earned_badges,
        "active_challenges": active_challenge_ids,
        "challenge_objects": active_challenges_map
    }
    
    kundali = get_financial_kundali(current_user)
    daily_trivia = get_daily_trivia()
    
    return render_template('gamification.html', config=config, user=user_state, now=datetime.utcnow(), kundali=kundali, trivia=daily_trivia)

def check_auto_challenges(profile):
    """Checks and updates progress for challenges that track data automatically."""
    from fintelligent.auth.models import Expense
    from datetime import timedelta
    
    active_autos = UserChallenge.query.filter_by(profile_id=profile.id, status='active').all()
    
    for chal in active_autos:
        if chal.challenge_id == 'chal_002': # No Zomato Week
            # Logic: Check last 7 days for any Zomato/Swiggy expenses
            start_date = chal.joined_at
            now = datetime.utcnow()
            
            # Keywords to watch
            food_apps = ['zomato', 'swiggy', 'uber eats', 'foodpanda', 'blinkit', 'zepto']
            
            # Check for violations since joined_at
            violations = Expense.query.filter(
                Expense.user_id == profile.user_id,
                Expense.date >= start_date
            ).all()
            
            has_violation = False
            for v in violations:
                if any(app in v.merchant.lower() for app in food_apps):
                    has_violation = True
                    break
            
            if has_violation:
                # Streak broken! Reset joined_at to 'now' to start over
                chal.joined_at = now
                # Optionally log this in progress_data
                try:
                    data = json.loads(chal.progress_data)
                except:
                    data = {}
                data['last_violation'] = now.strftime("%Y-%m-%d %H:%M:%S")
                chal.progress_data = json.dumps(data)
                db.session.commit()
            else:
                # Check if 7 days have passed
                if (now - start_date).days >= 7:
                    # Completion!
                    chal.status = 'completed'
                    chal.completed_at = now
                    
                    # Rewards
                    reward_xp = 200
                    profile.xp += reward_xp
                    
                    if profile.check_level_up():
                        flash(f'🎉 Level Up! You are now Level {profile.level}!', 'success')
                        
                    new_badge = UserBadge(profile_id=profile.id, badge_id='badge_homechef')
                    db.session.add(new_badge)
                    db.session.commit()
                    flash('🎉 You did it! No Zomato Week completed. Home Chef badge unlocked!', 'success')

@gamification.route('/gamification/challenge/join', methods=['POST'])
@login_required
def join_challenge():
    challenge_id = request.form.get('challenge_id')
    profile = get_or_create_profile(current_user)
    
    # Check if already joined
    existing = UserChallenge.query.filter_by(profile_id=profile.id, challenge_id=challenge_id, status='active').first()
    if existing:
        flash('You are already tracking this challenge!', 'info')
        return redirect(url_for('gamification.dashboard'))
    
    new_chal = UserChallenge(profile_id=profile.id, challenge_id=challenge_id)
    db.session.add(new_chal)
    db.session.commit()
    
    flash('Challenge Accepted! Good luck! 🚀', 'success')
    return redirect(url_for('gamification.dashboard'))

@gamification.route('/gamification/challenge/update', methods=['POST'])
@login_required
def update_challenge():
    challenge_id = request.form.get('challenge_id')
    amount = float(request.form.get('amount', 0))
    
    profile = get_or_create_profile(current_user)
    challenge = UserChallenge.query.filter_by(profile_id=profile.id, challenge_id=challenge_id, status='active').first()
    
    if not challenge:
        flash('Challenge not found or not active.', 'error')
        return redirect(url_for('gamification.dashboard'))
    
    # Update Progress
    try:
        data = json.loads(challenge.progress_data)
    except:
        data = {}
        
    current_savings = data.get('savings', 0)
    current_checkins = data.get('checkins', 0)
    
    # If input is boolean/count based (amount=1 usually)
    if amount == 1:
        current_checkins += 1
        data['checkins'] = current_checkins
        
    # If input is value based
    new_total = current_savings + amount
    data['savings'] = new_total
    
    # Log valid entry
    if 'history' not in data:
        data['history'] = []
    data['history'].append({
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'amount': amount
    })
    
    challenge.progress_data = json.dumps(data)
    
    config = load_gamification_config()
    chal_config = next((c for c in config['challenges'] if c['id'] == challenge_id), None)
    
    msg = f"Logged! Progress updated."
    if amount > 1:
        msg = f"Logged ₹{int(amount)}! Total saved: ₹{int(new_total)}."
    
    # Check completion (Dynamic logic)
    if chal_config and 'success_condition' in chal_config:
        cond = chal_config['success_condition']
        completed = False
        
        # Parse simple conditions
        # e.g. "cumulative_savings >= 500"
        # e.g. "checkins >= 5"
        # e.g. "applied == true" (handled by simple boolean input check)
        
        if "cumulative_savings >=" in cond:
            target = float(cond.split('>=')[1].strip())
            if new_total >= target:
                completed = True
        elif "checkins >=" in cond:
            target = float(cond.split('>=')[1].strip())
            if current_checkins >= target:
                completed = True
        elif "applied == true" in cond:
            # If we logged anything for this boolean challenge, it's done
            completed = True
            
        if completed:
            challenge.status = 'completed'
            challenge.completed_at = datetime.utcnow()
            
            # Award XP
            reward_xp = chal_config['reward']['xp']
            profile.xp += reward_xp
            
            # Check Level Up
            if profile.check_level_up():
                msg = f"🎉 LEVEL UP! You reached Level {profile.level}! " + msg
            else:
                msg = f"🎉 Challenge Completed! +{reward_xp} XP! " + msg

            # Award Badge if applicable
            badge_id = chal_config['reward'].get('badge_id')
            if badge_id:
                new_badge = UserBadge(profile_id=profile.id, badge_id=badge_id)
                db.session.add(new_badge)
                msg += " New Badge Unlocked!"
            
    db.session.commit()
    flash(msg, 'success')
    
    return redirect(url_for('gamification.dashboard'))

@gamification.route('/api/gamification')
def get_config():
    """Return the raw gamification config."""
    config = load_gamification_config()
    return jsonify(config)

@gamification.route('/api/gamification/benchmark')
@login_required
def get_benchmark():
    """Get anonymous benchmarking data."""
    from fintelligent.auth.models import Expense
    from sqlalchemy import func
    
    # Peer Group: Students/Youth (simplified as all users for now)
    # Average monthly savings (simulated as monthly_budget - monthly_expenses)
    stats = db.session.query(
        func.avg(Expense.amount),
        func.count(Expense.id)
    ).all()
    
    # In a real app, we'd query by user category (e.g., students)
    # Peer average (hardcoded/simulated for now based on typical student data)
    peer_avg_savings = 3200 
    
    # User's actual monthly savings (Current month)
    user_expenses_this_month = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.strftime('%m', Expense.date) == datetime.utcnow().strftime('%m')
    ).scalar() or 0
    
    user_savings = max(0, current_user.monthly_budget - user_expenses_this_month)
    
    return jsonify({
        "peer_avg_savings": peer_avg_savings,
        "user_savings": user_savings,
        "percentile": 65 if user_savings > 2000 else 30, # Simulated
        "social_proof": "Join 12,000 students who aren't broke in their 20s"
    })

@gamification.route('/api/gamification/flex-cards')
@login_required
def get_flex_cards():
    """Generate data for shareable stories."""
    from fintelligent.auth.models import Expense
    from sqlalchemy import func
    
    user_expenses_this_month = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.strftime('%m', Expense.date) == datetime.utcnow().strftime('%m')
    ).scalar() or 0
    
    user_savings = max(0, current_user.monthly_budget - user_expenses_this_month)
    profile = get_or_create_profile(current_user)

    cards = [
        {
            "id": "monthly_save",
            "title": f"Saved ₹{int(user_savings)} this month",
            "icon": "💸",
            "subtitle": "FinTelligent | Financial Freedom",
            "color": "#00C896"
        },
        {
            "id": "streak",
            "title": f"{profile.streak_count} Day Savings Streak!",
            "icon": "🔥",
            "subtitle": "No days off. Money never sleeps.",
            "color": "#FF6B35"
        }
    ]
    
    if user_savings > 10000:
        cards.append({
            "id": "milestone",
            "title": "₹10K Emergency Fund Hit! 🎯",
            "icon": "🛡️",
            "subtitle": "Unbreakable. FinTelligent",
            "color": "#7C3AED"
        })
        
    return jsonify(cards)

def update_streak(profile):
    """Update user streak based on activity."""
    from datetime import date
    today = date.today()
    
    if profile.last_activity_date:
        last_date = profile.last_activity_date.date()
        diff = (today - last_date).days
        
        if diff == 1:
            # Consecutive day
            profile.streak_count += 1
            if profile.streak_count > profile.long_streak_record:
                profile.long_streak_record = profile.streak_count
        elif diff > 1:
            # Streak broken
            profile.streak_count = 1
        # If diff == 0, already tracked today
    else:
        profile.streak_count = 1
        
    profile.last_activity_date = datetime.utcnow()
    db.session.commit()
