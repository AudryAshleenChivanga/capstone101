# 📋 Patient Registration & Saving System Explained

## 🔑 **How Patient Registration Works**

### **The Complete Flow:**

---

## 📝 **STAGE 1: Patient Registration (Screening Assessment)**

### **What Happens:**

1. **Clinician fills out Stage 1 form:**
   - Patient Name: "John Doe"
   - Age: 45
   - Sex: Male
   - Residence: Urban
   - Phone: +250 XXX XXX XXX
   - Symptoms: [Selected checkboxes]
   - Family History: Yes

2. **Clinician clicks "Submit Assessment"**

3. **Backend receives the data and:**
   ```python
   # In app/routes_workflow.py
   # The system calls get_or_create_patient()
   
   # Step 1: Generate unique Patient ID
   patient_id = "HP-2025-0001"  # Auto-incremented
   
   # Step 2: Create Patient record in database
   new_patient = Patient(
       patient_id = "HP-2025-0001",
       full_name = "John Doe",
       age = 45,
       sex = "M",
       residence = "Urban",
       phone = "+250 XXX XXX XXX",
       created_by = current_user.id,  # The logged-in clinician
       created_at = datetime.now()
   )
   db.add(new_patient)
   db.commit()
   
   # Step 3: Create Case record linked to Patient
   new_case = Case(
       patient_db_id = new_patient.id,  # Foreign key to Patient
       patient_pseudo_id = "HP-2025-0001",  # Also store ID for quick access
       patient_name = "John Doe",
       case_type = "screening",
       workflow_stage = "stage1_symptom",
       stage1_assessment = {...},  # All symptom data stored as JSON
       user_id = current_user.id
   )
   db.add(new_case)
   db.commit()
   ```

4. **Frontend receives response:**
   ```json
   {
       "patient_id": "HP-2025-0001",
       "case_id": 123,
       "assessment": {
           "risk_level": "moderate",
           "proceed_to_stage2": true,
           "recommended_tests": [...]
       }
   }
   ```

---

## 🔬 **STAGE 2: Lab Screening**

### **What Happens:**

1. **Patient ID is auto-filled:** `HP-2025-0001`
   - The system remembers from Stage 1
   - No need to re-enter patient name

2. **Clinician enters lab results and submits**

3. **Backend:**
   ```python
   # System finds existing Patient by ID
   patient = db.query(Patient).filter(
       Patient.patient_id == "HP-2025-0001"
   ).first()
   
   # Creates new Case for Stage 2, linked to same Patient
   new_case = Case(
       patient_db_id = patient.id,  # SAME patient
       patient_pseudo_id = "HP-2025-0001",
       case_type = "screening",
       workflow_stage = "stage2_lab",
       stage2_lab_results = {...},  # Lab data stored
       user_id = current_user.id
   )
   ```

---

## 💊 **STAGE 3: RIC Staging**

### **What Happens:**

1. **Patient ID auto-filled:** `HP-2025-0001`

2. **Clinician enters MIC values, mutations**

3. **Backend:**
   ```python
   # System finds same Patient
   patient = db.query(Patient).filter(
       Patient.patient_id == "HP-2025-0001"
   ).first()
   
   # Creates Case for Stage 3
   new_case = Case(
       patient_db_id = patient.id,  # SAME patient
       case_type = "staging",
       workflow_stage = "stage3_ric",
       stage3_ric_values = {...},
       stage_pred = "moderate",
       user_id = current_user.id
   )
   
   # Creates Prescription linked to Patient
   prescription = Prescription(
       patient_id = patient.id,  # SAME patient
       case_id = new_case.id,
       medications = [...],
       prescribed_by = current_user.id
   )
   ```

---

## 🗄️ **DATABASE STRUCTURE**

### **Patient Table** (One patient, one record)
```sql
id                 | patient_id      | full_name  | age | sex | phone
1                  | HP-2025-0001    | John Doe   | 45  | M   | +250...
2                  | HP-2025-0002    | Jane Smith | 32  | F   | +250...
```

### **Cases Table** (Multiple cases per patient)
```sql
id  | patient_db_id | patient_pseudo_id | case_type  | workflow_stage   | created_at
1   | 1             | HP-2025-0001      | screening  | stage1_symptom   | 2025-01-01
2   | 1             | HP-2025-0001      | screening  | stage2_lab       | 2025-01-02
3   | 1             | HP-2025-0001      | staging    | stage3_ric       | 2025-01-03
4   | 2             | HP-2025-0002      | screening  | stage1_symptom   | 2025-01-05
```

---

## ❓ **YOUR QUESTIONS ANSWERED**

### **Q1: Is patient saved by ID instead of name?**
**A:** Patient is saved by **BOTH**:
- **Patient ID** (HP-2025-XXXX) - Unique identifier, auto-generated
- **Full Name** (John Doe) - Stored with the patient record
- **Other data** - Age, sex, phone, etc.

The Patient table looks like this:
```
Patient(
    id = 1,                    # Database primary key
    patient_id = "HP-2025-0001", # Human-readable unique ID
    full_name = "John Doe",    # Patient's actual name
    age = 45,
    sex = "M",
    phone = "+250...",
    created_by = clinician_id
)
```

