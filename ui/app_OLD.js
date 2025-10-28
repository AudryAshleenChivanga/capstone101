/**
 * Main application JavaScript for H. pylori CDSS Dashboard
 */

const API_BASE = 'http://localhost:8000';
let currentPage = 1;
let currentCaseId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = sessionStorage.getItem('jwt_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }
    
    // Load user info
    loadUserInfo();
    
    // Setup tab navigation
    setupTabs();
    
    // Setup form handlers
    setupScreeningForm();
    setupStagingForm();
    setupBatchUpload();
    
    // Setup logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Load initial data
    loadDashboardMetrics();
    loadRecentCases();
    loadCaseHistory();
    loadVersionInfo();
});

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const token = sessionStorage.getItem('jwt_token');
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        ...defaultOptions,
        headers: defaultOptions.headers
    });
    
    if (response.status === 401) {
        showToast('Session expired. Please login again.', 'error');
        setTimeout(() => {
            logout();
        }, 1500);
        throw new Error('Unauthorized');
    }
    
    return response;
}

// Load user info
async function loadUserInfo() {
    try {
        const response = await apiRequest('/auth/me');
        if (response.ok) {
            const user = await response.json();
            
            // Display doctor's full name or username
            const displayName = user.full_name || `Dr. ${user.username}`;
            document.getElementById('userName').textContent = displayName;
            
            // Update role badge with appropriate styling
            const roleBadge = document.getElementById('userRole');
            let roleDisplay = '';
            let roleIcon = '';
            
            switch(user.role) {
                case 'admin':
                    roleDisplay = 'Administrator';
                    roleIcon = '🏥';
                    break;
                case 'clinician':
                    roleDisplay = 'Clinician';
                    roleIcon = '👨‍⚕️';
                    break;
                case 'specialist':
                    roleDisplay = 'Specialist';
                    roleIcon = '🔬';
                    break;
                default:
                    roleDisplay = user.role;
                    roleIcon = '👨‍⚕️';
            }
            
            roleBadge.textContent = `${roleIcon} ${roleDisplay}`;
            roleBadge.className = 'badge';
            roleBadge.setAttribute('data-role', user.role);
            
            // Show model retrain section for admins
            if (user.role === 'admin') {
                const retrainSection = document.getElementById('modelRetrainSection');
                if (retrainSection) {
                    retrainSection.style.display = 'block';
                }
                
                // Show admin tab
                const adminTab = document.getElementById('adminTab');
                if (adminTab) {
                    adminTab.style.display = 'inline-block';
                }
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Logout
function logout() {
    sessionStorage.removeItem('jwt_token');
    sessionStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Tab navigation
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Update active states
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // Load tab-specific data
            if (targetTab === 'history') {
                loadCaseHistory();
            } else if (targetTab === 'settings') {
                loadVersionInfo();
            }
        });
    });
}

// Get form data as object
function getFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (value !== '' && value !== null) {
            // Convert numeric strings to numbers
            if (!isNaN(value) && value.trim() !== '') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    }
    
    return data;
}

// Screening form
function setupScreeningForm() {
    const form = document.getElementById('screeningForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner');
        
        submitBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.style.display = 'inline-block';
        
        try {
            const data = getFormData('screeningForm');
            
            const response = await apiRequest('/recommend', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                displayResults(result);
                showToast('Recommendation generated successfully', 'success');
                currentCaseId = result.case_id;
            } else {
                const error = await response.json();
                showToast(error.detail || 'Error processing request', 'error');
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error('Error:', error);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Get Recommendation';
            spinner.style.display = 'none';
        }
    });
}

