// ========================================
// H. PYLORI CDSS - ENHANCED FEATURES
// Signature Pad, Profile Editor, PDF Preview, Admin Panel
// VERSION 5.0 - PRODUCTION READY
// ========================================

// This file extends app.js with enhanced features
// Include this AFTER app.js in dashboard.html

console.log('%c✅ ENHANCED FEATURES LOADED - VERSION 5.0', 'background: #667eea; color: white; padding: 10px; font-size: 16px; font-weight: bold;');

// ========================================
// SIGNATURE PAD INTEGRATION
// ========================================

let signaturePad = null;
let profileSignaturePad = null;

function initializeSignaturePad(canvasId, clearBtnId, saveBtnId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const pad = new SignaturePad(canvas, {
        backgroundColor: 'rgb(255, 255, 255)',
        penColor: 'rgb(0, 0, 0)',
        minWidth: 1,
        maxWidth: 2.5
    });
    
    // Resize canvas to fit container
    function resizeCanvas() {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext('2d').scale(ratio, ratio);
        pad.clear();
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Clear button
    const clearBtn = document.getElementById(clearBtnId);
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            pad.clear();
            showToast('Signature cleared', 'info');
        });
    }
    
    return pad;
}

// ========================================
// PROFILE EDITOR
// ========================================

