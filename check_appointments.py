from app.db import SessionLocal
from app.models import Appointment, User

db = SessionLocal()

# Get all appointments
appointments = db.query(Appointment).all()

print('\n' + '='*70)
print('  ALL APPOINTMENTS IN DATABASE')
print('='*70)

if not appointments:
    print('❌ No appointments found in database!')
else:
    for apt in appointments:
        # Get clinician and specialist names
        clinician = db.query(User).filter(User.id == apt.clinician_id).first()
        specialist = db.query(User).filter(User.id == apt.specialist_id).first()
        
        print(f'\nAppointment ID: {apt.id}')
        print(f'  Clinician: {clinician.full_name if clinician else "Unknown"} (ID: {apt.clinician_id})')
        print(f'  Specialist: {specialist.full_name if specialist else "Unknown"} (ID: {apt.specialist_id})')
        print(f'  Status: {apt.status}')
        print(f'  Requested Date: {apt.requested_date}')
        print(f'  Reason: {apt.reason or "N/A"}')
        print(f'  Created: {apt.created_at}')
        print('-' * 70)

print(f'\nTotal appointments: {len(appointments)}')

# Show all users for reference
print('\n' + '='*70)
print('  ALL USERS (for reference)')
print('='*70)
users = db.query(User).all()
for u in users:
    print(f'ID: {u.id} | Username: {u.username:15} | Role: {u.role:10} | Name: {u.full_name}')

print('='*70 + '\n')

db.close()

