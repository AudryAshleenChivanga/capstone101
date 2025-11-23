# 🖊️ Signature Module Implementation Plan

## Goal:
Add signature capability so specialists can:
1. Sign cases
2. Generate PDFs after signing
3. See visual distinction between signed/unsigned cases

## Files to Modify:

### 1. ui/login.html
- Fix redirect: dashboard_new.html → dashboard.html

### 2. ui/dashboard.html  
- Add signature modal (canvas for drawing)
- Add modal HTML before </body>

### 3. ui/app.js
- Add CRUD buttons with signed/unsigned logic
- Add signature modal functions:
  - openSignatureModal(caseId)
  - closeSignatureModal()
  - clearSignature()
  - saveSignature()
- Add canvas drawing handlers

### 4. Backend (already exists)
- POST /documents/{case_id}/sign
- GET /documents/{case_id}/generate-pdf
- Checks signed_at before allowing PDF

## Implementation Steps:

Step 1: Fix login redirect ✅
Step 2: Add signature modal HTML
Step 3: Add JavaScript functions
Step 4: Update CRUD buttons display
Step 5: Test locally
Step 6: Get your approval
Step 7: Commit and push (only with approval)

Ready to proceed?

