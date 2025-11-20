# END-USER LICENSE AND PRIVACY POLICY AGREEMENT
## H. pylori Clinical Decision Support System (CDSS)

**Effective Date**: January 2025  
**Version**: 1.0  
**Developer**: African Leadership University Capstone Project  
**Supervisor**: Thadee Gatera  
**Institution**: African Leadership University

---

## 1. INTRODUCTION

This End-User License Agreement and Privacy Policy ("Agreement") governs the use of the H. pylori Clinical Decision Support System ("the System", "CDSS", or "Service"). By accessing or using this System, you ("User", "Clinician", "Healthcare Provider") agree to be bound by the terms outlined herein.

**Purpose of System**: 
This System is an AI-powered clinical decision support tool designed to assist healthcare professionals in:
- Screening for H. pylori infection
- Staging antibiotic resistance
- Optimizing biopsy site selection
- Detecting gastric pathologies through capsule endoscopy simulation

**Important Notice**: This System is a DECISION SUPPORT TOOL, not a medical device or diagnostic instrument. All clinical decisions remain the sole responsibility of licensed healthcare professionals.

---

## 2. DATA COLLECTION & USE

### 2.1 Types of Data Collected

The System collects the following categories of data:

**User Data (Healthcare Professionals)**:
- Username and encrypted password
- Email address
- Full name
- Professional role (Admin, Clinician, Specialist)
- Medical specialty
- Institution/Health Facility
- Phone number (optional)

**Patient Data (Clinical Information)**:
- Pseudonymized Patient ID (e.g., HP-2025-0001)
- Demographics: Age, Gender, Weight, Height
- Clinical symptoms (17 symptom types)
- Laboratory test results
- Treatment history
- Appointment records
- Case documentation and clinical notes
- Prescriptions

**System Usage Data**:
- AI prediction logs (model inputs and outputs)
- Timestamp of actions
- IP addresses (for security purposes)
- Session data

### 2.2 Purpose Limitation

Data is collected and processed ONLY for the following purposes:

✅ **Primary Purposes (With User Consent)**:
1. Providing clinical decision support recommendations
2. Managing patient cases and medical records
3. Facilitating telemedicine consultations
4. Generating prescriptions and treatment plans
5. Sending appointment notifications and reminders
6. Monitoring treatment outcomes

✅ **Secondary Purposes (With Explicit Consent)**:
7. Improving AI model accuracy through retraining (using aggregated, de-identified data)
8. Clinical research (using fully anonymized datasets)
9. Public health surveillance (as legally required)
10. Quality assurance and system improvement

❌ **Prohibited Uses**:
- Commercial marketing or advertising
- Sale or rental of data to third parties
- Insurance risk profiling
- Employment decisions
- Any purpose not directly related to healthcare delivery or public health

---

## 3. PRIVACY PROTECTION & DE-IDENTIFICATION

### 3.1 De-identification Strategy

**What is De-identification?**
De-identification is the process of removing or encoding personal information that could be used to identify an individual, while preserving the clinical utility of the data.

**Our Implementation**:

**Level 1: Pseudonymization**
- Each patient receives a unique, non-identifiable code (e.g., HP-2025-0001)
- Real names are encrypted and stored separately from clinical data
- Only authorized clinicians can link pseudonymized IDs to real identities

**Level 2: Data Separation Architecture**
- Patient Identifying Information (PII) is stored in a separate database table
- Clinical data uses ONLY pseudonymized IDs
- Access to PII requires elevated privileges and is logged

**Level 3: Aggregation for Research**
- Research datasets contain NO individual identifiers
- Data is aggregated into groups (e.g., "Males aged 40-50 in Northern Rwanda")
- Statistical disclosure controls prevent re-identification from group statistics

**Re-identification Prevention**:
- Small group sizes (<5 patients) are suppressed in reports
- Quasi-identifiers (age + gender + location combinations) are generalized
- Direct identifiers (name, national ID, exact address, phone) are NEVER included in research datasets

### 3.2 Data Minimization

We collect ONLY the minimum data necessary for clinical decision support. Examples of data we DO NOT collect:
- National ID numbers
- Full home addresses (only general region)
- Financial/insurance information (unless required for billing)
- Employment details
- Family member information (unless medically relevant)
- Religious or political affiliations

---

## 4. USER RIGHTS & DATA CONTROL

### 4.1 Patient Rights (Where Applicable)

Patients have the following rights regarding their data:

**1. Right to Access**
- Patients can request copies of their medical records
- Response time: Within 7 business days
- Format: Digital PDF or paper copy

**2. Right to Rectification**
- Patients can request correction of inaccurate or incomplete data
- Healthcare provider reviews and approves corrections
- Original data is preserved with audit trail

