import traceback
import sys

try:
    from models.db import SessionLocal, init_db, User
    from services.auth_service import get_password_hash
    import uuid

    init_db()
    db = SessionLocal()
    
    test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    pwd = "password123"
    
    print("Hashing password...")
    hashed = get_password_hash(pwd)
    print(f"Hashed password: {hashed}")
    
    print("Creating user...")
    u = User(email=test_email, hashed_password=hashed)
    db.add(u)
    db.commit()
    print("SUCCESS: User created successfully!")
    db.close()
except Exception as e:
    print("ERROR OCCURRED:")
    traceback.print_exc(file=sys.stdout)
