from app import app, db
from fintelligent.auth.models import User
from fintelligent.gamification.models import GamificationProfile
from fintelligent.gamification.routes import get_or_create_profile

with app.app_context():
    print("--- Debugging Gamification Access ---")
    
    # Get first user
    user = User.query.first()
    if not user:
        print("No users found in database!")
    else:
        print(f"Found user: {user.username} (ID: {user.id})")
        
        try:
            print("Attempting to access user.gamification_profile...")
            # This triggers the relationship query
            prof = user.gamification_profile
            print(f"Profile from relationship: {prof}")
            
            if not prof:
                print("Profile is None, trying get_or_create_profile...")
                prof = get_or_create_profile(user)
                print("Profile created/fetched:", prof)
                print(f"XP: {prof.xp}, Level: {prof.level}")
            else:
                print(f"Existing Profile XP: {prof.xp}")
                
        except Exception as e:
            print(f"!!! CAUGHT EXCEPTION !!!")
            print(e)
            import traceback
            traceback.print_exc()

    print("--- End Debug ---")