async function loadProfileEditor() {
    try {
        const response = await fetch(`${API_BASE}/profile/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load profile');
        
        const profile = await response.json();
        
        // Populate form
        document.getElementById('editFullName').value = profile.full_name || '';
        document.getElementById('editEmail').value = profile.email || '';
        document.getElementById('editPhone').value = profile.phone || '';
        document.getElementById('editSpecialty').value = profile.specialty || '';
        document.getElementById('editLicense').value = profile.license_number || '';
        document.getElementById('editInstitution').value = profile.institution || '';
        document.getElementById('editBio').value = profile.bio || '';
        
        // Show existing signature if available
        if (profile.digital_signature) {
            const signaturePreview = document.getElementById('signaturePreview');
            signaturePreview.innerHTML = `
                <img src="${profile.digital_signature}" alt="Current Signature" style="max-width: 100%; border: 1px solid #ddd; padding: 10px; background: white;">
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Current signature on file</p>
            `;
        }
        
        // Initialize signature pad for profile
        setTimeout(() => {
            profileSignaturePad = initializeSignaturePad('profileSignatureCanvas', 'clearProfileSignature', null);
        }, 100);
        
    } catch (error) {
        console.error('Error loading profile:', error);
        showToast('Failed to load profile', 'error');
    }
}

async function saveProfile() {
    const profileData = {
        full_name: document.getElementById('editFullName').value,
        phone: document.getElementById('editPhone').value,
        specialty: document.getElementById('editSpecialty').value,
        license_number: document.getElementById('editLicense').value,
        institution: document.getElementById('editInstitution').value,
        bio: document.getElementById('editBio').value
    };
    
    try {
        // Save profile data
        const response = await fetch(`${API_BASE}/profile/me`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        if (!response.ok) throw new Error('Failed to update profile');
        
        // Save signature if drawn
        if (profileSignaturePad && !profileSignaturePad.isEmpty()) {
            const signatureData = profileSignaturePad.toDataURL('image/png');
            
            const sigResponse = await fetch(`${API_BASE}/profile/signature`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ signature_data: signatureData })
            });
            
            if (!sigResponse.ok) throw new Error('Failed to save signature');
        }
        
        showToast('Profile updated successfully!', 'success');
        loadUserData(); // Refresh user data in header
        
    } catch (error) {
        console.error('Error saving profile:', error);
        showToast('Failed to save profile', 'error');
    }
}

// ========================================
// PDF PREVIEW MODAL
// ========================================

async function previewCasePDF(caseId) {
    try {
        // Show loading
        const modal = document.getElementById('pdfPreviewModal');
        const previewContent = document.getElementById('pdfPreviewContent');
        previewContent.innerHTML = '<div class="loading-spinner">Generating PDF preview...</div>';
        modal.style.display = 'flex';
        
        // Get case document
        const response = await fetch(`${API_BASE}/documents/${caseId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load document');
        
        const docData = await response.json();
        
        // Generate HTML preview
        const previewHTML = generatePDFPreviewHTML(docData);
        previewContent.innerHTML = previewHTML;
        
    } catch (error) {
        console.error('Error previewing PDF:', error);
        showToast('Failed to preview PDF', 'error');
        closePDFPreviewModal();
    }
}

function generatePDFPreviewHTML(docData) {
    const recommendations = docData.recommendations || [];
    const editedRecommendations = docData.edited_recommendations || docData.recommendations || [];
    
    return `
        <div class="pdf-preview-page">
            <div class="pdf-header">
                <h1>H. pylori Clinical Decision Support Report</h1>
                <p class="institution">${currentUser?.institution || 'Medical Institution'}</p>
            </div>
            
            <div class="pdf-section">
                <h2>Patient Information</h2>
                <table class="pdf-info-table">
                    <tr>
                        <td><strong>Patient Name:</strong></td>
                        <td>${docData.patient_name || 'Not specified'}</td>
                    </tr>
                    <tr>
                        <td><strong>Case ID:</strong></td>
                        <td>#${docData.case_id}</td>
                    </tr>
                    <tr>
                        <td><strong>Date:</strong></td>
                        <td>${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</td>
                    </tr>
                </table>
            </div>
            
            <div class="pdf-section">
                <h2>Clinical Assessment</h2>
                <div class="assessment-results">
                    ${docData.screen_prob ? `
                        <div class="result-item">
                            <span class="label">Screening Probability:</span>
                            <span class="value">${(docData.screen_prob * 100).toFixed(1)}%</span>
                        </div>
                    ` : ''}
                    ${docData.stage_pred ? `
                        <div class="result-item">
                            <span class="label">Resistance Stage:</span>
                            <span class="value stage-${docData.stage_pred}">${docData.stage_pred.toUpperCase()}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            <div class="pdf-section">
                <h2>Clinical Recommendations</h2>
                <ol class="recommendations-list">
                    ${editedRecommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ol>
                ${recommendations.length !== editedRecommendations.length ? `
                    <p class="note"><em>Note: Recommendations have been clinically reviewed and modified</em></p>
                ` : ''}
            </div>
            
            <div class="pdf-section">
                <h2>Clinician Information</h2>
                <table class="pdf-info-table">
                    <tr>
                        <td><strong>Clinician:</strong></td>
                        <td>${docData.signed_by || currentUser?.full_name || currentUser?.username}</td>
                    </tr>
                    ${currentUser?.license_number ? `
                    <tr>
                        <td><strong>License Number:</strong></td>
                        <td>${currentUser.license_number}</td>
                    </tr>
                    ` : ''}
                    ${docData.signed_at ? `
                    <tr>
                        <td><strong>Signed:</strong></td>
                        <td>${new Date(docData.signed_at).toLocaleString()}</td>
                    </tr>
                    ` : ''}
                </table>
                ${docData.signature_data ? `
                    <div class="signature-container">
                        <img src="${docData.signature_data}" alt="Signature" class="signature-image">
                    </div>
                ` : ''}
            </div>
            
            <div class="pdf-footer">
                <p class="disclaimer">
                    <strong>Disclaimer:</strong> This is a clinical decision support tool. 
                    Final treatment decisions remain with the attending physician. 
                    This report is confidential and intended for medical use only.
                </p>
            </div>
        </div>
    `;
}

function closePDFPreviewModal() {
    const modal = document.getElementById('pdfPreviewModal');
    modal.style.display = 'none';
}

async function downloadPDF(caseId) {
    try {
        showToast('Generating PDF...', 'info');
        
        // In a real implementation, this would call a backend endpoint
        // that generates and returns a PDF file
        const response = await fetch(`${API_BASE}/documents/${caseId}/generate-pdf`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to generate PDF');
        
        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `case-${caseId}-report.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('PDF downloaded successfully', 'success');
        
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showToast('PDF download not yet implemented - preview available', 'warning');
    }
}

// ========================================
// ADMIN PANEL
// ========================================

async function loadAdminPanel() {
    if (currentUser?.role !== 'admin') {
        showToast('Access denied: Admin privileges required', 'error');
        return;
    }
    
    try {
        // Load all users
        const response = await fetch(`${API_BASE}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load users');
        
        const users = await response.json();
        displayAdminUsers(users);
        
        // Load system statistics
        loadSystemStatistics();
        
    } catch (error) {
        console.error('Error loading admin panel:', error);
        showToast('Failed to load admin panel', 'error');
    }
}

function displayAdminUsers(users) {
    const tbody = document.getElementById('adminUsersTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>
                <div class="user-cell">
                    <img src="${user.profile_photo || '/images/Dr_Angie.webp'}" alt="${user.username}" class="user-avatar-small">
                    <div>
                        <div class="user-name">${user.full_name || user.username}</div>
                        <div class="user-email">${user.email}</div>
                    </div>
                </div>
            </td>
            <td><span class="badge badge-${user.role}">${user.role}</span></td>
            <td>${user.specialty || '-'}</td>
            <td>${user.institution || '-'}</td>
            <td><span class="status-badge ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn-icon" onclick="editAdminUser(${user.id})" title="Edit">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="btn-icon" onclick="toggleUserStatus(${user.id}, ${user.is_active})" title="${user.is_active ? 'Deactivate' : 'Activate'}">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
                ${user.id !== currentUser.id ? `
                <button class="btn-icon danger" onclick="confirmDeleteUser(${user.id})" title="Delete">
                    <svg viewBox="0 0 24 24" width="16" height="16"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

async function loadSystemStatistics() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load statistics');
        
        const stats = await response.json();
        
        // Update statistics cards
        document.getElementById('adminTotalUsers').textContent = stats.total_users || 0;
        document.getElementById('adminActiveUsers').textContent = stats.active_users || 0;
        document.getElementById('adminTotalCases').textContent = stats.total_cases || 0;
        document.getElementById('adminMonthCases').textContent = stats.cases_this_month || 0;
        
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function openCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.style.display = 'flex';
    document.getElementById('createUserForm').reset();
}

function closeCreateUserModal() {
    const modal = document.getElementById('createUserModal');
    modal.style.display = 'none';
}

async function createNewUser(event) {
    event.preventDefault();
    
    const userData = {
        username: document.getElementById('newUsername').value,
        email: document.getElementById('newEmail').value,
        password: document.getElementById('newPassword').value,
        role: document.getElementById('newRole').value,
        full_name: document.getElementById('newFullName').value,
        specialty: document.getElementById('newSpecialty').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create user');
        }
        
        showToast('User created successfully', 'success');
        closeCreateUserModal();
        loadAdminPanel(); // Refresh user list
        
    } catch (error) {
        console.error('Error creating user:', error);
        showToast(error.message, 'error');
    }
}

async function toggleUserStatus(userId, currentStatus) {
    try {
        const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_active: currentStatus ? 0 : 1 })
        });
        
        if (!response.ok) throw new Error('Failed to update user status');
        
        showToast(`User ${currentStatus ? 'deactivated' : 'activated'} successfully`, 'success');
        loadAdminPanel(); // Refresh user list
        
    } catch (error) {
        console.error('Error updating user status:', error);
        showToast('Failed to update user status', 'error');
    }
}

