import sys
import os

from database import SessionLocal, Review, User
from ticket_data import generate_support_tickets

def seed():
    db = SessionLocal()
    
    # Get a user to assign reviews to (user_id 2 is the demo customer)
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = db.query(User).first()
        
    if not user:
        print("No users found to assign reviews to!")
        return

    # Map the existing generated tickets into DB reviews
    tickets = generate_support_tickets(count=120)
    
    # Convert severity to rating roughly
    severity_to_rating = {
        "low": 4,
        "medium": 3,
        "high": 2,
        "urgent": 1
    }
    
    new_reviews = []
    for t in tickets:
        r = Review(
            user_id=user.id,
            rating=severity_to_rating.get(t["severity"], 3),
            category=t["category"],
            comment=t["text"]
        )
        new_reviews.append(r)
        
    db.add_all(new_reviews)
    db.commit()
    print(f"Successfully seeded {len(new_reviews)} reviews into the database.")

if __name__ == "__main__":
    seed()
