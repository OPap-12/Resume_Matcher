from models.db import init_db, SessionLocal, User
from services.auth_service import get_password_hash
import traceback

try:
    init_db()
    db = SessionLocal()
    email = "test40@example.com"
    pwd = "password123"
    
    hashed = get_password_hash(pwd)
    u = User(email=email, hashed_password=hashed)
    db.add(u)
    db.commit()
    print("SUCCESS_USER_CREATED")
except Exception as e:
    with open("local_test_log.txt", "w") as f:
        traceback.print_exc(file=f)
