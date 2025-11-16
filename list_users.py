from app.db import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()

print('\n' + '='*60)
print('  ALL USERS IN SYSTEM')
print('='*60)
for u in users:
    name = u.full_name or 'N/A'
    print(f'Username: {u.username:15} | Role: {u.role:10} | Name: {name}')
print('='*60)
print(f'Total users: {len(users)}\n')

db.close()

