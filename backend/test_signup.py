from models.db import SessionLocal, init_db, User
from services.auth_service import get_password_hash
import traceback

init_db()
db = SessionLocal()
try:
    hashed_password = get_password_hash('password123')
    db_user = User(email='test2@example.com', hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    print('SUCCESS')
except Exception as e:
    print('ERROR:', e)
    traceback.print_exc()
