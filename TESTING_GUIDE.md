# H. pylori CDSS - Testing Guide

## 📋 Overview

This guide explains how to run the comprehensive test suite for the H. pylori Clinical Decision Support System.

## 🧪 Test Coverage

### 1. **Backend Tests**
- Authentication & Authorization
- User Management
- JWT Token Handling
- Role-Based Access Control (RBAC)

### 2. **ML Model Tests**
- Symptom Assessment Model
- Lab Screening Model  
- RIC Staging Model (Antibiotic Resistance)
- Model Integration

### 3. **Clinical Workflow Tests**
- Stage 1: Symptom Assessment
- Stage 2: Lab Screening
- Stage 3: RIC Staging
- Complete Patient Journey
- Workflow Integration

### 4. **Prescription Management Tests**
- Prescription Creation
- Prescription Retrieval
- Prescription Updates
- Patient Prescription History
- Print Functionality

### 5. **API Endpoint Tests**
- Recommendation Engine
- Batch Processing
- Case Management
- Health Checks

---

## 🚀 Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Or install from requirements.txt (already included)
pip install -r requirements.txt
```

### Option 1: Run All Tests (Recommended for Screenshots)

**Windows:**
```bash
python run_tests.py
```

**Linux/Mac:**
```bash
python3 run_tests.py
```

This will run all test suites with formatted output perfect for screenshots!

### Option 2: Run Quick Test (Windows Only)

```bash
run_quick_test.bat
```

### Option 3: Run Specific Test Suites

```bash
# Authentication tests
pytest tests/test_auth.py -v

# ML Models tests
pytest tests/test_ml_models.py -v

# Workflow tests
pytest tests/test_workflow.py -v

# Prescription tests
pytest tests/test_prescriptions.py -v

# Recommendation tests
pytest tests/test_recommend.py -v

# Case management tests
pytest tests/test_cases.py -v
```

### Option 4: Run with Coverage Report

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

This generates a coverage report in `htmlcov/index.html`

---

## 📊 Test Results for README

### How to Take Screenshots

1. **Open Terminal/Command Prompt**
2. **Run**: `python run_tests.py`
3. **Take Screenshot** when tests complete
4. **Save as**: `images/test_results_<section>.png`

### Recommended Screenshots:

#### 1. **All Tests Overview**
```bash
python run_tests.py
```
Screenshot: Shows all 6 test suites passing

#### 2. **Authentication Tests**
```bash
pytest tests/test_auth.py -v
```
Screenshot: 10+ tests passing for auth

#### 3. **ML Models Tests**
```bash
pytest tests/test_ml_models.py -v
```
Screenshot: Model validation tests passing

#### 4. **Workflow Tests**
```bash
pytest tests/test_workflow.py -v
```
Screenshot: 3-stage workflow tests passing

#### 5. **Prescription Tests**
```bash
pytest tests/test_prescriptions.py -v
```
Screenshot: Prescription CRUD tests passing

#### 6. **Coverage Report**
```bash
pytest --cov=app --cov-report=term
```
Screenshot: Code coverage percentage

---

## 📈 Expected Results

### All Tests Should Show:

```
==================== Test Summary ====================
  ✅ PASSED       Backend Authentication Tests
  ✅ PASSED       Recommendation API Tests
  ✅ PASSED       Case Management Tests
  ✅ PASSED       ML Models Tests
  ✅ PASSED       Clinical Workflow Tests
  ✅ PASSED       Prescription Management Tests

  Total Test Suites: 6
  Passed: 6
  Failed: 0
  Success Rate: 100.0%
=======================================================
```

### Individual Test Files:

| Test File | Expected Tests | Coverage |
|-----------|---------------|----------|
| `test_auth.py` | 10+ tests | Authentication, Registration, Login |
| `test_recommend.py` | 8+ tests | Recommendations, Batch Processing |
| `test_cases.py` | 6+ tests | Case Management, CRUD |
| `test_ml_models.py` | 15+ tests | All 3 ML Models + Integration |
| `test_workflow.py` | 12+ tests | Complete 3-Stage Workflow |
| `test_prescriptions.py` | 10+ tests | Prescription Management |

---

## 🔍 Troubleshooting

### Issue: Tests Fail with Database Error

**Solution:**
```bash
# Delete test database
rm test.db

# Run tests again
python run_tests.py
```

### Issue: Import Errors

**Solution:**
```bash
# Make sure you're in project root
cd path/to/capstone101

# Ensure all dependencies installed
pip install -r requirements.txt
```

### Issue: ML Model Tests Fail

**Solution:**
- Ensure model files exist in `models/` directory
- Models: `screening_hp_pos_calibrated.joblib`, `staging_3class.joblib`
- Tests will use rule-based fallback if models missing

### Issue: Workflow Tests Timeout

**Solution:**
```bash
# Increase pytest timeout
pytest -v --timeout=60
```

---

## 📸 Screenshot Checklist for README

- [ ] Overall test summary (all suites)
- [ ] Authentication tests passing
- [ ] ML model tests passing
- [ ] Workflow integration tests passing
- [ ] Prescription tests passing
- [ ] Coverage report showing >80% coverage
- [ ] Individual test details (optional)

---

## 🎯 Test Quality Metrics

### Current Status:
- **Total Tests**: 50+
- **Test Files**: 6
- **Code Coverage**: 80%+ (target)
- **Pass Rate**: 100% (target)

### Test Categories:
- **Unit Tests**: 30+
- **Integration Tests**: 15+
- **End-to-End Tests**: 5+

---

## 📝 Adding New Tests

### Template for New Tests:

```python
"""Test description."""
import pytest
from fastapi import status


def test_feature_name(client, auth_headers):
    """Test what the feature does."""
    response = client.post("/endpoint",
        headers=auth_headers,
        json={
            "field": "value"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "expected_field" in data
    assert data["expected_field"] == "expected_value"
```

### Run New Tests:

```bash
pytest tests/test_new_file.py -v
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All tests pass (`python run_tests.py`)
- [ ] Coverage >80% (`pytest --cov=app`)
- [ ] No security vulnerabilities in dependencies
- [ ] Environment variables properly set
- [ ] Database migrations complete
- [ ] ML models loaded successfully
- [ ] API health check returns 200 OK

---

## 🆘 Support

If tests fail unexpectedly:
1. Check error messages in terminal
2. Review test logs
3. Verify database is accessible
4. Ensure all dependencies installed
5. Check Python version (3.10+ required)

---

**Ready for Testing!** 🚀

Run `python run_tests.py` to start comprehensive testing.

