// Teleconsultation Booking System
const API_BASE = '';
let currentUser = null;
let specialists = [];
let selectedSpecialist = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeAuth();
    setupEventListeners();
    loadCurrentUser();
});

function initializeAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/ui/index.html';
        return;
    }
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            
            // Show pending requests tab for specialists
            if (currentUser.role === 'specialist') {
                document.getElementById('pendingTab').style.display = 'block';
            }
            
            // Load initial data
            loadSpecialists();
        } else {
            showToast('Failed to load user information', 'error');
            window.location.href = '/ui/index.html';
        }
    } catch (error) {
        console.error('Auth error:', error);
        window.location.href = '/ui/index.html';
    }
}

function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Modal
    document.getElementById('closeModal').addEventListener('click', closeBookingModal);
    document.getElementById('cancelBooking').addEventListener('click', closeBookingModal);
    document.getElementById('bookingModal').addEventListener('click', (e) => {
        if (e.target.id === 'bookingModal') closeBookingModal();
    });

    // Form submission
    document.getElementById('bookingForm').addEventListener('submit', handleBookingSubmit);
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Load data for the tab
    switch (tabName) {
        case 'book':
            loadSpecialists();
            break;
        case 'my-requests':
            loadMyRequests();
            break;
        case 'pending':
            loadPendingRequests();
            break;
        case 'appointments':
            loadMyAppointments();
            break;
    }
}

// Load Specialists
async function loadSpecialists() {
    const grid = document.getElementById('specialistsGrid');
    const loading = document.getElementById('loadingSpecialists');
    const empty = document.getElementById('noSpecialists');

    loading.style.display = 'block';
    grid.style.display = 'none';
    empty.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/appointments/specialists?specialty=gastroenterology`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            specialists = await response.json();
            loading.style.display = 'none';

            if (specialists.length === 0) {
                empty.style.display = 'block';
            } else {
                grid.style.display = 'grid';
                renderSpecialists(specialists);
            }
        } else {
            throw new Error('Failed to load specialists');
        }
    } catch (error) {
        console.error('Error loading specialists:', error);
        loading.style.display = 'none';
        empty.style.display = 'block';
        showToast('Failed to load specialists', 'error');
    }
}

function renderSpecialists(specialists) {
    const grid = document.getElementById('specialistsGrid');
    grid.innerHTML = specialists.map(specialist => `
        <div class="specialist-card" onclick="openBookingModal(${specialist.id})">
            <div class="specialist-header">
                <div class="specialist-avatar user-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                </div>
                <div class="specialist-info">
                    <h3>${specialist.full_name || specialist.username}</h3>
                    <div class="specialist-specialty">${specialist.specialty || 'Gastroenterology'}</div>
                </div>
            </div>
            <div class="specialist-details">
                ${specialist.institution ? `
                    <div class="detail-row">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                        <span>${specialist.institution}</span>
                    </div>
                ` : ''}
                <div class="detail-row">
                    <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span>Available for Consultation</span>
                </div>
            </div>
            <button class="book-btn">Book Consultation</button>
        </div>
    `).join('');
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

// Booking Modal
async function openBookingModal(specialistId) {
    selectedSpecialist = specialists.find(s => s.id === specialistId);
    if (!selectedSpecialist) return;

    document.getElementById('selectedSpecialistId').value = specialistId;
    document.getElementById('selectedSpecialistName').value = 
        selectedSpecialist.full_name || selectedSpecialist.username;

    // Load user's cases
    await loadCasesForBooking();

    // Set default date/time (tomorrow at 10 AM)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0, 0);
    document.getElementById('requestedDate').value = formatDateTimeLocal(tomorrow);

    document.getElementById('bookingModal').classList.add('active');
}

function closeBookingModal() {
    document.getElementById('bookingModal').classList.remove('active');
    document.getElementById('bookingForm').reset();
}

async function loadCasesForBooking() {
    try {
        const response = await fetch(`${API_BASE}/cases?limit=100`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const cases = await response.json();
            const caseSelect = document.getElementById('caseSelect');
            caseSelect.innerHTML = '<option value="">Select a case...</option>' + 
                cases.map(c => `
                    <option value="${c.id}">
                        ${c.patient_name || c.patient_pseudo_id || `Case #${c.id}`} - 
                        ${new Date(c.created_at).toLocaleDateString()}
                    </option>
                `).join('');
        }
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

async function handleBookingSubmit(e) {
    e.preventDefault();

    const requestData = {
        specialist_id: parseInt(document.getElementById('selectedSpecialistId').value),
        case_id: document.getElementById('caseSelect').value ? 
            parseInt(document.getElementById('caseSelect').value) : null,
        requested_date: new Date(document.getElementById('requestedDate').value).toISOString(),
        duration_minutes: parseInt(document.getElementById('duration').value),
        reason: document.getElementById('reason').value.trim(),
        clinician_notes: document.getElementById('clinicianNotes').value.trim() || null
    };

    try {
        const response = await fetch(`${API_BASE}/appointments/request`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (response.ok) {
            const appointment = await response.json();
            showToast('Consultation request sent successfully!', 'success');
            closeBookingModal();
            switchTab('my-requests');
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to create consultation request', 'error');
        }
    } catch (error) {
        console.error('Error creating appointment:', error);
        showToast('Failed to send consultation request', 'error');
    }
}

// Load My Requests
async function loadMyRequests() {
    const list = document.getElementById('requestsList');
    const loading = document.getElementById('loadingRequests');
    const empty = document.getElementById('noRequests');

    loading.style.display = 'block';
    list.style.display = 'none';
    empty.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/appointments/my-requests`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const appointments = await response.json();
            loading.style.display = 'none';

            if (appointments.length === 0) {
                empty.style.display = 'block';
            } else {
                list.style.display = 'flex';
                renderAppointments(appointments, list, true);
            }
        } else {
            throw new Error('Failed to load requests');
        }
    } catch (error) {
        console.error('Error loading requests:', error);
        loading.style.display = 'none';
        empty.style.display = 'block';
        showToast('Failed to load your requests', 'error');
    }
}