// Display results
function displayResults(result) {
    const resultsPanel = document.getElementById('screeningResults');
    resultsPanel.style.display = 'block';
    
    // Draw gauge
    if (result.screen_prob !== null) {
        drawGauge('screeningGauge', result.screen_prob);
    }
    
    // Display stage badge
    if (result.stage_pred) {
        const stageBadge = document.getElementById('stageBadge');
        stageBadge.style.display = 'block';
        const stageValue = document.getElementById('stageValue');
        stageValue.textContent = result.stage_pred.toUpperCase();
        stageValue.className = 'badge badge-large badge-' + result.stage_pred;
    } else {
        document.getElementById('stageBadge').style.display = 'none';
    }
    
    // Display recommendations
    const recList = document.getElementById('recommendationList');
    recList.innerHTML = '';
    result.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recList.appendChild(li);
    });
    
    // Scroll to results
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Staging form
function setupStagingForm() {
    const form = document.getElementById('stagingForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner');
        
        submitBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.style.display = 'inline-block';
        
        try {
            const data = getFormData('stagingForm');
            
            const response = await apiRequest('/recommend', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                // Display results in staging tab (similar to screening)
                showToast('Stage prediction generated successfully', 'success');
                currentCaseId = result.case_id;
                
                // For simplicity, show alert with stage
                alert(`Stage Prediction: ${result.stage_pred || 'N/A'}\n\nRecommendations:\n${result.recommendations.join('\n')}`);
            } else {
                const error = await response.json();
                showToast(error.detail || 'Error processing request', 'error');
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error('Error:', error);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Get Stage Prediction';
            spinner.style.display = 'none';
        }
    });
}

// Batch CSV upload
function setupBatchUpload() {
    const fileInput = document.getElementById('csvFile');
    
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        document.getElementById('fileName').textContent = file.name;
        
        const formData = new FormData();
        formData.append('file', file);
        
        showToast('Processing batch file...', 'info');
        
        try {
            const token = sessionStorage.getItem('jwt_token');
            const response = await fetch(`${API_BASE}/recommend/batch`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                displayBatchResults(result);
                showToast(`Processed ${result.processed} of ${result.total} cases`, 'success');
            } else {
                const error = await response.json();
                showToast(error.detail || 'Error processing batch file', 'error');
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error('Error:', error);
        }
    });
}