### **Q2: When we save, how does this work?**

**On Stage 1 (First time seeing patient):**
```
User enters: Name, Age, Sex, Symptoms
↓
System checks: Does "John Doe" already exist?
↓
NO → Create new Patient record
      - Generate new ID: HP-2025-0001
      - Save full_name: "John Doe"
      - Save all demographics
↓
Create Case record
      - Link to Patient (patient_db_id = 1)
      - Store Patient ID for quick access
      - Save Stage 1 assessment data
```

**On Stage 2 (Same patient, different day):**
```
User enters: Patient ID = HP-2025-0001
↓
System finds: Existing Patient (full_name = "John Doe")
↓
Create NEW Case record
      - Link to SAME Patient (patient_db_id = 1)
      - Different workflow_stage = "stage2_lab"
      - Patient info NOT duplicated
```

### **Q3: Can we search by name OR by ID?**
**A:** YES! Both work:

**Search by Patient ID:**
```python
patient = db.query(Patient).filter(
    Patient.patient_id == "HP-2025-0001"
).first()
# Returns: John Doe, age 45, etc.
```

**Search by Name:**
```python
patient = db.query(Patient).filter(
    Patient.full_name.ilike("%John%")
).first()
# Returns: HP-2025-0001, John Doe, age 45, etc.
```

---

## 🔄 **WORKFLOW SUMMARY**

```
PATIENT REGISTRATION (Stage 1):
┌─────────────────────────────────────┐
│ Clinician enters:                   │
│ - Name: John Doe                    │
│ - Age: 45                           │
│ - Sex: Male                         │
│ - Symptoms: [...]                   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ System creates:                     │
│ 1. Patient Record                   │
│    - ID: HP-2025-0001 (GENERATED)   │
│    - Name: John Doe (STORED)        │
│    - Age: 45 (STORED)               │
│                                     │
│ 2. Case Record                      │
│    - Linked to Patient              │
│    - Stage 1 assessment data        │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ Patient ID displayed:                │
│ HP-2025-0001                        │
│ (Used for Stages 2 & 3)             │
└─────────────────────────────────────┘

LAB SCREENING (Stage 2):
┌─────────────────────────────────────┐
│ Patient ID: HP-2025-0001 (auto)     │
│ Lab results: [...]                  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ System finds existing Patient       │
│ Creates NEW Case (Stage 2)          │
│ Links to SAME Patient               │
└─────────────────────────────────────┘

RIC STAGING (Stage 3):
┌─────────────────────────────────────┐
│ Patient ID: HP-2025-0001 (auto)     │
│ MIC values: [...]                   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ System finds SAME Patient           │
│ Creates NEW Case (Stage 3)          │
│ Creates Prescription                │
│ All linked to ONE Patient           │
└─────────────────────────────────────┘
```

---

## 📊 **CASE HISTORY VIEW**

When you view Case History, you'll see:

```
Date       | Patient ID    | Patient Name | Type      | Stage
2025-01-03 | HP-2025-0001  | John Doe     | Staging   | Stage 3
2025-01-02 | HP-2025-0001  | John Doe     | Screening | Stage 2
2025-01-01 | HP-2025-0001  | John Doe     | Screening | Stage 1
```

**All 3 cases linked to ONE patient: John Doe (HP-2025-0001)**

---

## 🔍 **KEY POINTS**

1. ✅ **Patient ID is auto-generated** (HP-2025-XXXX)
2. ✅ **Patient name is stored** with the ID
3. ✅ **One Patient record** can have **multiple Cases**
4. ✅ **Stage 1** creates the Patient + first Case
5. ✅ **Stages 2 & 3** create new Cases linked to same Patient
6. ✅ **You can search** by Patient ID OR Name
7. ✅ **No data duplication** - Patient info stored once
8. ✅ **All stages connected** through Patient ID

---

## 🎯 **EXAMPLE SCENARIO**

**Day 1 - Morning:**
- Patient walks in: "John Doe"
- Clinician does Stage 1 → System generates HP-2025-0001
- Lab tests ordered

**Day 1 - Afternoon:**
- Lab results ready
- Clinician enters HP-2025-0001 in Stage 2
- System knows it's John Doe (no need to re-enter name)

**Day 2:**
- Genetic test results ready
- Clinician enters HP-2025-0001 in Stage 3
- System knows it's John Doe
- Prescription generated for John Doe

**Result:**
- 1 Patient record (HP-2025-0001 = John Doe)
- 3 Case records (Stage 1, 2, 3)
- All linked together

---

## ✅ **READY TO TEST**

Refresh your browser and:
1. Click "Screening" → Fill Stage 1 → Note the Patient ID generated
2. Click "Lab Screening" → Patient ID auto-filled → Enter results
3. Click "Staging" → Patient ID auto-filled → Complete staging
4. Click "Case History" → See all 3 stages for the same patient

**Everything is saved properly! Patient ID + Name + All data!** 🎉