function confirmDeleteUser(userId) {
    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        deleteUser(userId);
    }
}

async function deleteUser(userId) {
    try {
        const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to delete user');
        
        showToast('User deleted successfully', 'success');
        loadAdminPanel(); // Refresh user list
        
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Failed to delete user', 'error');
    }
}

// ========================================
// ENHANCED ERROR HANDLING
// ========================================

// Global error handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'error');
});

// Enhanced API error handling
async function handleAPIError(response) {
    let errorMessage = 'An error occurred';
    
    try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.error || errorMessage;
        
        // Handle specific error codes
        switch (response.status) {
            case 401:
                errorMessage = 'Session expired. Please login again.';
                setTimeout(() => {
                    localStorage.removeItem('token');
                    window.location.href = 'index.html';
                }, 2000);
                break;
            case 403:
                errorMessage = 'Access denied. Insufficient permissions.';
                break;
            case 404:
                errorMessage = 'Resource not found.';
                break;
            case 422:
                // Validation errors
                if (errorData.detail && Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map(e => e.msg).join(', ');
                }
                break;
            case 500:
                errorMessage = 'Server error. Please try again later.';
                break;
        }
    } catch (e) {
        // If error response is not JSON
        errorMessage = `Error: ${response.statusText}`;
    }
    
    showToast(errorMessage, 'error');
    return errorMessage;
}