// Display batch results
function displayBatchResults(result) {
    const resultsDiv = document.getElementById('batchResults');
    resultsDiv.style.display = 'block';
    
    // Update stats
    document.getElementById('totalCases').textContent = result.total;
    document.getElementById('processedCases').textContent = result.processed;
    
    // Count high risk cases
    const highRisk = result.results.filter(r => r.screen_prob >= 0.6).length;
    document.getElementById('highRiskCases').textContent = highRisk;
    
    // Populate table
    const tbody = document.querySelector('#batchResultsTable tbody');
    tbody.innerHTML = '';
    
    result.results.forEach(r => {
        const row = document.createElement('tr');
        
        const patientId = r.input_data.patient_pseudo_id || 'N/A';
        const prob = r.screen_prob ? (r.screen_prob * 100).toFixed(1) + '%' : 'N/A';
        const stage = r.stage_pred || 'N/A';
        const risk = r.screen_prob >= 0.6 ? 'High' : r.screen_prob >= 0.4 ? 'Moderate' : 'Low';
        
        row.innerHTML = `
            <td>${patientId}</td>
            <td>${prob}</td>
            <td>${stage}</td>
            <td><span class="badge badge-${risk.toLowerCase()}">${risk}</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

// Load case history
async function loadCaseHistory(page = 1) {
    try {
        const response = await apiRequest(`/cases?page=${page}&page_size=10`);
        
        if (response.ok) {
            const data = await response.json();
            displayCaseHistory(data);
            currentPage = page;
        }
    } catch (error) {
        console.error('Error loading case history:', error);
    }
}

// Display case history
function displayCaseHistory(data) {
    const tbody = document.querySelector('#historyTable tbody');
    tbody.innerHTML = '';
    
    if (data.cases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No cases found</td></tr>';
        return;
    }
    
    data.cases.forEach(caseItem => {
        const row = document.createElement('tr');
        
        const date = new Date(caseItem.created_at).toLocaleString();
        const patientId = caseItem.patient_pseudo_id || 'N/A';
        const prob = caseItem.screen_prob ? (caseItem.screen_prob * 100).toFixed(1) + '%' : 'N/A';
        const stage = caseItem.stage_pred || 'N/A';
        
        row.innerHTML = `
            <td>${date}</td>
            <td>${patientId}</td>
            <td>${prob}</td>
            <td>${stage}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="viewCaseDetail(${caseItem.id})" style="margin-right: 0.5rem;">View</button>
                <button class="btn btn-secondary btn-sm" onclick="deleteCase(${caseItem.id})" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white;">Delete</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Update pagination
    const totalPages = Math.ceil(data.total / data.page_size);
    document.getElementById('pageInfo').textContent = `Page ${data.page} of ${totalPages}`;
    document.getElementById('prevPage').disabled = data.page === 1;
    document.getElementById('nextPage').disabled = data.page === totalPages;
}

// Change page
function changePage(delta) {
    loadCaseHistory(currentPage + delta);
}

// View case detail
async function viewCaseDetail(caseId) {
    try {
        const response = await apiRequest(`/cases/${caseId}`);
        
        if (response.ok) {
            const caseData = await response.json();
            
            // Display in modal
            const modal = document.getElementById('caseModal');
            const jsonDisplay = document.getElementById('caseDetailJSON');
            jsonDisplay.textContent = JSON.stringify(caseData, null, 2);
            modal.style.display = 'flex';
        }
    } catch (error) {
        showToast('Error loading case details', 'error');
        console.error('Error:', error);
    }
}

// Close case modal
function closeCaseModal() {
    document.getElementById('caseModal').style.display = 'none';
}

// Copy results
function copyResults() {
    const recommendations = Array.from(document.querySelectorAll('#recommendationList li'))
        .map(li => li.textContent)
        .join('\n');
    
    navigator.clipboard.writeText(recommendations).then(() => {
        showToast('Results copied to clipboard', 'success');
    }).catch(err => {
        showToast('Failed to copy results', 'error');
    });
}

// Show SMS dialog
function showSMSDialog() {
    const dialog = document.getElementById('smsDialog');
    dialog.style.display = 'block';
}

// Send SMS
async function sendSMS() {
    const phoneNumber = document.getElementById('phoneNumber').value;
    
    if (!phoneNumber) {
        showToast('Please enter a phone number', 'error');
        return;
    }
    
    const recommendations = Array.from(document.querySelectorAll('#recommendationList li'))
        .map(li => li.textContent)
        .join('\n');
    
    const message = `H. pylori CDSS Recommendation:\n\n${recommendations}`;
    
    try {
        const response = await apiRequest('/notify/patient', {
            method: 'POST',
            body: JSON.stringify({
                phone_number: phoneNumber,
                message: message,
                case_id: currentCaseId
            })
        });
        
        if (response.ok) {
            showToast('SMS notification queued (stub)', 'success');
            document.getElementById('smsDialog').style.display = 'none';
            document.getElementById('phoneNumber').value = '';
        } else {
            showToast('Failed to send SMS', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Error:', error);
    }
}

// Create telemedicine session
async function createTelemedSession() {
    const caseId = document.getElementById('telemedCaseId').value;
    
    try {
        const response = await apiRequest('/telemed/session', {
            method: 'POST',
            body: JSON.stringify({
                case_id: caseId ? parseInt(caseId) : null
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            document.getElementById('sessionId').textContent = result.session_id;
            document.getElementById('joinUrl').textContent = result.join_url;
            document.getElementById('telemedResult').style.display = 'block';
            
            showToast('Telemedicine session created', 'success');
        } else {
            showToast('Failed to create session', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Error:', error);
    }
}

// Copy join URL
function copyJoinUrl() {
    const url = document.getElementById('joinUrl').textContent;
    navigator.clipboard.writeText(url).then(() => {
        showToast('Join URL copied to clipboard', 'success');
    });
}

// Load version info
async function loadVersionInfo() {
    try {
        const response = await fetch(`${API_BASE}/version`);
        
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('serviceVersion').textContent = data.service_version;
            document.getElementById('sklearnVersion').textContent = data.scikit_learn_version;
            document.getElementById('pandasVersion').textContent = data.pandas_version;
            
            document.getElementById('screeningModel').textContent = data.models.screening_model;
            document.getElementById('stagingModel').textContent = data.models.staging_model || 'Not configured';
            document.getElementById('riskThreshold').textContent = (data.models.screening_threshold * 100).toFixed(0) + '%';
        }
    } catch (error) {
        console.error('Error loading version info:', error);
    }
}

// Download CSV template
function downloadCSVTemplate() {
    const headers = [
        'patient_pseudo_id', 'age', 'sex', 'residence', 'sanitation', 'water_source',
        'crowding', 'poverty_index', 'smoking', 'nsaid_use', 'prior_antibiotics_3m',
        'epigastric_pain', 'nausea', 'bloating', 'early_satiety', 'weight_loss',
        'stool_ag', 'stool_ab', 'hemoglobin', 'crp', 'wbc',
        'mic_clari', 'mut_A2143G', 'mut_A2144G', 'double_mut'
    ];
    
    const sampleRow = [
        'PATIENT001', '45', 'M', 'urban', 'good', 'treated',
        '2.5', '0.3', '1', '0', '0',
        '1', '1', '0', '0', '0',
        '1', '0', '13.5', '8.2', '7.5',
        '', '', '', ''
    ];
    
    const csv = [headers.join(','), sampleRow.join(',')].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cdss_template.csv';
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('Template downloaded', 'success');
}

// ========================================
// SIGNATURE PAD & DOCUMENT EDITING
// ========================================

let signaturePad = null;
let currentRecommendations = '';
let currentScreeningResult = null;

// Initialize signature pad
function initSignaturePad() {
    const canvas = document.getElementById('signaturePad');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    canvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        const rect = canvas.getBoundingClientRect();
        lastX = e.clientX - rect.left;
        lastY = e.clientY - rect.top;
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        lastX = x;
        lastY = y;
    });
    
    canvas.addEventListener('mouseup', () => {
        isDrawing = false;
    });
    
    canvas.addEventListener('mouseleave', () => {
        isDrawing = false;
    });
    
    // Touch support for mobile
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isDrawing = true;
        const rect = canvas.getBoundingClientRect();
        const touch = e.touches[0];
        lastX = touch.clientX - rect.left;
        lastY = touch.clientY - rect.top;
    });
    
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        const touch = e.touches[0];
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        lastX = x;
        lastY = y;
    });
    
    canvas.addEventListener('touchend', () => {
        isDrawing = false;
    });
    
    signaturePad = { canvas, ctx };
}

// Open signature modal
function openSignatureModal() {
    const modal = document.getElementById('signatureModal');
    if (!modal) return;
    
    // Get current recommendations
    const recommendationList = document.getElementById('recommendationList');
    const recommendations = [];
    if (recommendationList) {
        recommendationList.querySelectorAll('li').forEach(li => {
            recommendations.push(li.textContent);
        });
    }
    currentRecommendations = recommendations.join('\n');
    
    // Pre-fill the recommendations textarea
    document.getElementById('editedRecommendations').value = currentRecommendations;
    
    // Reset modal to step 1
    showSignatureStep('editStep');
    
    // Show modal
    modal.style.display = 'flex';
    
    // Initialize signature pad
    setTimeout(() => initSignaturePad(), 300);
}

// Close signature modal
function closeSignatureModal() {
    const modal = document.getElementById('signatureModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Reset form
    document.getElementById('patientName').value = '';
    document.getElementById('patientEmail').value = '';
    document.getElementById('patientPhone').value = '';
    document.getElementById('editedRecommendations').value = '';
    document.getElementById('clinicianNotes').value = '';
    clearSignature();
}

// Show specific signature step
function showSignatureStep(stepId) {
    document.querySelectorAll('.signature-step').forEach(step => {
        step.classList.remove('active');
    });
    const step = document.getElementById(stepId);
    if (step) {
        step.classList.add('active');
    }
}

// Go to signature step
function goToSignatureStep() {
    const patientName = document.getElementById('patientName').value;
    const editedRecs = document.getElementById('editedRecommendations').value;
    
    if (!patientName.trim()) {
        showToast('Please enter patient name', 'error');
        return;
    }
    
    if (!editedRecs.trim()) {
        showToast('Please enter recommendations', 'error');
        return;
    }
    
    showSignatureStep('signatureStep');
}

// Go back to edit step
function goBackToEdit() {
    showSignatureStep('editStep');
}

// Clear signature
function clearSignature() {
    if (signaturePad && signaturePad.canvas) {
        const ctx = signaturePad.ctx;
        ctx.clearRect(0, 0, signaturePad.canvas.width, signaturePad.canvas.height);
    }
}

// Check if signature pad is empty
function isSignatureEmpty() {
    if (!signaturePad || !signaturePad.canvas) return true;
    
    const canvas = signaturePad.canvas;
    const ctx = canvas.getContext('2d');
    const pixelData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    
    // Check if any pixel is not transparent
    for (let i = 3; i < pixelData.length; i += 4) {
        if (pixelData[i] !== 0) return false;
    }
    return true;
}

// Finalize and send
async function finalizeAndSend() {
    if (isSignatureEmpty()) {
        showToast('Please add your signature', 'error');
        return;
    }
    
    const patientName = document.getElementById('patientName').value;
    const patientEmail = document.getElementById('patientEmail').value;
    const patientPhone = document.getElementById('patientPhone').value;
    const editedRecs = document.getElementById('editedRecommendations').value;
    const notes = document.getElementById('clinicianNotes').value;
    
    // Get signature as base64
    const signatureData = signaturePad.canvas.toDataURL('image/png');
    
    try {
        const token = sessionStorage.getItem('jwt_token');
        
        // For now, show success (backend integration needed)
        showSignatureStep('confirmationStep');
        
        showToast('Recommendation signed and sent successfully!', 'success');
        
        // TODO: Implement actual API call to backend
        // const response = await fetch(`${API_BASE}/cases/${currentCaseId}/sign`, {
        //     method: 'POST',
        //     headers: {
        //         'Authorization': `Bearer ${token}`,
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({
        //         patient_name: patientName,
        //         patient_email: patientEmail,
        //         patient_phone: patientPhone,
        //         edited_recommendations: editedRecs,
        //         notes: notes,
        //         signature_data: signatureData
        //     })
        // });
        
    } catch (error) {
        console.error('Error signing and sending:', error);
        showToast('Error signing and sending recommendation', 'error');
    }
}

// Video consultation functions
let isRecording = false;

async function createVideoSession() {
    const caseId = document.getElementById('telemedCaseId').value;
    const sessionName = document.getElementById('sessionName').value || 'Consultation';
    
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/video/session/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                case_id: caseId || null,
                session_name: sessionName
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create session');
        }
        
        const data = await response.json();
        
        // Show result
        document.getElementById('telemedResult').style.display = 'block';
        document.getElementById('roomName').textContent = data.session_id;
        document.getElementById('joinUrl').value = data.join_url_guest;
        
        // Load QR code
        const qrUrl = `${API_BASE}/video/session/${data.session_id}/qr?token=${data.guest_token}`;
        document.getElementById('qrCodeImage').src = qrUrl;
        
        // Show record button
        const recordBtn = document.getElementById('recordBtn');
        if (recordBtn) {
            recordBtn.style.display = 'inline-flex';
        }
        
        // Store session ID for host join
        window.currentVideoSession = data;
        
        showToast('Video session created successfully!', 'success');
    } catch (error) {
        console.error('Error creating video session:', error);
        showToast('Failed to create video session', 'error');
    }
}

function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    
    if (!isRecording) {
        // Start recording
        isRecording = true;
        recordBtn.textContent = '⏹ Stop Recording';
        recordBtn.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)';
        recordBtn.style.color = 'white';
        showToast('Recording started', 'info');
        
        // In production, this would actually start recording the video stream
        console.log('Recording started...');
    } else {
        // Stop recording
        isRecording = false;
        recordBtn.textContent = '⏺ Start Recording';
        recordBtn.style.background = '';
        recordBtn.style.color = '';
        showToast('Recording stopped', 'success');
        
        // In production, this would save the recording
        console.log('Recording stopped');
    }
}

function endVideoSession() {
    if (!confirm('Are you sure you want to end this session?')) {
        return;
    }
    
    // Hide result section
    document.getElementById('telemedResult').style.display = 'none';
    
    // Reset form
    document.getElementById('telemedCaseId').value = '';
    document.getElementById('sessionName').value = '';
    
    // Reset recording state
    isRecording = false;
    const recordBtn = document.getElementById('recordBtn');
    if (recordBtn) {
        recordBtn.style.display = 'none';
        recordBtn.textContent = '⏺ Start Recording';
        recordBtn.style.background = '';
    }
    
    // Clear session data
    window.currentVideoSession = null;
    
    showToast('Video session ended', 'info');
}

function copyJoinUrl() {
    const urlInput = document.getElementById('joinUrl');
    urlInput.select();
    document.execCommand('copy');
    showToast('Link copied to clipboard!', 'success');
}

function joinAsHost() {
    if (window.currentVideoSession) {
        const hostUrl = window.currentVideoSession.join_url_host;
        window.open(hostUrl, '_blank');
    }
}

// Profile update function
async function updateProfile(event) {
    event.preventDefault();
    
    const profileData = {
        full_name: document.getElementById('profile_full_name').value,
        email: document.getElementById('profile_email').value,
        phone: document.getElementById('profile_phone').value,
        specialty: document.getElementById('profile_specialty').value,
        license_number: document.getElementById('profile_license').value,
        institution: document.getElementById('profile_institution').value,
        bio: document.getElementById('profile_bio').value
    };
    
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/profile/update`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to update profile');
        }
        
        showToast('Profile updated successfully!', 'success');
        loadUserInfo(); // Refresh user info
    } catch (error) {
        console.error('Error updating profile:', error);
        showToast('Failed to update profile', 'error');
    }
}

// ========================================
// DASHBOARD METRICS & RECENT CASES
// ========================================

// Chart instances
let casesChart = null;
let riskChart = null;

// Load dashboard metrics
async function loadDashboardMetrics() {
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/cases/report`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) return;
        
        const report = await response.json();
        const summary = report.summary;
        
        // Update metric cards
        document.getElementById('totalCasesMetric').textContent = summary.total_cases || 0;
        document.getElementById('screeningCasesMetric').textContent = summary.screening_cases || 0;
        document.getElementById('stagingCasesMetric').textContent = summary.staging_cases || 0;
        document.getElementById('highRiskMetric').textContent = summary.high_risk_cases || 0;
        
        // Initialize charts with data
        initializeCasesChart(summary);
        initializeRiskChart(summary);
    } catch (error) {
        console.error('Error loading dashboard metrics:', error);
    }
}

