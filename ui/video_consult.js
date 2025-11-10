// ========================================
// VIDEO CONSULTATION & APPOINTMENT BOOKING
// H. pylori CDSS
// ========================================

// Initialize Video Consultation Page
async function initVideoConsultation() {
    console.log('Initializing Video Consultation...');
    await loadSpecialistsForBooking();
    await loadMyAppointmentRequests();
    await loadUpcomingAppointments();
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
                <div class="specialist-avatar">
                    ${specialist.profile_photo ? 
                        `<img src="${specialist.profile_photo}" alt="${displayName}">` : 
                        `<div class="avatar-placeholder">${initials}</div>`
                    }
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
        preferred_date: document.getElementById('appointmentDateTime').value,
        case_id: document.getElementById('relatedCase').value || null,
        urgency: document.getElementById('urgencyLevel').value,
        reason: document.getElementById('consultationReason').value,
        notes: document.getElementById('additionalNotes').value
    };
    
    try {
        const response = await apiRequest('/scheduling/appointments', {
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
                    <div class="empty-icon">[Calendar]</div>
                    <p>No upcoming appointments</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = upcoming.map(apt => `
            <div class="appointment-card confirmed">
                <div class="apt-header">
                    <div class="apt-specialist">
                        <strong>${apt.specialist_name}</strong>
                        <span class="apt-specialty">${apt.specialist_specialty}</span>
                    </div>
                    <span class="apt-status status-confirmed">Confirmed</span>
                </div>
                <div class="apt-details">
                    <div class="apt-detail-item">
                        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        <span>${new Date(apt.confirmed_date).toLocaleString()}</span>
                    </div>
                </div>
                ${apt.video_link ? `
                    <div class="apt-actions">
                        <a href="${apt.video_link}" target="_blank" class="btn btn-primary">
                            Join Video Session
                        </a>
                    </div>
                ` : '<p class="apt-note">Video link will be available closer to the appointment time</p>'}
            </div>
        `).join('');
        
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
        await apiRequest(`/scheduling/appointments/${appointmentId}/cancel`, {
            method: 'PUT'
        });
        
        showToast('Appointment request cancelled', 'success');
        await loadMyAppointmentRequests();
        
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        showToast('Failed to cancel appointment: ' + error.message, 'error');
    }
}