**3. Right to Erasure ("Right to be Forgotten")**
- Patients can request deletion of their data
- **Important Limitation**: Medical data retention laws may override this right
  - Rwanda: Medical records must be retained for 10 years (per health regulations)
  - Anonymized data may be retained for research purposes
- Deletion applies to identifying information; de-identified data may remain

**4. Right to Data Portability**
- Patients can request their data in a machine-readable format (JSON, CSV)
- Facilitates transfer to other healthcare providers

**5. Right to Object**
- Patients can opt out of:
  - Automated decision-making (AI recommendations)
  - Research data use (even anonymized)
  - SMS/Email notifications
- Opting out may limit system functionality

**6. Right to Withdraw Consent**
- Consent can be withdrawn at any time
- Affects future data processing only; past processing remains valid

### 4.2 Healthcare Provider Rights

**1. Right to Professional Autonomy**
- Clinicians can override AI recommendations with documented justification
- No algorithmic coercion; final decisions rest with licensed professionals

**2. Right to Data Access**
- Clinicians can access cases for patients under their care
- Limited to role-based permissions (Clinician vs. Specialist vs. Admin)

**3. Right to Appeal**
- Users can appeal account suspensions or access restrictions
- Appeal process: Email admin@hpylori-cdss.edu.rw within 14 days

---

## 5. DATA SECURITY MEASURES

### 5.1 Technical Safeguards

**Encryption**:
- Data in Transit: TLS 1.3 encryption (HTTPS) for all communications
- Data at Rest: AES-256 encryption for database storage
- Password Security: bcrypt hashing (industry-standard, irreversible)

**Access Controls**:
- Role-Based Access Control (RBAC): Users see only data relevant to their role
- Multi-Factor Authentication (MFA): Optional for enhanced security
- Session Management: Automatic logout after 30 minutes of inactivity

**Network Security**:
- Firewall protection
- DDoS mitigation (via Render Cloud infrastructure)
- Regular security audits and vulnerability scanning

**Audit Trails**:
- Every data access is logged (who, what, when)
- Audit logs retained for 3 years
- Tamper-proof logging (write-only)

### 5.2 Organizational Safeguards

**Staff Training**:
- All users complete privacy and security training
- Annual refresher courses

**Access Limitation**:
- Principle of least privilege: Users have minimum necessary access
- Administrative access requires justification and approval

**Incident Response Plan**:
- Documented procedures for data breaches
- Rapid response team
- User notification within 72 hours of breach detection

### 5.3 Breach Notification

**In the event of a data breach, we will**:
1. Contain and remediate the breach immediately
2. Conduct forensic investigation
3. Notify affected users within **72 hours** via email and system notification
4. Notify regulatory authorities (Rwanda Ministry of Health) as legally required
5. Provide credit monitoring services if financial data is compromised (if applicable)
6. Publish transparent breach report (without compromising security)

**User Responsibilities**:
- Use strong, unique passwords
- Never share login credentials
- Report suspected security incidents immediately
- Log out when using shared computers

---

## 6. THIRD-PARTY DATA SHARING

### 6.1 Sharing with Explicit Consent ONLY

**We share patient data ONLY in these circumstances**:

✅ **With Patient Consent**:
- Referrals to other healthcare providers (for continuity of care)
- Telemedicine consultations with specialists
- Family members (if patient designates emergency contact)

✅ **Legal Obligations (Without Consent)**:
- Court orders or subpoenas
- Public health reporting (e.g., notifiable diseases)
- Child abuse or elder abuse reporting (as legally mandated)

✅ **Research (Anonymized Data Only)**:
- Academic collaborations (with Ethics Review Board approval)
- Public health research
- **Guarantee**: Research data is FULLY anonymized and cannot be traced to individuals

❌ **NEVER Shared**:
- Commercial marketing companies
- Insurance companies (for risk profiling)
- Employers
- Government agencies (except as legally required)
- Third-party app developers without explicit consent

### 6.2 Service Providers

**We use these third-party services**:
- **Render Cloud**: Web hosting and database (USA-based, GDPR-compliant)
- **Twilio**: SMS notifications (configurable, opt-out available)
- **Email service**: Appointment reminders (TBD based on deployment)

**Service Provider Agreements**:
- All third parties sign Data Processing Agreements (DPAs)
- Prohibited from using data for their own purposes
- Subject to same security standards as our primary system

---

## 7. AI-SPECIFIC DISCLOSURES

### 7.1 Nature of AI Recommendations

**Users Must Understand**:

