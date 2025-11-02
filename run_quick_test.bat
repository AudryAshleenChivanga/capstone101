@echo off
echo ========================================
echo H. pylori CDSS - Quick Test Suite
echo ========================================
echo.

echo [1/6] Testing Authentication...
pytest tests/test_auth.py -v --tb=short
echo.

echo [2/6] Testing Recommendations...
pytest tests/test_recommend.py -v --tb=short
echo.

echo [3/6] Testing ML Models...
pytest tests/test_ml_models.py -v --tb=short
echo.

echo [4/6] Testing Workflow...
pytest tests/test_workflow.py -v --tb=short
echo.

echo [5/6] Testing Prescriptions...
pytest tests/test_prescriptions.py -v --tb=short
echo.

echo [6/6] Testing Cases...
pytest tests/test_cases.py -v --tb=short
echo.

echo ========================================
echo All Tests Complete!
echo ========================================
pause