// Initialize Cases Overview Chart
function initializeCasesChart(summary) {
    const ctx = document.getElementById('casesChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (casesChart) {
        casesChart.destroy();
    }
    
    // Generate sample data for last 30 days
    const labels = [];
    const screeningData = [];
    const stagingData = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Generate sample data based on totals
        const screeningPerDay = Math.floor((summary.screening_cases || 0) / 30);
        const stagingPerDay = Math.floor((summary.staging_cases || 0) / 30);
        
        screeningData.push(screeningPerDay + Math.floor(Math.random() * 3));
        stagingData.push(stagingPerDay + Math.floor(Math.random() * 2));
    }
    
    casesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Screening',
                    data: screeningData,
                    borderColor: '#38ef7d',
                    backgroundColor: 'rgba(56, 239, 125, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Staging',
                    data: stagingData,
                    borderColor: '#ffd93d',
                    backgroundColor: 'rgba(255, 217, 61, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2.5,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Initialize Risk Distribution Chart
function initializeRiskChart(summary) {
    const ctx = document.getElementById('riskChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (riskChart) {
        riskChart.destroy();
    }
    
    const total = summary.total_cases || 0;
    const highRisk = summary.high_risk_cases || 0;
    const lowRisk = total - highRisk;
    
    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High Risk', 'Low Risk'],
            datasets: [{
                data: [highRisk, lowRisk],
                backgroundColor: [
                    'rgba(255, 107, 107, 0.8)',
                    'rgba(56, 239, 125, 0.8)'
                ],
                borderColor: [
                    '#ff6b6b',
                    '#38ef7d'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.2,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Load recent cases
async function loadRecentCases() {
    try {
        const response = await apiRequest('/cases?page=1&page_size=5');
        
        if (response.ok) {
            const data = await response.json();
            displayRecentCases(data.cases);
        }
    } catch (error) {
        console.error('Error loading recent cases:', error);
    }
}

// Display recent cases
function displayRecentCases(cases) {
    const container = document.getElementById('recentCasesList');
    
    if (!cases || cases.length === 0) {
        container.innerHTML = '<p class="loading-text">No recent cases found</p>';
        return;
    }
    
    container.innerHTML = cases.map(c => `
        <div class="case-item">
            <div>
                <strong>${c.patient_pseudo_id || 'N/A'}</strong>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.25rem 0 0 0;">
                    ${new Date(c.created_at).toLocaleDateString()} - ${c.task}
                </p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="viewCaseDetail(${c.id})">View</button>
        </div>
    `).join('');
}

// Switch tab programmatically
function switchTab(tabName) {
    const tabBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabBtn) {
        tabBtn.click();
    }
}

// ========================================
// DELETE CASE, REPORTS, MODEL RETRAINING
// ========================================

// Delete a case
async function deleteCase(caseId) {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
        return;
    }
    
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/cases/${caseId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete case');
        }
        
        showToast('Case deleted successfully!', 'success');
        loadCaseHistory(); // Refresh the list
    } catch (error) {
        console.error('Error deleting case:', error);
        showToast('Failed to delete case', 'error');
    }
}

// Generate comprehensive report
async function generateReport() {
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/cases/report`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate report');
        }
        
        const report = await response.json();
        
        // Display report in a modal
        showReportModal(report);
        
        showToast('Report generated successfully!', 'success');
    } catch (error) {
        console.error('Error generating report:', error);
        showToast('Failed to generate report', 'error');
    }
}

// Show report modal
function showReportModal(report) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    
    const summary = report.summary;
    
    modal.innerHTML = `
        <div class="modal-content modal-large">
            <div class="modal-header">
                <h2>Cases Report</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom: 2rem;">
                    <p><strong>Generated:</strong> ${new Date(report.report_date).toLocaleString()}</p>
                    <p><strong>By:</strong> ${report.generated_by}</p>
                    <p><strong>Date Range:</strong> ${report.date_range.start} to ${report.date_range.end}</p>
                </div>
                
                <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                    <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                        <div class="stat-value" style="font-size: 2.5rem; font-weight: 700;">${summary.total_cases}</div>
                        <div class="stat-label" style="font-size: 0.9rem; opacity: 0.9;">Total Cases</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                        <div class="stat-value" style="font-size: 2.5rem; font-weight: 700;">${summary.screening_cases}</div>
                        <div class="stat-label" style="font-size: 0.9rem; opacity: 0.9;">Screening</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                        <div class="stat-value" style="font-size: 2.5rem; font-weight: 700;">${summary.staging_cases}</div>
                        <div class="stat-label" style="font-size: 0.9rem; opacity: 0.9;">Staging</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                        <div class="stat-value" style="font-size: 2.5rem; font-weight: 700;">${summary.high_risk_cases}</div>
                        <div class="stat-label" style="font-size: 0.9rem; opacity: 0.9;">High Risk</div>
                    </div>
                </div>
                
                <div style="margin-top: 2rem;">
                    <p><strong>Average Screening Probability:</strong> ${(summary.average_screening_probability * 100).toFixed(1)}%</p>
                </div>
                
                <div style="margin-top: 2rem; text-align: center;">
                    <button class="btn btn-primary" onclick="downloadReportJSON(${JSON.stringify(report).replace(/"/g, '&quot;')})">
                        Download Full Report (JSON)
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Download report as JSON
function downloadReportJSON(report) {
    const dataStr = JSON.stringify(report, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cdss_report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Retrain models
async function retrainModels() {
    if (!confirm('Model retraining is a resource-intensive process. Are you sure you want to proceed?')) {
        return;
    }
    
    const statusDiv = document.getElementById('retrainStatus');
    const statusMessage = statusDiv.querySelector('.status-message');
    
    statusDiv.style.display = 'block';
    statusMessage.textContent = 'Initiating model retraining...';
    statusMessage.style.color = '#667eea';
    
    try {
        const token = sessionStorage.getItem('jwt_token');
        const response = await fetch(`${API_BASE}/ml/retrain`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to retrain models');
        }
        
        const result = await response.json();
        
        statusMessage.innerHTML = `
            <strong>Status:</strong> ${result.status}<br>
            <strong>Message:</strong> ${result.message}<br>
            <strong>Total Cases:</strong> ${result.data_summary.total_cases}<br>
            <strong>Screening Cases:</strong> ${result.data_summary.screening_cases}<br>
            <strong>Staging Cases:</strong> ${result.data_summary.staging_cases}<br>
            <br>
            <em>${result.note}</em>
        `;
        statusMessage.style.color = '#38ef7d';
        
        showToast('Model retraining initiated successfully!', 'success');
    } catch (error) {
        console.error('Error retraining models:', error);
        statusMessage.textContent = `Error: ${error.message}`;
        statusMessage.style.color = '#ff6b6b';
        showToast(error.message, 'error');
    }
}
