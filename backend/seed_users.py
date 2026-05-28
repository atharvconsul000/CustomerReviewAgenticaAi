from database import SessionLocal, User
from auth import hash_password

def seed_users():
    db = SessionLocal()
    if not db.query(User).first():
        admin = User(name="Admin User", email="admin@example.com", password_hash=hash_password("admin123"), role="admin")
        customer = User(name="Customer User", email="user@example.com", password_hash=hash_password("user123"), role="user")
        db.add_all([admin, customer])
        db.commit()
        print("Users seeded!")
    else:
        print("Users already exist.")

if __name__ == "__main__":
    seed_users()
