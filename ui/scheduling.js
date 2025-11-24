// ========================================
// SCHEDULING SYSTEM JAVASCRIPT
// H. pylori CDSS - Specialist Appointments
// ========================================

let specialists = [];
let appointments = [];

// Get API base URL and auth token
const API_BASE_SCHED = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
    ? 'http://localhost:8000' 
    : '';
const getAuthToken = () => localStorage.getItem('token');

// ========================================
// API REQUEST HELPER
// ========================================
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    if (!token) {
        showToast('Please log in to continue', 'error');
        throw new Error('No authentication token');
    }
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_SCHED}${endpoint}`, {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            showToast('Session expired. Please log in again.', 'error');
            setTimeout(() => window.location.href = 'index.html', 1500);
            throw new Error('Authentication failed');
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || errorData.message || `Request failed: ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
        return response.json();
    } catch (error) {
        if (error.message === 'Authentication failed') {
            throw error;
        }
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showToast('Unable to connect to server. Please check your connection.', 'error');
        }
        throw error;
    }
}

// ========================================
// Initialize Scheduling System
// ========================================
async function initScheduling() {
    console.log('Initializing Scheduling System...');
    
    // Load specialists
    await loadSpecialists();
    
    // Load user's appointments
    await loadAppointments();
    
    // Set minimum date for appointment to now
    const dateInput = document.getElementById('preferredDate');
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.min = now.toISOString().slice(0, 16);
    }
    
    // Load cases for dropdown
    await loadCasesForAppointment();
    
    // Check for preferred doctor from landing page
    const preferredDoctor = sessionStorage.getItem('preferred_doctor');
    if (preferredDoctor) {
        selectPreferredDoctor(preferredDoctor);
        sessionStorage.removeItem('preferred_doctor');
    }
}

// ========================================
// Load Specialists List
// ========================================
async function loadSpecialists() {
    try {
        const response = await apiRequest('/appointments/specialists');
        specialists = response || [];
        
        // Populate specialist select dropdown
        const select = document.getElementById('specialistSelect');
        if (select) {
            select.innerHTML = '<option value="">Select a specialist...</option>';
            specialists.forEach(spec => {
                const option = document.createElement('option');
                option.value = spec.id;
                const displayName = spec.full_name || spec.username;
                const displaySpecialty = spec.specialty || 'Gastroenterology';
                option.textContent = `${displayName} - ${displaySpecialty}`;
                select.appendChild(option);
            });
        }
        
        // Update specialists grid view
        displaySpecialists();
        
    } catch (error) {
        console.error('Error loading specialists:', error);
        showToast('Failed to load specialists', 'error');
    }
}

