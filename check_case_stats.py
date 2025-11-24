"""
Check case statistics in database to diagnose dashboard counter issue.
"""
from app.db import SessionLocal
from app.models import Case
import json

db = SessionLocal()

try:
    # Get all cases
    cases = db.query(Case).all()
    
    print(f"\n{'='*60}")
    print(f"TOTAL CASES IN DATABASE: {len(cases)}")
    print(f"{'='*60}\n")
    
    # Analyze each case
    screening_count = 0
    staging_count = 0
    unknown_count = 0
    case_type_count = 0
    
    print("CASE ANALYSIS:")
    print("-" * 60)
    
    for case in cases:
        case_id = case.id
        
        # Check input_data for task field
        task_from_input = None
        if case.input_data:
            task_from_input = case.input_data.get('task', 'NOT_SET')
        
        # Check case_type column
        case_type_value = case.case_type or 'NULL'
        
        print(f"Case #{case_id}:")
        print(f"  - input_data['task']: {task_from_input}")
        print(f"  - case_type column: {case_type_value}")
        
        # Count based on task (what backend uses)
        if task_from_input == 'screening':
            screening_count += 1
            print(f"  > Counted as SCREENING")
        elif task_from_input == 'staging':
            staging_count += 1
            print(f"  > Counted as STAGING")
        else:
            unknown_count += 1
            print(f"  > UNKNOWN/NOT_SET")
        
        # Count case_type if set
        if case_type_value and case_type_value != 'NULL':
            case_type_count += 1
        
        print()
    
    print(f"{'='*60}")
    print("SUMMARY:")
    print(f"{'='*60}")
    print(f"Total Cases: {len(cases)}")
    print(f"Screening Cases (from input_data['task']): {screening_count}")
    print(f"Staging Cases (from input_data['task']): {staging_count}")
    print(f"Unknown/Not Set: {unknown_count}")
    print(f"Cases with case_type column set: {case_type_count}")
    print(f"{'='*60}\n")
    
    # Show what backend /cases/report returns
    print("BACKEND API LOGIC (/cases/report):")
    print("-" * 60)
    print(f"screening_cases = sum(1 for c in cases if c.input_data.get('task') == 'screening')")
    print(f"staging_cases = sum(1 for c in cases if c.input_data.get('task') == 'staging')")
    print()
    print(f"Expected Results:")
    print(f"  total_cases: {len(cases)}")
    print(f"  screening_cases: {screening_count}")
    print(f"  staging_cases: {staging_count}")
    print(f"{'='*60}\n")
    
    # Check for cases without task field
    if unknown_count > 0:
        print(f"WARNING: {unknown_count} cases don't have 'task' field in input_data!")
        print(f"   These cases won't be counted in screening/staging stats.\n")
        
        print("Cases without task field:")
        for case in cases:
            if not case.input_data or case.input_data.get('task') in [None, 'NOT_SET']:
                print(f"  - Case #{case.id} (created: {case.created_at})")
                if case.input_data:
                    print(f"    input_data keys: {list(case.input_data.keys())}")
                else:
                    print(f"    input_data: NULL")
        
        print("\nFIX: These cases need to have the 'task' field set in input_data")
        print("   You can fix this by re-running them through the workflow")
        print("   Or update them manually in the database\n")

finally:
    db.close()

