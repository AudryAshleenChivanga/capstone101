/**
 * Enhanced Case Management with Filtering, Pagination, and CRUD Operations
 */

// Global state for pagination and filtering
let currentPage = 1;
let pageSize = 10;
let currentFilters = {};
let currentUserRole = null;

/**
 * Load case history with filters and pagination
 */
async function loadCaseHistory(page = 1) {
    currentPage = page;
    
    try {
        // Build query parameters
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize,
            ...currentFilters
        });
        
        const token = localStorage.getItem('token');
        const response = await fetch(`/cases?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load cases');
        }
        
        const data = await response.json();
        
        // Update statistics
        updateStatistics(data);
        
        // Render table
        renderCaseTable(data.cases);
        
        // Update pagination
        updatePagination(data.page, data.total_pages, data.total);
        
    } catch (error) {
        console.error('Error loading case history:', error);
        showToast('Error loading case history', 'error');
    }
}

/**
 * Update statistics dashboard
 */
function updateStatistics(data) {
    const cases = data.cases || [];
    
    // Calculate statistics
    const total = cases.length;
    const highRisk = cases.filter(c => c.risk_level === 'high').length;
    const screenings = cases.filter(c => c.case_type === 'screening').length;
    const stagings = cases.filter(c => c.case_type === 'staging').length;
    
    // Update UI
    document.getElementById('statTotalCases').textContent = total;
    document.getElementById('statHighRisk').textContent = highRisk;
    document.getElementById('statScreenings').textContent = screenings;
    document.getElementById('statStagings').textContent = stagings;
}

/**
 * Render case table
 */
function renderCaseTable(cases) {
    const tbody = document.getElementById('caseTableBody');
    
    if (!cases || cases.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.6);">
                    No cases found matching your filters.
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = cases.map(caseItem => {
        const date = new Date(caseItem.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const riskBadge = getRiskBadge(caseItem.risk_level);
        const typeBadge = getTypeBadge(caseItem.case_type);
        
        const result = caseItem.case_type === 'screening' 
            ? `${(caseItem.screen_prob * 100).toFixed(1)}%`
            : caseItem.stage_pred || 'N/A';
        
        return `
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); transition: background 0.3s;" onmouseover="this.style.background='rgba(0, 212, 255, 0.05)'" onmouseout="this.style.background='transparent'">
                <td style="padding: 15px;">${date}</td>
                <td style="padding: 15px; font-weight: 600; color: #00d4ff;">${caseItem.patient_id || 'N/A'}</td>
                <td style="padding: 15px;">${caseItem.patient_name || 'Unknown'}</td>
                <td style="padding: 15px;">${typeBadge}</td>
                <td style="padding: 15px;">${riskBadge}</td>
                <td style="padding: 15px; font-weight: 600;">${result}</td>
                <td style="padding: 15px; font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">${caseItem.clinician_name || 'Unknown'}</td>
                <td style="padding: 15px; text-align: center;">
                    <div style="display: flex; gap: 8px; justify-content: center;">
                        <button onclick="viewCaseDetail(${caseItem.id})" class="btn-icon" title="View Details" style="padding: 8px; background: rgba(0, 150, 255, 0.2); border: 1px solid rgba(0, 150, 255, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                            👁️
                        </button>
                        ${currentUserRole === 'admin' ? `
                            <button onclick="editCase(${caseItem.id})" class="btn-icon" title="Edit" style="padding: 8px; background: rgba(255, 193, 7, 0.2); border: 1px solid rgba(255, 193, 7, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                                ✏️
                            </button>
                            <button onclick="deleteCase(${caseItem.id})" class="btn-icon" title="Delete" style="padding: 8px; background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                                🗑️
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Get risk badge HTML
 */
function getRiskBadge(riskLevel) {
    const badges = {
        'high': '<span style="padding: 4px 12px; background: linear-gradient(135deg, #ff6b6b, #ee5a52); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: white;">⚠️ High</span>',
        'moderate': '<span style="padding: 4px 12px; background: linear-gradient(135deg, #ffd93d, #f9c74f); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: #000;">⚡ Moderate</span>',
        'low': '<span style="padding: 4px 12px; background: linear-gradient(135deg, #6bcf7f, #51cf66); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: white;">✓ Low</span>',
        'unknown': '<span style="padding: 4px 12px; background: rgba(128, 128, 128, 0.3); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: white;">N/A</span>'
    };
    return badges[riskLevel] || badges['unknown'];
}

/**
 * Get type badge HTML
 */
function getTypeBadge(type) {
    const badges = {
        'screening': '<span style="padding: 4px 12px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: white;">🔬 Screening</span>',
        'staging': '<span style="padding: 4px 12px; background: linear-gradient(135deg, #f093fb, #f5576c); border-radius: 12px; font-size: 0.85rem; font-weight: 600; color: white;">📊 Staging</span>'
    };
    return badges[type] || '<span style="padding: 4px 12px; background: rgba(128, 128, 128, 0.3); border-radius: 12px; font-size: 0.85rem;">Unknown</span>';
}

/**
 * Update pagination controls
 */
function updatePagination(page, totalPages, total) {
    document.getElementById('currentPage').textContent = page;
    document.getElementById('totalPages').textContent = totalPages;
    document.getElementById('paginationInfo').textContent = total;
    
    // Disable/enable buttons
    document.getElementById('btnPrevPage').disabled = page === 1;
    document.getElementById('btnNextPage').disabled = page === totalPages;
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters = {
        search: document.getElementById('filterSearch').value,
        case_type: document.getElementById('filterCaseType').value,
        risk_level: document.getElementById('filterRiskLevel').value,
        start_date: document.getElementById('filterStartDate').value,
        end_date: document.getElementById('filterEndDate').value
    };
    
    // Remove empty filters
    Object.keys(currentFilters).forEach(key => {
        if (!currentFilters[key]) delete currentFilters[key];
    });
    
    loadCaseHistory(1); // Reset to page 1 when filtering
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    document.getElementById('filterSearch').value = '';
    document.getElementById('filterCaseType').value = '';
    document.getElementById('filterRiskLevel').value = '';
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    
    currentFilters = {};
    loadCaseHistory(1);
}

/**
 * Pagination functions
 */
function nextPage() {
    loadCaseHistory(currentPage + 1);
}

function previousPage() {
    if (currentPage > 1) {
        loadCaseHistory(currentPage - 1);
    }
}

/**
 * View case detail
 */
async function viewCaseDetail(caseId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/cases/${caseId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load case details');
        }
        
        const caseData = await response.json();
        
        // Show modal with case details
        showCaseDetailModal(caseData);
        
    } catch (error) {
        console.error('Error loading case details:', error);
        showToast('Error loading case details', 'error');
    }
}

/**
 * Show case detail modal
 */
function showCaseDetailModal(caseData) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(5px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 16px; max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 30px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #00d4ff;">📋 Case Details</h2>
                <button onclick="this.closest('div[style*=fixed]').remove()" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-size: 1.2rem;">✕</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Patient ID</label>
                    <div style="color: white; font-weight: 600; font-size: 1.1rem; margin-bottom: 15px;">${caseData.patient_id || 'N/A'}</div>
                </div>
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Patient Name</label>
                    <div style="color: white; font-weight: 600; font-size: 1.1rem; margin-bottom: 15px;">${caseData.patient_name || 'N/A'}</div>
                </div>
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Case Type</label>
                    <div style="color: white; font-weight: 600; margin-bottom: 15px;">${caseData.task}</div>
                </div>
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Created Date</label>
                    <div style="color: white; font-weight: 600; margin-bottom: 15px;">${new Date(caseData.created_at).toLocaleString()}</div>
                </div>
                ${caseData.screen_prob ? `
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Screening Probability</label>
                    <div style="color: white; font-weight: 600; margin-bottom: 15px;">${(caseData.screen_prob * 100).toFixed(1)}%</div>
                </div>
                ` : ''}
                ${caseData.stage_pred ? `
                <div>
                    <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Stage Prediction</label>
                    <div style="color: white; font-weight: 600; margin-bottom: 15px;">${caseData.stage_pred}</div>
                </div>
                ` : ''}
            </div>
            
            <div style="margin-top: 20px;">
                <label style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 10px; display: block;">Recommendations</label>
                <ul style="color: white; padding-left: 20px;">
                    ${caseData.recommendations.map(rec => `<li style="margin-bottom: 8px;">${rec}</li>`).join('')}
                </ul>
            </div>
            
            <div style="margin-top: 30px; text-align: right;">
                <button onclick="this.closest('div[style*=fixed]').remove()" class="btn btn-secondary">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

/**
 * Edit case (admin only)
 */
async function editCase(caseId) {
    const notes = prompt('Enter notes for this case:');
    if (notes === null) return;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/cases/${caseId}?notes=${encodeURIComponent(notes)}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to update case');
        }
        
        showToast('Case updated successfully', 'success');
        loadCaseHistory(currentPage);
        
    } catch (error) {
        console.error('Error updating case:', error);
        showToast('Error updating case', 'error');
    }
}

/**
 * Delete case (admin only)
 */
async function deleteCase(caseId) {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/cases/${caseId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete case');
        }
        
        showToast('Case deleted successfully', 'success');
        loadCaseHistory(currentPage);
        
    } catch (error) {
        console.error('Error deleting case:', error);
        showToast('Error deleting case', 'error');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const bgColors = {
        'success': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'error': 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
        'info': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    };
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColors[type] || bgColors.info};
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10001;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Get current user role
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    currentUserRole = user.role;
    
    // Load cases when cases page is active
    if (window.location.hash === '#cases' || document.querySelector('.nav-item[data-page="cases"]')?.classList.contains('active')) {
        loadCaseHistory();
    }
});

