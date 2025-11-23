// ========================================
// VIDEO CONSULTATION & APPOINTMENT BOOKING
// H. pylori CDSS
// ========================================

// Initialize Video Consultation Page
async function initVideoConsultation() {
    console.log('Initializing Video Consultation...');
    
    // Load common data
    await loadSpecialistsForBooking();
    await loadMyAppointmentRequests();
    await loadUpcomingAppointments();
    
    // If user is specialist, show pending requests tab
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            if (user.role === 'specialist') {
                const pendingTab = document.getElementById('pendingTab');
                if (pendingTab) {
                    pendingTab.style.display = 'block';
                }
                await loadPendingRequests();
            }
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
}

// Switch between tabs
function switchConsultTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.consult-tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.consult-tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// Load specialists for booking
async function loadSpecialistsForBooking() {
    try {
        const response = await apiRequest('/appointments/specialists');
        const specialists = response || [];
        
        const grid = document.getElementById('specialists-booking-grid');
        
        if (specialists.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">[Doctor]</div>
                    <p>No specialists available at the moment</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = specialists.map(specialist => {
            // Get display name (full_name or username)
            const displayName = specialist.full_name || specialist.username;
            
            // Get initials for avatar
            const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
            
            // Generate email from username if not provided
            const email = specialist.email || `${specialist.username}@hospital.com`;
            
            return `
            <div class="specialist-booking-card">
                <div class="specialist-avatar user-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                </div>
                <div class="specialist-info">
                    <h3>${displayName}</h3>
                    <div class="specialist-specialty">${specialist.specialty || 'Gastroenterology'}</div>
                    <div class="specialist-hospital">${specialist.institution || 'Medical Center'}</div>
                    
                    <div class="specialist-contact">
                        <div class="contact-item">
                            <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                <polyline points="22,6 12,13 2,6"/>
                            </svg>
                            <span>${email}</span>
                        </div>
                        <div class="contact-item">
                            <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                            </svg>
                            <span>+1 (555) 123-4567</span>
                        </div>
                    </div>
                    
                    <button class="btn-book-appointment" onclick="openBookingModal(${specialist.id}, '${displayName.replace("'", "\\'")}')">
                        Book Appointment
                    </button>
                </div>
            </div>
        `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading specialists:', error);
        document.getElementById('specialists-booking-grid').innerHTML = `
            <div class="error-state">
                <p>Failed to load specialists. Please try again.</p>
            </div>
        `;
    }
}

// Open booking modal
function openBookingModal(specialistId, specialistName) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content booking-modal">
            <div class="modal-header">
                <h2>Book Appointment with ${specialistName}</h2>
                <button class="close-modal" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="bookingForm" onsubmit="submitBooking(event, ${specialistId})">
                    <div class="form-group">
                        <label>Preferred Date & Time *</label>
                        <input type="datetime-local" id="appointmentDateTime" required min="${new Date().toISOString().slice(0, 16)}">
                    </div>
                    
                    <div class="form-group">
                        <label>Related Case (Optional)</label>
                        <select id="relatedCase">
                            <option value="">Select a case...</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Urgency Level *</label>
                        <select id="urgencyLevel" required>
                            <option value="normal">Normal</option>
                            <option value="urgent">Urgent</option>
                            <option value="emergency">Emergency</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Reason for Consultation *</label>
                        <textarea id="consultationReason" rows="4" placeholder="Describe the reason for this appointment..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Additional Notes</label>
                        <textarea id="additionalNotes" rows="3" placeholder="Any special requirements or additional information..."></textarea>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Request Appointment</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Load cases for dropdown
    loadCasesForBooking();
}

// Load cases for booking dropdown
async function loadCasesForBooking() {
    try {
        const response = await apiRequest('/cases');
        const cases = response.cases || [];
        
        const select = document.getElementById('relatedCase');
        if (select && cases.length > 0) {
            select.innerHTML = '<option value="">Select a case...</option>' + 
                cases.map(c => `<option value="${c.id}">Case #${c.id} - ${c.patient_pseudo_id || 'Patient'}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

// Submit booking
async function submitBooking(event, specialistId) {
    event.preventDefault();
    
    const formData = {
        specialist_id: specialistId,
        requested_date: document.getElementById('appointmentDateTime').value,
        case_id: document.getElementById('relatedCase').value || null,
        duration_minutes: 30,  // Default 30 minutes
        reason: document.getElementById('consultationReason').value,
        clinician_notes: document.getElementById('additionalNotes').value
    };
    
    try {
        const response = await apiRequest('/appointments/request', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        showToast('Appointment request submitted successfully!', 'success');
        document.querySelector('.modal-overlay').remove();
        
        // Reload appointments
        await loadMyAppointmentRequests();
        
    } catch (error) {
        console.error('Error submitting booking:', error);
        showToast('Failed to submit appointment request: ' + error.message, 'error');
    }
}

// Load my appointment requests
async function loadMyAppointmentRequests() {
    try {
        const response = await apiRequest('/appointments/my-requests');
        const requests = response || [];
        
        const container = document.getElementById('my-requests-list');
        
        if (requests.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">[List]</div>
                    <p>No appointment requests yet</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = requests.map(apt => `
            <div class="appointment-card status-${apt.status}">
                <div class="apt-header">
                    <div class="apt-specialist">
                        <strong>${apt.specialist_name}</strong>
                        <span class="apt-specialty">${apt.specialist_specialty}</span>
                    </div>
                    <span class="apt-status status-${apt.status}">${apt.status}</span>
                </div>
                <div class="apt-details">
                    <div class="apt-detail-item">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        <span>${new Date(apt.preferred_date).toLocaleString()}</span>
                    </div>
                    <div class="apt-detail-item">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <span>Urgency: ${apt.urgency}</span>
                    </div>
                </div>
                <div class="apt-reason">
                    <strong>Reason:</strong> ${apt.reason}
                </div>
                ${apt.status === 'pending' ? `
                    <div class="apt-actions">
                        <button class="btn btn-sm btn-danger" onclick="cancelAppointment(${apt.id})">Cancel Request</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading appointment requests:', error);
    }
}

// Load upcoming appointments
async function loadUpcomingAppointments() {
    try {
        const response = await apiRequest('/appointments/my-appointments');
        const upcoming = response || [];
        
        const container = document.getElementById('upcoming-appointments-list');
        
        if (upcoming.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <p>No upcoming appointments</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = upcoming.map(apt => {
            const appointmentDate = apt.scheduled_date || apt.requested_date;
            const isAccepted = apt.status === 'accepted';
            const displayName = apt.specialist_name || apt.clinician_name;
            const displaySpecialty = apt.specialist_specialty || 'Consultation';
            
            return `
                <div class="appointment-card confirmed">
                    <div class="apt-header">
                        <div class="apt-specialist">
                            <strong>${displayName}</strong>
                            <span class="apt-specialty">${displaySpecialty}</span>
                        </div>
                        <span class="apt-status status-${apt.status}">${apt.status}</span>
                    </div>
                    <div class="apt-details">
                        <div class="apt-detail-item">
                            <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                                <line x1="16" y1="2" x2="16" y2="6"/>
                                <line x1="8" y1="2" x2="8" y2="6"/>
                                <line x1="3" y1="10" x2="21" y2="10"/>
                            </svg>
                            <span>${new Date(appointmentDate).toLocaleString()}</span>
                        </div>
                        <div class="apt-detail-item">
                            <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12 6 12 12 16 14"/>
                            </svg>
                            <span>Duration: ${apt.duration_minutes || 30} minutes</span>
                        </div>
                    </div>
                    ${apt.reason ? `<div class="apt-reason"><strong>Reason:</strong> ${apt.reason}</div>` : ''}
                    ${apt.specialist_notes ? `<div class="apt-notes"><strong>Notes:</strong> ${apt.specialist_notes}</div>` : ''}
                    ${isAccepted ? `
                        <div class="apt-actions">
                            <button class="btn btn-primary" onclick="joinVideoSession(${apt.id})">
                                <svg style="width: 16px; height: 16px; margin-right: 8px; vertical-align: middle;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="23 7 16 12 23 17 23 7"></polygon>
                                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                                </svg>
                                Join Video Session
                            </button>
                        </div>
                    ` : '<p class="apt-note">Waiting for confirmation</p>'}
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading upcoming appointments:', error);
    }
}

// Cancel appointment
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment request?')) {
        return;
    }
    
    try {
        await apiRequest(`/appointments/${appointmentId}`, {
            method: 'DELETE'
        });
        
        showToast('Appointment request cancelled', 'success');
        await loadMyAppointmentRequests();
        
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        showToast('Failed to cancel appointment: ' + error.message, 'error');
    }
}

// Load pending requests for specialists
async function loadPendingRequests() {
    try {
        const response = await apiRequest('/appointments/pending-requests');
        const pending = response || [];
        
        const container = document.getElementById('pending-requests-list');
        
        if (pending.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔔</div>
                    <p>No pending appointment requests</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = pending.map(apt => `
            <div class="appointment-card pending-request">
                <div class="apt-header">
                    <div class="apt-specialist">
                        <strong>${apt.clinician_name || 'Clinician'}</strong>
                        <span class="apt-specialty">Requesting consultation</span>
                    </div>
                    <span class="apt-status status-pending">Pending</span>
                </div>
                <div class="apt-details">
                    <div class="apt-detail-item">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        <span>${new Date(apt.requested_date).toLocaleString()}</span>
                    </div>
                    <div class="apt-detail-item">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <span>Duration: ${apt.duration_minutes || 30} minutes</span>
                    </div>
                </div>
                <div class="apt-reason">
                    <strong>Reason:</strong> ${apt.reason || 'Not specified'}
                </div>
                ${apt.clinician_notes ? `
                    <div class="apt-notes">
                        <strong>Notes:</strong> ${apt.clinician_notes}
                    </div>
                ` : ''}
                <div class="apt-actions">
                    <button class="btn btn-sm btn-danger" onclick="respondToAppointmentRequest(${apt.id}, 'rejected')">
                        Reject
                    </button>
                    <button class="btn btn-sm btn-success" onclick="openApprovalModal(${apt.id}, '${apt.clinician_name || 'Clinician'}', '${apt.requested_date}')">
                        Accept
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading pending requests:', error);
    }
}

// Open approval modal
function openApprovalModal(appointmentId, clinicianName, requestedDate) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content approval-modal">
            <div class="modal-header">
                <h2>Accept Appointment Request</h2>
                <button class="close-modal" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>Clinician:</strong> ${clinicianName}</p>
                <p><strong>Requested Date:</strong> ${new Date(requestedDate).toLocaleString()}</p>
                
                <form id="approvalForm" onsubmit="submitApproval(event, ${appointmentId})">
                    <div class="form-group">
                        <label>Scheduled Date & Time *</label>
                        <input type="datetime-local" id="scheduledDate" required value="${requestedDate.slice(0, 16)}" min="${new Date().toISOString().slice(0, 16)}">
                        <small>You can adjust the date/time if needed</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Notes to Clinician</label>
                        <textarea id="specialistNotes" rows="3" placeholder="Any additional information or instructions..."></textarea>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                        <button type="submit" class="btn btn-success">Confirm Acceptance</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Submit approval
async function submitApproval(event, appointmentId) {
    event.preventDefault();
    
    const scheduledDate = document.getElementById('scheduledDate').value;
    const specialistNotes = document.getElementById('specialistNotes').value;
    
    await respondToAppointmentRequest(appointmentId, 'accepted', scheduledDate, specialistNotes);
    document.querySelector('.modal-overlay').remove();
}

// Respond to appointment request
async function respondToAppointmentRequest(appointmentId, status, scheduledDate = null, notes = '') {
    try {
        const payload = {
            status: status,
            specialist_notes: notes
        };
        
        if (status === 'accepted' && scheduledDate) {
            payload.scheduled_date = scheduledDate;
        }
        
        await apiRequest(`/appointments/${appointmentId}/respond`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        
        showToast(
            status === 'accepted' 
                ? 'Appointment accepted successfully!' 
                : 'Appointment request rejected',
            'success'
        );
        
        // Reload pending requests
        await loadPendingRequests();
        
    } catch (error) {
        console.error('Error responding to appointment:', error);
        showToast('Failed to respond: ' + error.message, 'error');
    }
}

// Join video session
async function joinVideoSession(appointmentId) {
    try {
        showToast('Creating video session...', 'info');
        
        const response = await apiRequest('/video/session/create', {
            method: 'POST',
            body: JSON.stringify({
                appointment_id: appointmentId,
                session_name: `Appointment #${appointmentId} Consultation`
            })
        });
        
        if (response && response.join_url_host) {
            // Get auth token to pass to video window
            const authToken = localStorage.getItem('token');
            
            // Add auth token to URL for the new window to use
            const videoUrl = `${response.join_url_host}&auth=${encodeURIComponent(authToken)}`;
            
            // Open video session in new window
            window.open(videoUrl, '_blank', 'width=1280,height=720');
            showToast('Video session created! Opening in new window...', 'success');
        }
        
    } catch (error) {
        console.error('Error creating video session:', error);
        showToast('Failed to create video session: ' + error.message, 'error');
    }
}

