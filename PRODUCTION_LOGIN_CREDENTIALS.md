# 🔐 Production Login Credentials

**H. pylori Clinical Decision Support System**

**Production URL:** https://h-pylori-cdss.onrender.com/

**Login Page:** https://h-pylori-cdss.onrender.com/ui/login.html

---

## 👤 User Accounts

### 1. ADMIN ACCOUNT (Original System Admin)

```
Username: admin
Password: Admin@2024
Email: admin@hpylori.com
Role: admin
Full Name: System Administrator
Specialty: Administration
Institution: H. pylori CDSS
```

**Access Level:** Full system administration
- Manage all users
- View all cases
- System configuration
- Admin panel access

---

### 2. ADMIN ACCOUNT (Your Personal Account)

```
Username: dr_audry
Password: Audry@2024
Email: audry@hospital.com
Role: admin
Full Name: Dr. Audry Chivanga
Specialty: Medical Informatics
Institution: H. pylori CDSS Research
```

**Access Level:** Full system administration
- Manage all users
- View all cases
- System configuration
- Admin panel access

---

### 3. CLINICIAN ACCOUNT

```
Username: clinician1
Password: Clinician@2024
Email: clinician1@hospital.com
Role: clinician
Full Name: Dr. Clinical Staff
Specialty: General Practice
Institution: District Hospital
```

**Access Level:** Standard clinician
- Create and manage cases
- Run screening models
- Run staging models
- Generate prescriptions
- Request specialist consultations
- Schedule appointments

---

### 4. SPECIALIST ACCOUNT

```
Username: specialist1
Password: Specialist@2024
Email: specialist1@hospital.com
Role: specialist
Full Name: Dr. Gastro Specialist
Specialty: Gastroenterology
Institution: Referral Hospital
```

**Access Level:** Specialist clinician
- View referred cases
- Provide specialist consultations
- Access video consultation features
- Review biopsy simulations
- All clinician features

---

## 🧪 Testing Instructions

### Test Clinician Workflow:
1. Login as **clinician1**
2. Create a new patient case
3. Run H. pylori screening
4. Run resistance staging
5. Generate prescription
6. Schedule specialist appointment

### Test Specialist Workflow:
1. Login as **specialist1**
2. View referred cases
3. Review patient history
4. Perform 3D biopsy simulation
5. Provide consultation notes
6. Video consultation (if available)

### Test Admin Features:
1. Login as **admin** or **dr_audry**
2. Access admin panel
3. View all users
4. View system statistics
5. Manage user accounts

---

## 📊 Account Summary Table

| Username     | Password         | Role       | Primary Use Case                |
|--------------|------------------|------------|---------------------------------|
| admin        | Admin@2024       | admin      | System administration           |
| dr_audry     | Audry@2024       | admin      | Your personal admin account     |
| clinician1   | Clinician@2024   | clinician  | Primary care / screening        |
| specialist1  | Specialist@2024  | specialist | Gastroenterology consultation   |

---

## 🔒 Security Notes

- All passwords follow format: `Role@2024`
- JWT token-based authentication
- Session timeout: 24 hours
- HTTPS encryption on all connections
- HIPAA-ready architecture

---

## 🚨 For Presentation Demo

**Recommended Demo Flow:**

1. **Start as Clinician** (`clinician1`)
   - Show patient registration
   - Demonstrate AI screening
   - Show treatment recommendations

2. **Switch to Specialist** (`specialist1`)
   - Show referral workflow
   - Demonstrate 3D biopsy simulation
   - Show RL capsule endoscopy

3. **Show Admin Panel** (`dr_audry`)
   - System statistics
   - User management
   - Overall system health

---

## 📝 Quick Copy-Paste Credentials

**Clinician:**
```
clinician1
Clinician@2024
```

**Specialist:**
```
specialist1
Specialist@2024
```

**Admin (Your Account):**
```
dr_audry
Audry@2024
```

---

## ✅ Verification Status

- [x] All users created in production PostgreSQL
- [x] All users tested and verified working
- [x] JWT authentication functional
- [x] Role-based access control enabled
- [x] Ready for presentation demo

**Last Updated:** November 20, 2024
**Production URL:** https://h-pylori-cdss.onrender.com/
**Status:** ✅ PRODUCTION READY

---

## 🆘 Troubleshooting

**If login fails:**
1. Verify you're on the correct URL (https://h-pylori-cdss.onrender.com/)
2. Clear browser cache and cookies
3. Try in incognito/private mode
4. Check Render service status (should be green)
5. Wake up service by visiting homepage first

**To create additional users:**
Run from your computer:
```bash
python register_users_authenticated.py
```

Or in Render Shell:
```bash
python create_production_users.py
```

---

**Deployment Status:** LIVE ✅
**Repository:** https://github.com/AudryAshleenChivanga/capstone101
**Commits Pushed:** main ✅ | master ✅

