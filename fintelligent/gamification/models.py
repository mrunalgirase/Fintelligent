from fintelligent.extensions import db
from datetime import datetime

class GamificationProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    badges = db.relationship('UserBadge', backref='profile', lazy=True)
    challenges = db.relationship('UserChallenge', backref='profile', lazy=True)

    def get_title(self):
        """Returns the title based on level."""
        # Simple mapping, ideal world this comes from config too
        titles = {
            1: "Money Aware",
            2: "Smart Saver",
            3: "Early Investor"
        }
        return titles.get(self.level, "Financial Guru")

    def next_level_xp(self):
        # Formula: Base 500 * Level
        return 500 * self.level

    def check_level_up(self):
        """Checks if XP triggers a level up. Returns new level if leveled up."""
        leveled_up = False
        while self.xp >= self.next_level_xp():
            self.xp -= self.next_level_xp()
            self.level += 1
            leveled_up = True
        return leveled_up

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('gamification_profile.id'), nullable=False)
    badge_id = db.Column(db.String(50), nullable=False) # ID from JSON config
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('gamification_profile.id'), nullable=False)
    challenge_id = db.Column(db.String(50), nullable=False) # ID from JSON config
    status = db.Column(db.String(20), default='active') # active, completed
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    progress_data = db.Column(db.Text, default='{}') # JSON string for flexible storage