// ========================================
// Display Specialists Grid
// ========================================
function displaySpecialists() {
    const container = document.getElementById('specialistsList');
    if (!container) return;
    
    if (specialists.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">[Doctor]</div>
                <p class="empty-text">No specialists available at the moment</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = specialists.map(spec => {
        const displayName = spec.full_name || spec.username;
        const displaySpecialty = spec.specialty || 'Gastroenterology';
        const displayInstitution = spec.institution || 'Medical Center';
        const email = spec.email || `${spec.username}@hospital.com`;
        const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        
        return `
        <div class="specialist-card">
            <div class="specialist-avatar user-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
            </div>
            <div class="specialist-name">${displayName}</div>
            <div class="specialist-specialty">${displaySpecialty}</div>
            <div class="specialist-info">${displayInstitution}</div>
            <div class="specialist-info">${email}</div>
            <br>
            <button class="btn btn-primary btn-sm" 
                    onclick="requestAppointmentWithSpecialist(${spec.id})">
                Request Appointment
            </button>
        </div>
    `;
    }).join('');
}

// ========================================
// Load User's Appointments
// ========================================
async function loadAppointments() {
    try {
        const response = await apiRequest('/appointments/my-requests');
        appointments = response || [];
        
        // Separate pending and confirmed
        const pending = appointments.filter(a => a.status === 'pending');
        const confirmed = appointments.filter(a => a.status === 'confirmed');
        
        // Update counts
        document.getElementById('pendingCount').textContent = pending.length;
        document.getElementById('confirmedCount').textContent = confirmed.length;
        
        // Display appointments
        displayPendingAppointments(pending);
        displayConfirmedAppointments(confirmed);
        
    } catch (error) {
        console.error('Error loading appointments:', error);
        showToast('Failed to load appointments', 'error');
    }
}

// ========================================
// Display Pending Appointments
// ========================================
function displayPendingAppointments(pending) {
    const container = document.getElementById('pendingAppointments');
    if (!container) return;
    
    if (pending.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">[Inbox]</div>
                <p class="empty-text">No pending appointments</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = pending.map(apt => `
        <div class="appointment-card">
            <div class="appointment-header">
                <div>
                    <div class="appointment-title">${apt.specialist_name}</div>
                    <small>${apt.specialty}</small>
                </div>
                <span class="appointment-status status-${apt.urgency}">
                    ${apt.urgency.toUpperCase()}
                </span>
            </div>
            
            <div class="appointment-details">
                <div class="detail-item">
                    <span class="detail-icon">[Date]</span>
                    <span class="detail-text">${formatDateTime(apt.preferred_date)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">[Time]</span>
                    <span class="detail-text">Requested ${formatRelativeTime(apt.created_at)}</span>
                </div>
            </div>
            
            <div class="appointment-reason">
                <strong>Reason:</strong> ${apt.reason}
            </div>
            
            ${apt.notes ? `<p><strong>Notes:</strong> ${apt.notes}</p>` : ''}
            
            <div class="appointment-actions">
                <button class="btn btn-secondary btn-sm" onclick="cancelAppointment(${apt.id})">
                    Cancel
                </button>
                <button class="btn btn-secondary btn-sm" onclick="viewAppointmentDetails(${apt.id})">
                    Details
                </button>
            </div>
        </div>
    `).join('');
}

// ========================================
// Display Confirmed Appointments
// ========================================
function displayConfirmedAppointments(confirmed) {
    const container = document.getElementById('confirmedAppointments');
    if (!container) return;
    
    if (confirmed.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">[Check]</div>
                <p class="empty-text">No confirmed appointments yet</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = confirmed.map(apt => `
        <div class="appointment-card">
            <div class="appointment-header">
                <div>
                    <div class="appointment-title">${apt.specialist_name}</div>
                    <small>${apt.specialty}</small>
                </div>
                <span class="appointment-status status-confirmed">
                    CONFIRMED
                </span>
            </div>
            
            <div class="appointment-details">
                <div class="detail-item">
                    <span class="detail-icon">[Date]</span>
                    <span class="detail-text">${formatDateTime(apt.confirmed_date)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">[Clock]</span>
                    <span class="detail-text">${getTimeUntil(apt.confirmed_date)}</span>
                </div>
            </div>
            
            <div class="appointment-reason">
                <strong>Reason:</strong> ${apt.reason}
            </div>
            
            ${apt.specialist_notes ? `<p><strong>Specialist Notes:</strong> ${apt.specialist_notes}</p>` : ''}
            
            ${apt.video_session_url ? generateVideoLinkCard(apt) : ''}
            
            <div class="appointment-actions">
                ${!apt.video_session_url ? `
                    <button class="btn btn-primary btn-sm" onclick="createVideoSession(${apt.id})">
                        Generate Video Link
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="goToVideoConsultation()">
                        Go to Video Consultation
                    </button>
                `}
                <button class="btn btn-secondary btn-sm" onclick="cancelAppointment(${apt.id})">
                    Cancel
                </button>
            </div>
        </div>
    `).join('');
}

// ========================================
// Generate Video Link Card
// ========================================
function generateVideoLinkCard(apt) {
    return `
        <div class="video-link-card">
            <h4>Video Consultation Link</h4>
            <div class="video-link-input">
                <input type="text" 
                       value="${apt.video_session_url}" 
                       id="videoLink${apt.id}" 
                       readonly>
                <button class="btn btn-copy" onclick="copyVideoLink(${apt.id})">
                    Copy
                </button>
            </div>
            <button class="btn btn-primary" onclick="joinVideoSession('${apt.video_session_id}')">
                Join Video Call
            </button>
        </div>
    `;
}

// ========================================
// Switch Scheduling Tabs
// ========================================
function switchSchedulingTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// ========================================
// Submit Appointment Request
// ========================================
async function submitAppointmentRequest(event) {
    event.preventDefault();
    
    const formData = {
        specialist_id: parseInt(document.getElementById('specialistSelect').value),
        case_id: document.getElementById('caseSelect').value || null,
        requested_date: document.getElementById('preferredDate').value,  // Fixed: backend expects 'requested_date'
        duration_minutes: 30,  // Default 30 minutes
        urgency: document.getElementById('urgencyLevel').value,
        reason: document.getElementById('appointmentReason').value,
        clinician_notes: document.getElementById('appointmentNotes').value || null  // Fixed: backend expects 'clinician_notes'
    };
    
    if (!formData.specialist_id) {
        showToast('Please select a specialist', 'error');
        return;
    }
    
    try {
        showToast('Submitting appointment request...', 'info');
        
        const response = await apiRequest('/appointments/request', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        showToast('Appointment requested successfully!', 'success');
        
        // Reset form
        event.target.reset();
        
        // Reload appointments
        await loadAppointments();
        
        // Switch to pending tab
        switchSchedulingTab('pending');
        document.querySelector('.tab-btn:nth-child(2)').classList.add('active');
        document.querySelector('.tab-btn:nth-child(1)').classList.remove('active');
        
    } catch (error) {
        console.error('Error submitting appointment:', error);
        // Properly extract error message
        let errorMessage = 'Failed to submit appointment request';
        
        if (typeof error === 'string') {
            errorMessage = error;
        } else if (error instanceof Error) {
            errorMessage = error.message;
        } else if (error && typeof error === 'object') {
            errorMessage = error.detail || error.message || JSON.stringify(error);
        }
        
        showToast(errorMessage, 'error');
    }
}

// ========================================
// Create Video Session for Appointment
// ========================================
async function createVideoSession(appointmentId) {
    try {
        showToast('Creating video session...', 'info');
        
        const response = await apiRequest('/video/session/create', {
            method: 'POST',
            body: JSON.stringify({
                appointment_id: appointmentId,
                session_name: 'Specialist Consultation'
            })
        });
        
        showToast('Video session created successfully!', 'success');
        
        // Reload appointments to show new video link
        await loadAppointments();
        
    } catch (error) {
        console.error('Error creating video session:', error);
        let errorMessage = 'Failed to create video session';
        if (error instanceof Error) {
            errorMessage = error.message;
        } else if (error && typeof error === 'object') {
            errorMessage = error.detail || error.message || errorMessage;
        }
        showToast(errorMessage, 'error');
    }
}

// ========================================
// Copy Video Link to Clipboard
// ========================================
function copyVideoLink(appointmentId) {
    const input = document.getElementById(`videoLink${appointmentId}`);
    input.select();
    document.execCommand('copy');
    showToast('Video link copied to clipboard!', 'success');
}

// ========================================
// Join Video Session
// ========================================
function joinVideoSession(sessionId) {
    window.open(`video.html?session=${sessionId}`, '_blank');
}

// ========================================
// Cancel Appointment
// ========================================
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }
    
    try {
        await apiRequest(`/appointments/${appointmentId}`, {
            method: 'DELETE'
        });
        
        showToast('Appointment cancelled successfully', 'success');
        await loadAppointments();
        
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        let errorMessage = 'Failed to cancel appointment';
        if (error instanceof Error) {
            errorMessage = error.message;
        } else if (error && typeof error === 'object') {
            errorMessage = error.detail || error.message || errorMessage;
        }
        showToast(errorMessage, 'error');
    }
}

// ========================================
// Request Appointment with Specific Specialist
// ========================================
function requestAppointmentWithSpecialist(specialistId) {
    // Switch to request tab
    document.querySelector('.tab-btn:first-child').click();
    
    // Select the specialist
    document.getElementById('specialistSelect').value = specialistId;
    
    // Scroll to form
    document.getElementById('appointmentRequestForm').scrollIntoView({ behavior: 'smooth' });
}

// ========================================
// TOAST NOTIFICATION SYSTEM
// ========================================
function showToast(message, type = 'info') {
    // Handle object errors properly - THIS FIXES [object Object]
    if (typeof message === 'object' && message !== null) {
        if (message.detail) {
            message = message.detail;
        } else if (message.message) {
            message = message.message;
        } else if (message.error) {
            message = message.error;
        } else {
            try {
                message = JSON.stringify(message);
            } catch (e) {
                message = 'An error occurred';
            }
        }
    }
    
    // Ensure message is a string
    message = String(message);
    
    // Check if toast container exists
    let container = document.getElementById('toastContainer');
    if (!container) {
        // Create container if it doesn't exist
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Icon based on type
    const icons = {
        success: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 20px; height: 20px; flex-shrink: 0;"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd"/></svg>',
        error: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 20px; height: 20px; flex-shrink: 0;"><path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd"/></svg>',
        warning: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 20px; height: 20px; flex-shrink: 0;"><path fill-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd"/></svg>',
        info: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 20px; height: 20px; flex-shrink: 0;"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.706l-.709 2.836.042-.02a.75.75 0 01.67 1.34l-.04.022c-1.147.573-2.438-.463-2.127-1.706l.71-2.836-.042.02a.75.75 0 11-.671-1.34l.041-.022zM12 9a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd"/></svg>'
    };
    
    // Colors for each type
    const colors = {
        success: { bg: '#10b981', text: '#ffffff' },
        error: { bg: '#ef4444', text: '#ffffff' },
        warning: { bg: '#f59e0b', text: '#ffffff' },
        info: { bg: '#3b82f6', text: '#ffffff' }
    };
    
    const color = colors[type] || colors.info;
    
    toast.style.cssText = `
        background: ${color.bg};
        color: ${color.text};
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 300px;
        max-width: 500px;
        animation: slideInRight 0.3s ease;
        font-weight: 500;
        font-size: 14px;
    `;
    
    toast.innerHTML = `${icons[type] || icons.info}<span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Add animations if not already present
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);
}

// ========================================
// Select Preferred Doctor (from landing page)
// ========================================
function selectPreferredDoctor(doctorName) {
    const select = document.getElementById('specialistSelect');
    if (!select) return;
    
    // Find specialist by name
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].textContent.includes(doctorName)) {
            select.selectedIndex = i;
            break;
        }
    }
}

// ========================================
// Load Cases for Appointment Dropdown
// ========================================
async function loadCasesForAppointment() {
    try {
        const response = await apiRequest('/cases?limit=50');
        const cases = response.cases || [];
        
        const select = document.getElementById('caseSelect');
        if (select) {
            select.innerHTML = '<option value="">Select a case...</option>';
            cases.forEach(case_ => {
                const option = document.createElement('option');
                option.value = case_.id;
                option.textContent = `Case #${case_.id} - ${case_.patient_name || 'Unnamed'} (${formatDate(case_.created_at)})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

// ========================================
// View Appointment Details
// ========================================
function viewAppointmentDetails(appointmentId) {
    const apt = appointments.find(a => a.id === appointmentId);
    if (!apt) return;
    
    alert(`
Appointment Details:

Specialist: ${apt.specialist_name}
Specialty: ${apt.specialty}
Date: ${formatDateTime(apt.preferred_date || apt.confirmed_date)}
Status: ${apt.status}
Urgency: ${apt.urgency}

Reason: ${apt.reason}

${apt.notes ? 'Notes: ' + apt.notes : ''}
${apt.specialist_notes ? 'Specialist Notes: ' + apt.specialist_notes : ''}
    `.trim());
}

// ========================================
// Utility Functions
// ========================================

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return formatDate(dateString);
}

function getTimeUntil(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date - now;
    
    if (diffMs < 0) return 'Past appointment';
    
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `In ${diffMins} minutes`;
    if (diffHours < 24) return `In ${diffHours} hours`;
    return `In ${diffDays} days`;
}

// ========================================
// Go to Video Consultation Page
// ========================================
function goToVideoConsultation() {
    // Switch to video consultation page
    const videoNavItem = document.querySelector('[data-page="video"]');
    if (videoNavItem) {
        videoNavItem.click();
    }
}

console.log('Scheduling System JavaScript Loaded!');

