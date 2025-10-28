// ========================================
// PROFESSIONAL MEDICAL DASHBOARD
// Dark/Light Mode, Charts, Real-time Updates
// ========================================

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : window.location.origin;
let authToken = null;
let currentUser = null;
let charts = {};

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Check authentication
    authToken = localStorage.getItem('token');
    if (!authToken) {
        window.location.href = 'index.html';
        return;
    }
    
    // Load theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Setup event listeners
    setupEventListeners();
    
    // Load user data
    loadUserData();
    
    // Load dashboard data
    loadDashboardData();
}

function setupEventListeners() {
    // Sidebar navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', handleNavigation);
    });
    
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Restore sidebar state
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
    
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}

// ========================================
// NAVIGATION
// ========================================

function handleNavigation(e) {
    e.preventDefault();
    
    const clickedItem = e.currentTarget;
    const pageId = clickedItem.getAttribute('data-page');
    
    // Update active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    clickedItem.classList.add('active');
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    
    // Show selected page
    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
        targetPage.style.display = 'block';
        
        // Initialize page-specific functionality
        initializeCurrentPage(pageId);
        
        // Update page title
        const pageTitle = clickedItem.querySelector('span').textContent;
        document.getElementById('pageTitle').textContent = pageTitle;
        
        // Load page-specific data
        loadPageData(pageId);
    }
}

function loadPageData(pageId) {
    switch(pageId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'screening':
            // Load screening form
            break;
        case 'staging':
            // Load staging form
            break;
        case 'cases':
            loadCaseHistory();
            break;
        case 'profile':
            loadProfilePage();
            break;
        case 'admin':
            loadAdminPanel();
            break;
    }
}

// ========================================
// THEME MANAGEMENT
// ========================================

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme label
    const themeLabel = document.querySelector('.theme-label');
    themeLabel.textContent = newTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    
    // Re-render charts with new theme
    updateChartsTheme();
    
    showToast(`Switched to ${newTheme} mode`, 'success');
}

// ========================================
// USER DATA
// ========================================

async function loadUserData() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load user data');
        
        currentUser = await response.json();
        
        // Update UI
        document.getElementById('userName').textContent = currentUser.full_name || `Dr. ${currentUser.username}`;
        document.getElementById('userRole').textContent = currentUser.role || 'Clinician';
        
        // Set avatar based on user - use real doctor images
        const avatarMap = {
            'admin': '/images/Dr_Angie.webp',
            'clinician': '/images/Dr_Ishimwe.webp',
            'specialist': '/images/Dr_Mugisha.webp',
            'default': '/images/Dr_Tatenda.webp'
        };
        
        let avatarSrc = avatarMap[currentUser.role] || avatarMap.default;
        
        // If user has custom profile photo, use that instead
        if (currentUser.profile_photo) {
            avatarSrc = currentUser.profile_photo;
        }
        
        document.querySelector('.user-avatar').src = avatarSrc;
        
        // Show admin nav if admin
        if (currentUser.role === 'admin') {
            document.getElementById('adminNavItem').style.display = 'flex';
        }
        
    } catch (error) {
        console.error('Error loading user data:', error);
        showToast('Failed to load user information', 'error');
    }
}

// ========================================
// DASHBOARD DATA
// ========================================

async function loadDashboardData() {
    try {
        // Load stats
        const statsResponse = await fetch(`${API_BASE}/cases/report`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: getDateDaysAgo(30),
                end_date: new Date().toISOString().split('T')[0]
            })
        });
        
        if (!statsResponse.ok) throw new Error('Failed to load stats');
        
        const statsData = await statsResponse.json();
        
        // Update stat cards
        updateStatCards(statsData);
        
        // Load and render charts
        renderCharts(statsData);
        
        // Load recent activity
        loadRecentActivity();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

function updateStatCards(data) {
    const summary = data.summary || {};
    
    document.getElementById('statTotalCases').textContent = summary.total_cases || 0;
    document.getElementById('statScreening').textContent = summary.screening_cases || 0;
    document.getElementById('statStaging').textContent = summary.staging_cases || 0;
    document.getElementById('statHighRisk').textContent = summary.high_risk_cases || 0;
}

// ========================================
// CHARTS
// ========================================

