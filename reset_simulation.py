
from app.database import SessionLocal, engine
from app import models
from sqlalchemy import text

def reset_simulation():
    db = SessionLocal()
    print("Resetting simulation...")
    
    # Clear Leaderboard
    db.query(models.Leaderboard).delete()
    print("Leaderboard cleared.")
    
    # Clear CTF Solves
    db.query(models.CTFSolve).delete()
    print("CTF Solves cleared.")
    
    # Reset User Status (active challenge, etc.)
    users = db.query(models.User).all()
    for user in users:
        user.active_challenge_id = None
        user.challenge_start_time = None
    
    db.commit()
    db.close()
    print("Simulation reset complete.")

if __name__ == "__main__":
    reset_simulation()
