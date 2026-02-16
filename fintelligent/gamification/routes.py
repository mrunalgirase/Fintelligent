from flask import Blueprint, render_template, jsonify, current_app, request, redirect, url_for, flash
from flask_login import current_user, login_required
from fintelligent.extensions import db
from fintelligent.gamification.models import GamificationProfile, UserBadge, UserChallenge
import json
import os
from datetime import datetime

gamification = Blueprint('gamification', __name__)

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
        "badges_earned": earned_badges,
        "active_challenges": active_challenge_ids,
        "challenge_objects": active_challenges_map
    }
    
    return render_template('gamification.html', config=config, user=user_state, now=datetime.utcnow())

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
