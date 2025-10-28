"""Check telemed_sessions table structure."""
from app.db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('telemed_sessions')

print("\nColumns in telemed_sessions table:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")
print()