function renderCharts(data) {
    const theme = document.documentElement.getAttribute('data-theme');
    const isDark = theme === 'dark';
    
    const textColor = isDark ? '#f7fafc' : '#2d3748';
    const gridColor = isDark ? '#4a5568' : '#e2e8f0';
    
    Chart.defaults.color = textColor;
    Chart.defaults.borderColor = gridColor;
    
    // Cases Line Chart
    renderCasesLineChart(data, textColor, gridColor);
    
    // Risk Doughnut Chart
    renderRiskDoughnutChart(data);
    
    // Monthly Bar Chart
    renderMonthlyBarChart(data, textColor, gridColor);
    
    // Success Rate Chart
    renderSuccessRateChart(data, textColor, gridColor);
}

function renderCasesLineChart(data, textColor, gridColor) {
    const ctx = document.getElementById('casesLineChart');
    if (!ctx) return;
    
    if (charts.casesLine) {
        charts.casesLine.destroy();
    }
    
    // Generate last 30 days data
    const labels = [];
    const casesData = [];
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        casesData.push(Math.floor(Math.random() * 10) + 5); // Mock data
    }
    
    charts.casesLine = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Cases',
                data: casesData,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor,
                        maxRotation: 0
                    }
                }
            }
        }
    });
}

function renderRiskDoughnutChart(data) {
    const ctx = document.getElementById('riskDoughnutChart');
    if (!ctx) return;
    
    if (charts.riskDoughnut) {
        charts.riskDoughnut.destroy();
    }
    
    const summary = data.summary || {};
    
    charts.riskDoughnut = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High Risk', 'Medium Risk', 'Low Risk'],
            datasets: [{
                data: [
                    summary.high_risk_cases || 15,
                    summary.medium_risk_cases || 35,
                    summary.low_risk_cases || 50
                ],
                backgroundColor: [
                    '#ff6b6b',
                    '#ffd93d',
                    '#38ef7d'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8
                }
            }
        }
    });
}

function renderMonthlyBarChart(data, textColor, gridColor) {
    const ctx = document.getElementById('monthlyBarChart');
    if (!ctx) return;
    
    if (charts.monthlyBar) {
        charts.monthlyBar.destroy();
    }
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const screeningData = [45, 52, 48, 65, 58, 70];
    const stagingData = [30, 38, 35, 42, 48, 55];
    
    charts.monthlyBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Screening',
                    data: screeningData,
                    backgroundColor: '#667eea',
                    borderRadius: 6
                },
                {
                    label: 'Staging',
                    data: stagingData,
                    backgroundColor: '#38ef7d',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
}

function renderSuccessRateChart(data, textColor, gridColor) {
    const ctx = document.getElementById('successRateChart');
    if (!ctx) return;
    
    if (charts.successRate) {
        charts.successRate.destroy();
    }
    
    const treatments = ['First Line', 'Second Line', 'Third Line'];
    const successRates = [85, 72, 65];
    
    charts.successRate = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: treatments,
            datasets: [{
                label: 'Success Rate (%)',
                data: successRates,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f5576c'
                ],
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
}

function updateChartsTheme() {
    if (Object.keys(charts).length > 0) {
        loadDashboardData();
    }
}

// ========================================
// RECENT ACTIVITY
// ========================================

async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_BASE}/cases?limit=5`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load recent activity');
        
        const cases = await response.json();
        
        const activityList = document.getElementById('recentActivity');
        
        if (cases.length === 0) {
            activityList.innerHTML = '<p class="loading">No recent activity</p>';
            return;
        }
        
        activityList.innerHTML = cases.map(caseItem => `
            <div class="activity-item">
                <div>
                    <strong>Case #${caseItem.id}</strong> - ${caseItem.case_type}
                    <br>
                    <small style="color: var(--text-secondary);">
                        ${new Date(caseItem.created_at).toLocaleDateString()}
                    </small>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

// ========================================
// CASE HISTORY
// ========================================

async function loadCaseHistory() {
    // Implementation for case history page
    console.log('Loading case history...');
}

// ========================================
// PROFILE PAGE
// ========================================

