// ========================================
// PROFESSIONAL MEDICAL DASHBOARD
// Dark/Light Mode, Charts, Real-time Updates
// ========================================

const API_BASE = 'http://localhost:8000';
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
        
        // User avatar is now an icon - no need to set image source
        
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
    
    // Profile avatar is now an icon - no need to set image source
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
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${authToken}`,
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
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
}