// Load Pending Requests (for specialists)
async function loadPendingRequests() {
    const list = document.getElementById('pendingList');
    const loading = document.getElementById('loadingPending');
    const empty = document.getElementById('noPending');

    loading.style.display = 'block';
    list.style.display = 'none';
    empty.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/appointments/pending-requests`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const appointments = await response.json();
            loading.style.display = 'none';

            if (appointments.length === 0) {
                empty.style.display = 'block';
            } else {
                list.style.display = 'flex';
                renderAppointments(appointments, list, false, true);
            }
        } else {
            throw new Error('Failed to load pending requests');
        }
    } catch (error) {
        console.error('Error loading pending requests:', error);
        loading.style.display = 'none';
        empty.style.display = 'block';
        showToast('Failed to load pending requests', 'error');
    }
}

// Load My Appointments
async function loadMyAppointments() {
    const list = document.getElementById('appointmentsList');
    const loading = document.getElementById('loadingAppointments');
    const empty = document.getElementById('noAppointments');

    loading.style.display = 'block';
    list.style.display = 'none';
    empty.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/appointments/my-appointments`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const appointments = await response.json();
            loading.style.display = 'none';

            if (appointments.length === 0) {
                empty.style.display = 'block';
            } else {
                list.style.display = 'flex';
                renderAppointments(appointments, list);
            }
        } else {
            throw new Error('Failed to load appointments');
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
        loading.style.display = 'none';
        empty.style.display = 'block';
        showToast('Failed to load appointments', 'error');
    }
}

// Render Appointments
function renderAppointments(appointments, container, isMyRequests = false, isPending = false) {
    container.innerHTML = appointments.map(apt => {
        const date = apt.scheduled_date || apt.requested_date;
        const dateStr = new Date(date).toLocaleString();
        const isUpcoming = new Date(date) > new Date();
        const canStartVideo = apt.status === 'accepted' && isUpcoming;

        return `
            <div class="appointment-card">
                <div class="appointment-header">
                    <div>
                        <h3>${isMyRequests ? apt.specialist_name : apt.clinician_name}</h3>
                        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
                            ${isMyRequests ? 'Gastroenterologist' : 'Requesting Clinician'}
                        </p>
                    </div>
                    <span class="appointment-status status-${apt.status}">${apt.status}</span>
                </div>

                <div class="appointment-details">
                    <div class="detail-item">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">${dateStr}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Duration:</span>
                        <span class="detail-value">${apt.duration_minutes} minutes</span>
                    </div>
                    ${apt.reason ? `
                        <div class="detail-item" style="grid-column: 1 / -1;">
                            <span class="detail-label">Reason:</span>
                            <span class="detail-value">${apt.reason}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="appointment-actions">
                    ${isPending ? `
                        <button class="action-btn btn-success" onclick="respondToAppointment(${apt.id}, 'accepted')">
                            Accept
                        </button>
                        <button class="action-btn btn-danger" onclick="respondToAppointment(${apt.id}, 'rejected')">
                            Reject
                        </button>
                    ` : ''}
                    
                    ${canStartVideo ? `
                        <button class="action-btn btn-primary" onclick="startVideoSession(${apt.id})">
                            Start Video Session
                        </button>
                    ` : ''}
                    
                    ${apt.status === 'pending' && isMyRequests ? `
                        <button class="action-btn btn-secondary" onclick="cancelAppointment(${apt.id})">
                            Cancel
                        </button>
                    ` : ''}
                    
                    ${apt.status === 'accepted' && !canStartVideo ? `
                        <button class="action-btn btn-secondary" onclick="completeAppointment(${apt.id})">
                            Mark Complete
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Respond to Appointment (for specialists)
async function respondToAppointment(appointmentId, status) {
    const responseData = {
        status: status,
        scheduled_date: null,
        specialist_notes: null
    };

    // If accepting, could prompt for schedule confirmation
    if (status === 'accepted') {
        // For now, use the requested date
        // In a full implementation, you'd show a date picker
    }

    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}/respond`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(responseData)
        });

        if (response.ok) {
            showToast(`Appointment ${status} successfully!`, 'success');
            loadPendingRequests();
            loadMyAppointments();
        } else {
            const error = await response.json();
            showToast(error.detail || `Failed to ${status} appointment`, 'error');
        }
    } catch (error) {
        console.error('Error responding to appointment:', error);
        showToast('Failed to respond to appointment', 'error');
    }
}

// Cancel Appointment
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            showToast('Appointment cancelled successfully', 'success');
            loadMyRequests();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to cancel appointment', 'error');
        }
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        showToast('Failed to cancel appointment', 'error');
    }
}

// Complete Appointment
async function completeAppointment(appointmentId) {
    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}/complete`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            showToast('Appointment marked as completed', 'success');
            loadMyAppointments();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to complete appointment', 'error');
        }
    } catch (error) {
        console.error('Error completing appointment:', error);
        showToast('Failed to complete appointment', 'error');
    }
}

// Start Video Session
function startVideoSession(appointmentId) {
    // Redirect to video consultation page
    window.location.href = `/ui/video.html?appointment_id=${appointmentId}`;
}

// Utility Functions
function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toast.className = `toast toast-${type}`;
    toastMessage.textContent = message;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

