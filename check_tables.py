"""Check database tables."""
from app.db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("\nTables in database:")
for table in tables:
    print(f"  - {table}")
print()