**1. Probabilistic, Not Deterministic**
- AI predictions are probability estimates (e.g., "78% likelihood of H. pylori infection")
- NOT absolute certainty; clinical judgment remains essential

**2. Model Limitations**
- Screening Model: 70.1% accuracy, 84.9% recall, 0.738 AUC-ROC
- Staging Model: 90% accuracy (validated on limited dataset)
- RL Agents: 82-85% performance in simulation (not validated in live clinical settings)

**3. Known Biases**
- Models trained on predominantly African demographic data
- May underperform on populations with significantly different epidemiology
- Age-based performance variations documented in README

**4. Not a Replacement for Clinical Judgment**
- AI augments, does not replace, healthcare professionals
- Licensed clinicians must review and approve all AI recommendations
- System does NOT make autonomous treatment decisions

### 7.2 Prediction Logging & Monitoring

**Transparency Commitment**:
- Every AI prediction is logged with timestamp, model version, input features, and output
- Logs used for quality monitoring, model improvement, and accountability
- Users cannot opt out of prediction logging (essential for safety and auditability)

**Purpose of Logging**:
- Detect model degradation over time
- Enable retraining with improved data
- Investigate adverse events or complaints
- Research and development

**Privacy Protection in Logs**:
- Logs linked to pseudonymized patient IDs, not real names
- Aggregate statistics only for external reporting

### 7.3 Model Updates & Versioning

**Continuous Improvement**:
- AI models may be updated periodically with improved versions
- Users will be notified of major model changes via system announcements
- Model version displayed in system footer (e.g., "Screening Model v1.0.0")

**User Rights Regarding Updates**:
- Users can view model documentation and performance metrics in README
- Users can compare predictions across model versions
- Critical model failures will trigger immediate rollback to previous version

---

## 8. COOKIES & TRACKING TECHNOLOGIES

### 8.1 Cookies Used

**Essential Cookies (Cannot be Disabled)**:
- Session cookies: Maintain login state
- Authentication tokens: Verify user identity (JWT tokens)

**Analytics Cookies (Opt-Out Available)**:
- Usage patterns: Identify popular features, improve UX
- Error tracking: Detect system bugs and failures

**We DO NOT Use**:
- Advertising cookies
- Third-party tracking (e.g., Facebook Pixel, Google Analytics)
- Cross-site tracking

---

## 9. DATA RETENTION & DELETION

### 9.1 Retention Periods

**Active Patient Records**:
- Retained for duration of active treatment + **10 years** (per Rwanda medical record retention laws)

**Inactive Accounts**:
- Healthcare provider accounts: Deactivated after 2 years of inactivity
- Patient data: Retained until legal retention period expires

**Research Data**:
- De-identified datasets: Retained indefinitely for longitudinal studies
- Can be deleted upon written request (if not legally required)

**Audit Logs**:
- Retained for **3 years** (for security investigations and compliance)

### 9.2 Deletion Procedures

**Upon Request for Deletion**:
1. User submits written deletion request via email
2. Identity verification (to prevent malicious deletion)
3. Legal review (ensure no retention obligations)
4. Data deletion within **30 days**
5. Confirmation email sent to user

**Secure Deletion Methods**:
- Database records: Overwritten with random data (3-pass overwrite)
- Backups: Purged from all backup systems
- Logs: Pseudonymized IDs unlinked, making data non-recoverable

**Exceptions**:
- De-identified data used in research may remain (cannot be traced back)
- Audit logs may retain pseudonymized IDs for legal compliance

---

## 10. CHILDREN'S PRIVACY

**Age Restrictions**:
- This System is intended for use by licensed healthcare professionals (18+ years)
- Pediatric patient data may be collected, but consent is obtained from parents/guardians

**Pediatric Data Protection**:
- Additional safeguards for patients under 18
- Parental consent required for treatment documentation
- Special care in de-identification (smaller datasets increase re-identification risk)

---

## 11. INTERNATIONAL DATA TRANSFERS

**Current Deployment**:
- Hosted on Render Cloud (servers in USA or EU, depending on region)
- Rwanda does not currently have data localization requirements

**Data Transfer Safeguards**:
- Standard Contractual Clauses (SCCs) with cloud provider
- GDPR-compliant data processing agreements
- Encryption in transit and at rest

**User Rights**:
- Rwandan users have same rights as EU users under GDPR (principle of best practice)

---

## 12. LIABILITY & DISCLAIMERS

### 12.1 Limitation of Liability

**Developer/Institution Liability**:
- This System is provided "AS IS" without warranties
- We do NOT guarantee:
  - Uninterrupted service (system may have downtime)
  - 100% accuracy of AI predictions
  - Specific patient outcomes

