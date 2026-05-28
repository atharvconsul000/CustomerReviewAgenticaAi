import requests
import json

BASE = "http://127.0.0.1:8000"

print("--- Testing Workflows ---")
# 1. Login user
user_res = requests.post(f"{BASE}/auth/login", json={"email": "user@example.com", "password": "user123"})
user_token = user_res.json()["access_token"]
print("User logged in")

# 2. Get reviews
reviews = requests.get(f"{BASE}/reviews", headers={"Authorization": f"Bearer {user_token}"}).json()
first_rev = reviews[0]["id"]
print(f"User found review {first_rev}")

# 3. Customer Chat
chat1 = requests.post(f"{BASE}/customer/chat", headers={"Authorization": f"Bearer {user_token}"}, json={"message": "I can't login to the app"})
print(f"Customer Chat 1: {chat1.json().get('reply', chat1.text)}")

# 4. Admin Login & Respond
admin_res = requests.post(f"{BASE}/auth/login", json={"email": "admin@example.com", "password": "admin123"})
admin_token = admin_res.json()["access_token"]
print("Admin logged in")

admin_respond = requests.put(f"{BASE}/admin/reviews/{first_rev}/respond", headers={"Authorization": f"Bearer {admin_token}"}, json={"admin_response": "We have fixed the login servers! Clear your cookies and try again."})
print(f"Admin responded: {admin_respond.json().get('admin_response')}")

# 5. Customer Chat 2
chat2 = requests.post(f"{BASE}/customer/chat", headers={"Authorization": f"Bearer {user_token}"}, json={"message": "I can't login to the app"})
print(f"Customer Chat 2: {chat2.json().get('reply', chat2.text)}")