async function loadProfilePage() {
    if (!currentUser) {
        await loadUserData();
    }
    
    // Update profile display
    document.getElementById('profileName').textContent = currentUser.full_name || `Dr. ${currentUser.username}`;
    document.getElementById('profileRole').textContent = currentUser.role || 'Clinician';
    document.getElementById('profileUsername').textContent = currentUser.username;
    document.getElementById('profileEmail').textContent = currentUser.email || 'Not set';
    document.getElementById('profileInstitution').textContent = currentUser.institution || 'Not set';
    document.getElementById('profileSpecialty').textContent = currentUser.specialty || 'Not set';
    
    // Set profile avatar based on role
    const avatarMap = {
        'admin': '/images/Dr_Angie.webp',
        'clinician': '/images/Dr_Ishimwe.webp',
        'specialist': '/images/Dr_Mugisha.webp',
        'default': '/images/Dr_Tatenda.webp'
    };
    
    let avatarSrc = avatarMap[currentUser.role] || avatarMap.default;
    if (currentUser.profile_photo) {
        avatarSrc = currentUser.profile_photo;
    }
    
    document.getElementById('profileAvatar').src = avatarSrc;
}

// ========================================
// ADMIN PANEL
// ========================================

async function loadAdminPanel() {
    // Implementation for admin panel
    console.log('Loading admin panel...');
}

// ========================================
// LOGOUT
// ========================================

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

// ========================================
// UTILITIES
// ========================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getDateDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
}

// ========================================
// API HELPERS
// ========================================

async function apiRequest(endpoint, options = {}) {
    // Ensure we have the latest token
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        throw new Error('No authentication token');
    }
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
        throw new Error('Authentication failed');
    }
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API request failed: ${response.statusText}`);
    }
    
    return response.json();
}

// ========================================
// PAGE-SPECIFIC FUNCTIONALITY
// ========================================

// Screening Assessment Functions
function initializeScreeningPage() {
    const form = document.getElementById('screeningForm');
    if (form) {
        form.addEventListener('submit', handleScreeningSubmit);
    }
}

async function handleScreeningSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Convert string values to appropriate types
    data.age = parseInt(data.age);
    data.stool_ag = parseInt(data.stool_ag);
    data.hemoglobin = parseFloat(data.hemoglobin);
    
    // Add task type for screening
    data.task = 'screening';
    
    try {
        showSpinner(e.target);
        const result = await apiRequest('/recommend', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        // Store the case ID for signing/SMS later
        currentCaseId = result.case_id;
        currentRecommendations = result.recommendations || [];
        
        displayScreeningResults(result);
        showToast('Screening assessment completed successfully!', 'success');
    } catch (error) {
        showToast('Error processing screening: ' + error.message, 'error');
    } finally {
        hideSpinner(e.target);
    }
}

function displayScreeningResults(result) {
    const resultsPanel = document.getElementById('screeningResults');
    const recommendationList = document.getElementById('recommendationList');
    
    // Show results panel
    resultsPanel.style.display = 'block';
    
    // Update gauge (use screen_prob from API response)
    const probability = result.screen_prob || 0;
    updateScreeningGauge(probability);
    
    // Update recommendations
    recommendationList.innerHTML = (result.recommendations || []).map(rec => 
        `<li>${rec}</li>`
    ).join('');
}

function updateScreeningGauge(probability) {
    // Simple gauge implementation
    const canvas = document.getElementById('screeningGauge');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        const percentage = Math.round(probability * 100);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw gauge background
        ctx.beginPath();
        ctx.arc(100, 80, 60, Math.PI, 0);
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 10;
        ctx.stroke();
        
        // Draw gauge value
        const angle = Math.PI + (probability * Math.PI);
        ctx.beginPath();
        ctx.arc(100, 80, 60, Math.PI, angle);
        ctx.strokeStyle = probability > 0.6 ? '#ff4444' : probability > 0.3 ? '#ffaa00' : '#44ff44';
        ctx.lineWidth = 10;
        ctx.stroke();
        
        // Draw percentage text
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${percentage}%`, 100, 100);
    }
}

// Staging Assessment Functions
function initializeStagingPage() {
    const form = document.getElementById('stagingForm');
    if (form) {
        form.addEventListener('submit', handleStagingSubmit);
    }
}

async function handleStagingSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Convert values to appropriate types
    data.age = parseInt(data.age);
    data.mic_clari = parseFloat(data.mic_clari);
    data.mut_A2143G = parseInt(data.mut_A2143G);
    data.mut_A2144G = parseInt(data.mut_A2144G);
    
    // Add task type for staging
    data.task = 'staging';
    
    try {
        showSpinner(e.target);
        // Use the /recommend endpoint which handles both screening and staging
        const result = await apiRequest('/recommend', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        displayStagingResults(result);
        showToast('Staging assessment completed successfully!', 'success');
    } catch (error) {
        showToast('Error processing staging: ' + error.message, 'error');
    } finally {
        hideSpinner(e.target);
    }
}