**We ARE NOT LIABLE for**:
- Medical outcomes resulting from use of AI recommendations
- Adverse events if clinicians override AI suggestions appropriately
- Third-party service failures (e.g., Render Cloud outage, Twilio SMS delivery)

**We ARE LIABLE for**:
- Gross negligence or willful misconduct
- Data breaches caused by our security failures
- Violation of privacy laws

### 12.2 Professional Responsibility

**Healthcare Providers Remain Fully Responsible for**:
- Final clinical decisions
- Informed consent from patients
- Compliance with medical standards of care
- Malpractice liability

**AI Recommendations Do NOT**:
- Constitute medical advice
- Create a doctor-patient relationship
- Replace physical examination or clinical judgment

---

## 13. USER CONDUCT & ACCEPTABLE USE

### 13.1 Prohibited Activities

Users MUST NOT:
- Share login credentials with unauthorized individuals
- Access patient data outside their scope of care
- Export data for unauthorized purposes (e.g., commercial sale)
- Attempt to reverse-engineer AI models
- Introduce malware or conduct cyberattacks
- Falsify patient records or predictions
- Use the System for discrimination or harassment

### 13.2 Enforcement

**Violations May Result in**:
- Account suspension or termination
- Legal action (civil or criminal)
- Reporting to professional licensing boards
- Notification to law enforcement

---

## 14. UPDATES TO THIS POLICY

**Right to Modify**:
- We may update this Agreement periodically
- Users will be notified via email and system banner 30 days before changes take effect
- Continued use after changes implies acceptance

**Version Control**:
- All versions archived and accessible
- Current version always available at: https://h-pylori-cdss.onrender.com/privacy-policy

---

## 15. DISPUTE RESOLUTION

**Governing Law**:
- This Agreement is governed by the laws of the Republic of Rwanda
- Disputes resolved in Rwandan courts

**Alternative Dispute Resolution**:
- Mediation preferred before litigation
- Arbitration available upon mutual agreement

---

## 16. CONTACT INFORMATION

**For Privacy Concerns or Data Requests**:
- **Email**: privacy@hpylori-cdss.edu.rw (or supervisor email)
- **Phone**: [To be determined based on institution]
- **Address**: African Leadership University, Kigali, Rwanda

**Response Time**:
- Privacy inquiries: Within 7 business days
- Data deletion requests: Within 30 days
- Security incidents: Immediate response

---

## 17. CONSENT & ACCEPTANCE

**By using this System, you acknowledge that**:
- You have read and understood this Agreement
- You consent to data collection and processing as described
- You agree to use the System ethically and legally
- You understand the limitations of AI recommendations
- You retain full professional responsibility for clinical decisions

**For Healthcare Providers**:
- [ ] I have read and agree to the End-User License Agreement
- [ ] I understand that AI recommendations are decision support, not prescriptions
- [ ] I will obtain informed consent from patients before using the System
- [ ] I will comply with medical ethics and privacy laws

**For Patients (Consent Form Read by Clinician)**:
- [ ] I understand my data will be used for clinical decision support
- [ ] I consent to AI-assisted diagnosis and treatment planning
- [ ] I understand I can withdraw consent or request data deletion
- [ ] I have been informed of my privacy rights

---

## SIGNATURE

**User Name**: ___________________________

**User Role**: [  ] Admin  [  ] Clinician  [  ] Specialist

**Institution**: ___________________________

**Date**: ___________________________

**Signature**: ___________________________

---

**Effective Date**: January 2025  
**Version**: 1.0  
**Last Updated**: January 20, 2025

---

## APPENDIX A: GLOSSARY

**De-identification**: Removal or encoding of personal identifiers from data  
**Pseudonymization**: Replacement of direct identifiers with artificial codes  
**Aggregation**: Combining individual data into group statistics  
**Encryption**: Converting data into unreadable code  
**Audit Trail**: Tamper-proof log of system activities  
**Role-Based Access Control (RBAC)**: Permission system based on user roles  
**Data Processing Agreement (DPA)**: Contract governing third-party data handling  
**Standard Contractual Clauses (SCCs)**: EU-approved data transfer agreements  

---

## APPENDIX B: REGULATORY COMPLIANCE

This System is designed to comply with:
- **Rwanda**: Medical records retention laws, health privacy regulations
- **GDPR** (EU General Data Protection Regulation): Gold standard for privacy
- **HIPAA** (USA Health Insurance Portability and Accountability Act): Principles applied
- **WHO Guidelines**: Ethical use of AI in healthcare

**Note**: As Rwanda develops comprehensive data protection legislation, this System will be updated to ensure full compliance.

---

**END OF DOCUMENT**

