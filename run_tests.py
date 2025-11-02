#!/usr/bin/env python
"""
Test Runner for H. pylori CDSS
Runs all tests and displays formatted results for documentation
"""

import subprocess
import sys
from datetime import datetime


def print_header():
    """Print test header."""
    print("\n" + "="*80)
    print("  H. PYLORI CDSS - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"  Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


def print_section(title):
    """Print section header."""
    print("\n" + "-"*80)
    print(f"  {title}")
    print("-"*80 + "\n")


def run_pytest(test_file=None, verbose=True):
    """Run pytest with specified options."""
    cmd = ["pytest"]
    
    if test_file:
        cmd.append(test_file)
    
    if verbose:
        cmd.extend(["-v", "--tb=short"])
    
    # Add color output and show summary
    cmd.extend(["--color=yes", "-ra"])
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    """Run all test suites."""
    print_header()
    
    test_suites = [
        ("Backend Authentication Tests", "tests/test_auth.py"),
        ("Recommendation API Tests", "tests/test_recommend.py"),
        ("Case Management Tests", "tests/test_cases.py"),
        ("ML Models Tests", "tests/test_ml_models.py"),
        ("Clinical Workflow Tests", "tests/test_workflow.py"),
        ("Prescription Management Tests", "tests/test_prescriptions.py"),
    ]
    
    results = []
    
    for title, test_file in test_suites:
        print_section(title)
        returncode = run_pytest(test_file)
        results.append((title, returncode == 0))
        print()
    
    # Print summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80 + "\n")
    
    for title, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status:15} {title}")
    
    print("\n" + "="*80)
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    
    print(f"\n  Total Test Suites: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/total*100):.1f}%")
    print("\n" + "="*80 + "\n")
    
    # Return exit code
    return 0 if all(p for _, p in results) else 1


if __name__ == "__main__":
    sys.exit(main())