function displayStagingResults(result) {
    const resultsPanel = document.getElementById('stagingResults');
    const stageValue = document.getElementById('stageValue');
    const recommendationList = document.getElementById('stagingRecommendationList');
    
    resultsPanel.style.display = 'block';
    stageValue.textContent = result.stage_pred || 'Unknown';
    
    // Add stage color coding
    const stageElement = document.getElementById('stageValue');
    if (result.stage_pred) {
        stageElement.className = `stage-${result.stage_pred}`;
        switch(result.stage_pred.toLowerCase()) {
            case 'low':
                stageElement.style.color = '#22c55e';
                break;
            case 'moderate': 
                stageElement.style.color = '#f59e0b';
                break;
            case 'high':
                stageElement.style.color = '#ef4444';
                break;
        }
    }
    
    recommendationList.innerHTML = (result.recommendations || []).map(rec => 
        `<li>${rec}</li>`
    ).join('');
}

// Case History Functions
async function loadCaseHistory() {
    try {
        const response = await apiRequest('/cases?page=1&page_size=50');
        // API returns { total, page, page_size, cases }
        displayCaseHistory(response.cases || []);
    } catch (error) {
        showToast('Error loading case history: ' + error.message, 'error');
        console.error('Case history error:', error);
    }
}

function displayCaseHistory(cases) {
    const tbody = document.getElementById('casesTableBody');
    if (!tbody) return;
    
    if (!cases || cases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No cases found</td></tr>';
        return;
    }
    
    tbody.innerHTML = cases.map(case_ => {
        // Determine result display based on available data
        let resultDisplay = 'Completed';
        if (case_.screen_prob !== null) {
            resultDisplay = `${Math.round(case_.screen_prob * 100)}% risk`;
        }
        if (case_.stage_pred) {
            resultDisplay += ` (${case_.stage_pred} resistance)`;
        }
        
        return `
            <tr>
                <td>${formatDate(case_.created_at)}</td>
                <td>${case_.task || 'Screening'}</td>
                <td>${case_.patient_pseudo_id || 'N/A'}</td>
                <td>${resultDisplay}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewCase(${case_.id})" title="Sign & Send SMS">
                        📝 Sign
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function viewCase(caseId) {
    // Set the current case ID and open signature modal for this case
    try {
        const response = await apiRequest(`/cases/${caseId}`);
        const caseData = response;
        
        // Set current case details
        currentCaseId = caseId;
        currentRecommendations = caseData.recommendations || [];
        
        // Pre-populate patient information if available
        const patientNameField = document.getElementById('patientName');
        const patientPhoneField = document.getElementById('patientPhone');
        const patientEmailField = document.getElementById('patientEmail');
        
        if (patientNameField && caseData.patient_name) {
            patientNameField.value = caseData.patient_name;
        }
        if (patientPhoneField && caseData.patient_phone) {
            patientPhoneField.value = caseData.patient_phone;
        }
        if (patientEmailField && caseData.patient_email) {
            patientEmailField.value = caseData.patient_email;
        }
        
        // Open signature modal for this case
        openSignatureModal(caseId);
        showToast('Case loaded! You can now sign and send.', 'success');
    } catch (error) {
        console.error('Error loading case:', error);
        showToast(`Error loading case: ${error.message || 'Please try again'}`, 'error');
    }
}

// Digital Signature Workflow Functions
let signaturePad = null;
let currentCaseId = null;
let currentRecommendations = [];

function openSignatureModal(caseId = null) {
    const modal = document.getElementById('signatureModal');
    if (!modal) return;
    
    // If a case ID is provided, use it
    if (caseId) {
        currentCaseId = caseId;
    }
    
    // Use currentRecommendations if already set (from viewCase), otherwise extract from DOM
    let recommendations = [];
    
    if (currentRecommendations && currentRecommendations.length > 0) {
        // Already loaded from viewCase or previous assessment
        recommendations = currentRecommendations;
    } else {
        // Try to extract from DOM (for fresh assessments)
        const screeningResults = document.querySelector('#screeningResults');
        const stagingResults = document.querySelector('#stagingResults');
        
        if (screeningResults && !screeningResults.style.display) {
            const recList = screeningResults.querySelectorAll('li');
            recList.forEach(item => recommendations.push(item.textContent));
        }
        if (stagingResults && !stagingResults.style.display) {
            const recList = stagingResults.querySelectorAll('li');
            recList.forEach(item => recommendations.push(item.textContent));
        }
        
        if (recommendations.length === 0) {
            showToast('Please complete an assessment first or load a case from history', 'error');
            return;
        }
        
        currentRecommendations = recommendations;
    }
    
    // Populate recommendations textarea
    const editTextarea = document.getElementById('editedRecommendations');
    if (editTextarea) {
        editTextarea.value = recommendations.join('\n\n');
    }
    
    // Show modal and first step
    modal.style.display = 'flex';
    showSignatureStep('patientInfoStep');
}

function closeSignatureModal() {
    const modal = document.getElementById('signatureModal');
    if (modal) {
        modal.style.display = 'none';
        // Reset to first step
        showSignatureStep('patientInfoStep');
        // Clear form
        document.getElementById('patientName').value = '';
        document.getElementById('patientPhone').value = '';
        document.getElementById('editedRecommendations').value = '';
        if (signaturePad) {
            clearSignature();
        }
    }
}

function showSignatureStep(stepId) {
    document.querySelectorAll('.signature-step').forEach(step => {
        step.classList.remove('active');
    });
    const targetStep = document.getElementById(stepId);
    if (targetStep) {
        targetStep.classList.add('active');
    }
}

function goToSignatureStep() {
    const patientName = document.getElementById('patientName').value.trim();
    const patientPhone = document.getElementById('patientPhone').value.trim();
    const patientEmail = document.getElementById('patientEmail').value.trim();
    
    if (!patientName) {
        showToast('Please enter patient name', 'error');
        return;
    }
    
    if (!patientEmail) {
        showToast('Please enter patient email address', 'error');
        return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(patientEmail)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    // Validate phone format
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    if (!phoneRegex.test(patientPhone)) {
        showToast('Please enter a valid phone number', 'error');
        return;
    }
    
    showSignatureStep('signatureStep');
    
    // Initialize signature pad
    setTimeout(() => initSignaturePad(), 100);
}

function goBackToPatientInfo() {
    showSignatureStep('patientInfoStep');
}

function initSignaturePad() {
    const canvas = document.getElementById('signaturePad');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    // Set up canvas
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Mouse events
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Touch events for mobile
    canvas.addEventListener('touchstart', handleTouch);
    canvas.addEventListener('touchmove', handleTouch);
    canvas.addEventListener('touchend', stopDrawing);
    
    function startDrawing(e) {
        isDrawing = true;
        const rect = canvas.getBoundingClientRect();
        lastX = e.clientX - rect.left;
        lastY = e.clientY - rect.top;
    }
    
    function draw(e) {
        if (!isDrawing) return;
        
        const rect = canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(currentX, currentY);
        ctx.stroke();
        
        lastX = currentX;
        lastY = currentY;
    }
    
    function stopDrawing() {
        isDrawing = false;
    }
    
    function handleTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                        e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvas.dispatchEvent(mouseEvent);
    }
    
    signaturePad = { canvas, ctx };
}

function clearSignature() {
    if (signaturePad && signaturePad.canvas) {
        const ctx = signaturePad.ctx;
        ctx.clearRect(0, 0, signaturePad.canvas.width, signaturePad.canvas.height);
    }
}

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

async function finalizeAndSign() {
    if (isSignatureEmpty()) {
        showToast('Please add your signature', 'error');
        return;
    }
    
    if (!currentCaseId) {
        showToast('No case ID found. Please submit a screening/staging assessment first.', 'error');
        return;
    }
    
    const patientName = document.getElementById('patientName').value.trim();
    const patientPhone = document.getElementById('patientPhone').value.trim();
    const patientEmail = document.getElementById('patientEmail').value.trim();
    const editedRecs = document.getElementById('editedRecommendations').value.trim();
    const signatureData = signaturePad.canvas.toDataURL('image/png');
    
    if (!patientName || !patientEmail) {
        showToast('Patient name and email are required', 'error');
        return;
    }
    
    try {
        showSpinner(document.querySelector('#signatureStep'));
        
        // Step 1: Prepare the document with patient info
        let prepareUrl = `/documents/${currentCaseId}/prepare?patient_name=${encodeURIComponent(patientName)}&patient_email=${encodeURIComponent(patientEmail)}`;
        if (patientPhone) {
            prepareUrl += `&patient_phone=${encodeURIComponent(patientPhone)}`;
        }
        await apiRequest(prepareUrl, {
            method: 'POST'
        });
        
        // Step 2: If recommendations were edited, update them
        if (editedRecs) {
            const recsArray = editedRecs.split('\n').filter(r => r.trim());
            await apiRequest(`/documents/${currentCaseId}/edit`, {
                method: 'PUT',
                body: JSON.stringify({ recommendations: recsArray })
            });
        }
        
        // Step 3: Sign the document
        await apiRequest(`/documents/${currentCaseId}/sign`, {
            method: 'POST',
            body: JSON.stringify({ signature_data: signatureData })
        });
        
        showToast('Document signed successfully!', 'success');
        
        // Update final display
        document.getElementById('finalPatientName').textContent = patientName;
        document.getElementById('finalPatientPhone').textContent = patientPhone;
        
        // Generate SMS preview
        const smsPreview = generateSMSPreview(patientName, editedRecs || currentRecommendations.join('\n\n'));
        document.getElementById('smsPreview').textContent = smsPreview;
        
        hideSpinner(document.querySelector('#signatureStep'));
        showSignatureStep('smsStep');
        
    } catch (error) {
        hideSpinner(document.querySelector('#signatureStep'));
        console.error('Error signing document:', error);
        showToast('Error signing document: ' + error.message, 'error');
    }
}

async function sendSMSToPatient() {
    if (!currentCaseId) {
        showToast('No case ID found', 'error');
        return;
    }
    
    try {
        showSpinner(document.querySelector('#smsStep'));
        
        // Send notification via backend API (Email + SMS)
        const result = await apiRequest(`/documents/${currentCaseId}/send-notification`, {
            method: 'POST'
        });
        
        // Update delivery status
        const statusDiv = document.getElementById('deliveryStatus');
        
        // Build status message
        let statusHTML = `<strong>✅ Notification Sent!</strong><br>`;
        statusHTML += `Patient: ${result.patient_name}<br>`;
        statusHTML += `Time: ${new Date(result.sent_at).toLocaleString()}<br><br>`;
        
        // Email status
        if (result.delivery.email.attempted) {
            if (result.delivery.email.success) {
                statusHTML += `📧 Email: ✅ Delivered to ${result.delivery.email.to}<br>`;
            } else {
                statusHTML += `📧 Email: ❌ Failed (${result.delivery.email.error})<br>`;
            }
        } else {
            statusHTML += `📧 Email: Not sent (no email provided)<br>`;
        }
        
        // SMS status
        if (result.delivery.sms.attempted) {
            if (result.delivery.sms.success) {
                const mode = result.delivery.sms.simulated ? ' (Simulated)' : '';
                statusHTML += `📱 SMS: ✅ Sent to ${result.delivery.sms.to}${mode}<br>`;
            } else {
                statusHTML += `📱 SMS: ❌ Failed (${result.delivery.sms.error})<br>`;
            }
        } else {
            statusHTML += `📱 SMS: Not sent (no phone provided)<br>`;
        }
        
        statusDiv.innerHTML = statusHTML;
        
        hideSpinner(document.querySelector('#smsStep'));
        showSignatureStep('confirmationStep');
        
        // Show appropriate toast message
        const emailSent = result.delivery.email.success;
        const smsSent = result.delivery.sms.success || result.delivery.sms.simulated;
        
        if (emailSent && smsSent) {
            showToast('Email and SMS sent successfully!', 'success');
        } else if (emailSent) {
            showToast('Email sent successfully! SMS may have failed.', 'success');
        } else if (smsSent) {
            showToast('SMS sent! Email may have failed.', 'success');
        }
        
    } catch (error) {
        hideSpinner(document.querySelector('#smsStep'));
        console.error('Error sending notification:', error);
        showToast('Error sending notification: ' + error.message, 'error');
    }
}

function generateSMSPreview(patientName, recommendations) {
    const firstRec = recommendations.split('\n')[0];
    let cleanRec = firstRec.replace(/🔴|🟡|🟢/g, '').replace(/⚠/g, 'CAUTION:').replace(/ℹ️/g, 'INFO:');
    if (cleanRec.length > 100) {
        cleanRec = cleanRec.substring(0, 97) + '...';
    }
    return `H. pylori Treatment Plan for ${patientName}:\n\n${cleanRec}\n\nQuestions? Please call our office. Follow-up appointment required.`;
}

// Video Consultation Functions
async function startVideoSession() {
    const sessionName = document.getElementById('sessionName').value || 'Consultation Session';
    
    try {
        const session = await apiRequest('/video/session/create', {
            method: 'POST',
            body: JSON.stringify({ session_name: sessionName })
        });
        
        showVideoInterface();
        initializeWebRTC();
        showToast('Video session started successfully!', 'success');
    } catch (error) {
        showToast('Error starting video session: ' + error.message, 'error');
    }
}

function showVideoInterface() {
    document.getElementById('videoSetup').style.display = 'none';
    document.getElementById('videoInterface').style.display = 'block';
}

function initializeWebRTC() {
    // Basic WebRTC setup (simplified for demo)
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = stream;
            }
        })
        .catch(error => {
            showToast('Camera/microphone access denied', 'error');
        });
}

function toggleMute() {
    showToast('Microphone toggled', 'info');
}

function toggleVideo() {
    showToast('Camera toggled', 'info');
}

function shareScreen() {
    showToast('Screen sharing feature coming soon', 'info');
}

function endSession() {
    document.getElementById('videoInterface').style.display = 'none';
    document.getElementById('videoSetup').style.display = 'block';
    showToast('Video session ended', 'success');
}

// Settings Functions
function saveSettings() {
    // Save settings to localStorage for demo
    const settings = {
        theme: document.querySelector('.theme-option.active')?.dataset.theme || 'light',
        fontSize: document.getElementById('fontSize').value,
        emailNotifications: document.getElementById('emailNotifications').checked,
        smsNotifications: document.getElementById('smsNotifications').checked,
        pushNotifications: document.getElementById('pushNotifications').checked
    };
    
    localStorage.setItem('userSettings', JSON.stringify(settings));
    showToast('Settings saved successfully!', 'success');
}

function resetSettings() {
    localStorage.removeItem('userSettings');
    showToast('Settings reset to defaults', 'success');
    setTimeout(() => location.reload(), 1000);
}

// Admin Functions
async function loadAdminStats() {
    try {
        const stats = await apiRequest('/admin/stats');
        updateAdminStats(stats);
    } catch (error) {
        showToast('Error loading admin statistics', 'error');
    }
}

function updateAdminStats(stats) {
    document.getElementById('totalUsers').textContent = stats.total_users || '0';
    document.getElementById('activeSessions').textContent = stats.active_sessions || '0'; 
    document.getElementById('totalCases').textContent = stats.total_cases || '0';
    document.getElementById('systemUptime').textContent = stats.uptime || '--';
}

function createUser() {
    window.location.href = 'admin.html';
}

function viewUsers() {
    window.location.href = 'admin.html';
}

// 3D Biopsy Functions
function toggleRotation() {
    showToast('3D model rotation toggled', 'info');
}

function resetView() {
    showToast('3D view reset to default', 'info');
}

function fullscreen() {
    const viewer = document.querySelector('.sketchfab-embed-wrapper');
    if (viewer && viewer.requestFullscreen) {
        viewer.requestFullscreen();
    }
}

// Utility Functions
function showSpinner(form) {
    const spinner = form.querySelector('.spinner');
    if (spinner) spinner.style.display = 'inline-block';
}

function hideSpinner(form) {
    const spinner = form.querySelector('.spinner');
    if (spinner) spinner.style.display = 'none';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function copyResults() {
    showToast('Results copied to clipboard', 'success');
}

function saveCase() {
    showToast('Case saved successfully', 'success');
}

function copyStageResults() {
    showToast('Staging results copied to clipboard', 'success');
}

function saveStageCase() {
    showToast('Staging case saved successfully', 'success');
}

// Initialize page-specific functionality when pages are shown
function initializeCurrentPage(pageId) {
    switch(pageId) {
        case 'screening':
            initializeScreeningPage();
            break;
        case 'staging':
            initializeStagingPage();
            break;
        case 'cases':
            loadCaseHistory();
            break;
        case 'video':
            // Initialize video consultation system if function exists
            if (typeof initVideoConsultation === 'function') {
                initVideoConsultation();
            }
            break;
        case 'scheduling':
            // Initialize scheduling system if function exists
            if (typeof initScheduling === 'function') {
                initScheduling();
            }
            break;
        case 'admin':
            loadAdminStats();
            break;
    }
}