// Enhanced toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} toast-enter`;
    
    const icons = {
        success: '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>',
        error: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('toast-show'), 10);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('input-error');
            isValid = false;
        } else {
            input.classList.remove('input-error');
        }
    });
    
    if (!isValid) {
        showToast('Please fill in all required fields', 'warning');
    }
    
    return isValid;
}

// ========================================
// DOCUMENT WORKFLOW WITH SIGNATURE
// ========================================

async function prepareDocument(caseId) {
    const patientName = prompt('Enter patient name:');
    const patientPhone = prompt('Enter patient phone number:');
    
    if (!patientName || !patientPhone) {
        showToast('Patient information is required', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/${caseId}/prepare`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                patient_name: patientName,
                patient_phone: patientPhone
            })
        });
        
        if (!response.ok) throw new Error('Failed to prepare document');
        
        const result = await response.json();
        showToast('Document prepared. You can now edit and sign it.', 'success');
        
        // Open signature modal
        openSignatureModal(caseId);
        
    } catch (error) {
        console.error('Error preparing document:', error);
        showToast('Failed to prepare document', 'error');
    }
}

function openSignatureModal(caseId) {
    currentCaseId = caseId;
    const modal = document.getElementById('signatureModal');
    modal.style.display = 'flex';
    
    // Initialize signature pad
    setTimeout(() => {
        signaturePad = initializeSignaturePad('signatureCanvas', 'clearSignature', null);
    }, 100);
}

function closeSignatureModal() {
    const modal = document.getElementById('signatureModal');
    modal.style.display = 'none';
    if (signaturePad) {
        signaturePad.clear();
    }
}

async function saveSignature() {
    if (!signaturePad || signaturePad.isEmpty()) {
        showToast('Please provide a signature', 'warning');
        return;
    }
    
    const signatureData = signaturePad.toDataURL('image/png');
    
    try {
        const response = await fetch(`${API_BASE}/documents/${currentCaseId}/sign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ signature_data: signatureData })
        });
        
        if (!response.ok) throw new Error('Failed to sign document');
        
        const result = await response.json();
        showToast('Document signed successfully!', 'success');
        closeSignatureModal();
        
        // Ask if user wants to send to patient
        if (confirm('Document signed! Would you like to send it to the patient via SMS?')) {
            sendDocumentSMS(currentCaseId);
        }
        
    } catch (error) {
        console.error('Error signing document:', error);
        showToast('Failed to sign document', 'error');
    }
}

async function sendDocumentSMS(caseId) {
    try {
        const response = await fetch(`${API_BASE}/documents/${caseId}/send-sms`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to send SMS');
        
        const result = await response.json();
        showToast('SMS sent successfully to patient!', 'success');
        
    } catch (error) {
        console.error('Error sending SMS:', error);
        showToast(error.message || 'Failed to send SMS', 'error');
    }
}

// ========================================
// INITIALIZATION
// ========================================

// Extend the initialization when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners for new features
    const profileSaveBtn = document.getElementById('saveProfileBtn');
    if (profileSaveBtn) {
        profileSaveBtn.addEventListener('click', saveProfile);
    }
    
    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
        createUserForm.addEventListener('submit', createNewUser);
    }
});

console.log('✅ Enhanced features initialized: Signature Pad, Profile Editor, PDF Preview, Admin Panel');

