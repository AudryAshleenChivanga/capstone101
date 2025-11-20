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
            <tr style="border-bottom: 1px solid rgba(128, 128, 128, 0.2); transition: background 0.3s;" onmouseover="this.style.background='rgba(0, 212, 255, 0.05)'" onmouseout="this.style.background='transparent'">
                <td style="padding: 15px;">${date}</td>
                <td style="padding: 15px; font-weight: 600; color: #00d4ff;">${caseItem.patient_id || 'N/A'}</td>
                <td style="padding: 15px;">${caseItem.patient_name || 'Unknown'}</td>
                <td style="padding: 15px;">${typeBadge}</td>
                <td style="padding: 15px;">${riskBadge}</td>
                <td style="padding: 15px; font-weight: 600;">${result}</td>
                <td style="padding: 15px; font-size: 0.9rem; font-weight: 500;">${caseItem.clinician_name || 'Unknown'}</td>
                <td style="padding: 15px; text-align: center;">
                    <div style="display: flex; gap: 8px; justify-content: center;">
                        <button onclick="viewCaseDetail(${caseItem.id})" class="btn-icon" title="View Details" style="padding: 8px; background: rgba(0, 150, 255, 0.2); border: 1px solid rgba(0, 150, 255, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                            👁️
                        </button>
                        <button onclick="generateCasePDF(${caseItem.id})" class="btn-icon" title="Download PDF Report" style="padding: 8px; background: rgba(76, 175, 80, 0.2); border: 1px solid rgba(76, 175, 80, 0.5); border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                            📄
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
    // Create modal for case editing
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;';
    
    modal.innerHTML = `
        <div class="modal-content" style="background: var(--bg-secondary); border-radius: 16px; padding: 32px; max-width: 600px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
                <h2 style="margin: 0; color: var(--text-primary); font-size: 24px;">Edit Case #${caseId}</h2>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 28px; cursor: pointer; color: var(--text-secondary); padding: 0; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.background='var(--bg-tertiary)'" onmouseout="this.style.background='none'">&times;</button>
            </div>
            
            <form id="editCaseForm" style="display: flex; flex-direction: column; gap: 20px;">
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <label style="color: var(--text-primary); font-weight: 600; font-size: 14px;">Case Notes</label>
                    <textarea 
                        id="caseNotes" 
                        rows="6" 
                        placeholder="Enter notes about this case..."
                        style="padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-primary); font-family: inherit; font-size: 14px; resize: vertical; transition: border-color 0.2s;"
                        onfocus="this.style.borderColor='var(--primary)'"
                        onblur="this.style.borderColor='var(--border-color)'"
                    ></textarea>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <label style="color: var(--text-primary); font-weight: 600; font-size: 14px;">Status</label>
                    <select 
                        id="caseStatus"
                        style="padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-primary); font-family: inherit; font-size: 14px; cursor: pointer; transition: border-color 0.2s;"
                        onfocus="this.style.borderColor='var(--primary)'"
                        onblur="this.style.borderColor='var(--border-color)'"
                    >
                        <option value="pending">Pending Review</option>
                        <option value="reviewed">Reviewed</option>
                        <option value="approved">Approved</option>
                        <option value="follow-up">Needs Follow-up</option>
                    </select>
                </div>
                
                <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px;">
                    <button 
                        type="button" 
                        onclick="this.closest('.modal-overlay').remove()"
                        style="padding: 12px 24px; border: 2px solid var(--border-color); border-radius: 8px; background: transparent; color: var(--text-primary); font-weight: 600; cursor: pointer; transition: all 0.2s;"
                        onmouseover="this.style.background='var(--bg-tertiary)'"
                        onmouseout="this.style.background='transparent'"
                    >
                        Cancel
                    </button>
                    <button 
                        type="submit"
                        style="padding: 12px 24px; border: none; border-radius: 8px; background: var(--primary); color: white; font-weight: 600; cursor: pointer; transition: all 0.2s;"
                        onmouseover="this.style.opacity='0.9'"
                        onmouseout="this.style.opacity='1'"
                    >
                        Save Changes
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle form submission
    document.getElementById('editCaseForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const notes = document.getElementById('caseNotes').value;
        const status = document.getElementById('caseStatus').value;
        
        if (!notes.trim()) {
            showToast('Please enter some notes', 'warning');
            return;
        }
        
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
            modal.remove();
            loadCaseHistory(currentPage);
            
        } catch (error) {
            console.error('Error updating case:', error);
            showToast('Error updating case: ' + error.message, 'error');
        }
    });
    
    // Focus on textarea
    setTimeout(() => document.getElementById('caseNotes').focus(), 100);
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

/**
 * Generate and download PDF for a specific case
 */
async function generateCasePDF(caseId) {
    try {
        const token = localStorage.getItem('token');
        
        // Show loading toast
        showToast('Generating PDF report...', 'info');
        
        // Call the PDF generation endpoint
        const response = await fetch(`/documents/${caseId}/generate-pdf`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            
            // Check if the error is about missing signature
            if (response.status === 400 && errorData.detail?.includes('signed')) {
                showToast('⚠️ Document must be signed before generating PDF. Please complete the signature workflow first.', 'error');
                return;
            }
            
            throw new Error(errorData.detail || 'Failed to generate PDF');
        }
        
        // Get the PDF blob
        const blob = await response.blob();
        
        // Extract filename from headers or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `case_${caseId}_report.pdf`;
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showToast('✅ PDF report downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('Error generating PDF:', error);
        showToast('Error generating PDF: ' + error.message, 'error');
    }
}

/**
 * Generate report from the main button (bulk export or summary)
 */
async function generateCaseReport() {
    // Show a modal to let user choose report type
    const reportType = await showReportTypeModal();
    
    if (!reportType) return; // User cancelled
    
    if (reportType === 'summary') {
        // Generate summary report for all filtered cases
        generateSummaryReport();
    } else if (reportType === 'select') {
        // Show case selection modal
        showCaseSelectionModal();
    }
}

/**
 * Show modal to select report type
 */
function showReportTypeModal() {
    return new Promise((resolve) => {
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
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 16px; max-width: 500px; width: 100%; padding: 30px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);">
                <h2 style="margin: 0 0 20px 0; color: #00d4ff;">📊 Generate Report</h2>
                <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 25px;">Choose the type of report you want to generate:</p>
                
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <button onclick="this.closest('div[style*=fixed]').dataset.result='summary'; this.closest('div[style*=fixed]').remove();" 
                        style="padding: 15px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1rem;">
                        📋 Summary Report (All Cases)
                    </button>
                    
                    <button onclick="this.closest('div[style*=fixed]').dataset.result='select'; this.closest('div[style*=fixed]').remove();" 
                        style="padding: 15px 20px; background: linear-gradient(135deg, #f093fb, #f5576c); border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1rem;">
                        ✅ Select Specific Cases
                    </button>
                    
                    <button onclick="this.closest('div[style*=fixed]').dataset.result='cancel'; this.closest('div[style*=fixed]').remove();" 
                        style="padding: 15px 20px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 8px; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1rem;">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Wait for user selection
        const checkResult = setInterval(() => {
            if (modal.dataset.result) {
                clearInterval(checkResult);
                const result = modal.dataset.result === 'cancel' ? null : modal.dataset.result;
                resolve(result);
            }
        }, 100);
    });
}

/**
 * Generate summary report for all cases (CSV export)
 */
async function generateSummaryReport() {
    try {
        showToast('Generating summary report...', 'info');
        
        // Get all cases (without pagination limit)
        const token = localStorage.getItem('token');
        const response = await fetch('/cases?limit=1000', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch cases');
        }
        
        const data = await response.json();
        const cases = data.cases || [];
        
        if (cases.length === 0) {
            showToast('No cases to export', 'error');
            return;
        }
        
        // Convert to CSV
        const headers = ['Date', 'Patient ID', 'Patient Name', 'Type', 'Risk Level', 'Result', 'Clinician'];
        const rows = cases.map(c => [
            new Date(c.created_at).toLocaleDateString(),
            c.patient_id || 'N/A',
            c.patient_name || 'Unknown',
            c.case_type,
            c.risk_level,
            c.case_type === 'screening' ? `${(c.screen_prob * 100).toFixed(1)}%` : c.stage_pred,
            c.clinician_name || 'Unknown'
        ]);
        
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `case_summary_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showToast(`✅ Summary report exported (${cases.length} cases)`, 'success');
        
    } catch (error) {
        console.error('Error generating summary report:', error);
        showToast('Error generating report: ' + error.message, 'error');
    }
}

/**
 * Show modal to select specific cases for PDF generation
 */
async function showCaseSelectionModal() {
    try {
        // Get all cases
        const token = localStorage.getItem('token');
        const response = await fetch('/cases?limit=100', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch cases');
        }
        
        const data = await response.json();
        const cases = data.cases || [];
        
        if (cases.length === 0) {
            showToast('No cases available', 'error');
            return;
        }
        
        // Create modal
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
        
        const casesList = cases.map(c => `
            <label style="display: flex; align-items: center; padding: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; cursor: pointer; transition: all 0.3s; margin-bottom: 10px;" onmouseover="this.style.background='rgba(0, 212, 255, 0.1)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.05)'">
                <input type="checkbox" value="${c.id}" style="margin-right: 12px; width: 18px; height: 18px; cursor: pointer;">
                <div style="flex: 1;">
                    <div style="color: white; font-weight: 600;">${c.patient_name || c.patient_id || 'Case #' + c.id}</div>
                    <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">${new Date(c.created_at).toLocaleDateString()} - ${c.case_type}</div>
                </div>
            </label>
        `).join('');
        
        modal.innerHTML = `
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 16px; max-width: 600px; width: 100%; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);">
                <div style="padding: 30px 30px 20px 30px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                    <h2 style="margin: 0; color: #00d4ff;">📄 Select Cases for PDF Export</h2>
                    <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0;">Select one or more cases to download as PDF reports:</p>
                </div>
                
                <div style="flex: 1; overflow-y: auto; padding: 20px 30px;">
                    ${casesList}
                </div>
                
                <div style="padding: 20px 30px; border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; gap: 15px; justify-content: flex-end;">
                    <button onclick="this.closest('div[style*=fixed]').remove()" style="padding: 12px 24px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 8px; color: white; font-weight: 600; cursor: pointer;">
                        Cancel
                    </button>
                    <button onclick="downloadSelectedCases(this)" style="padding: 12px 24px; background: linear-gradient(135deg, #43e97b, #38f9d7); border: none; border-radius: 8px; color: #1e293b; font-weight: 600; cursor: pointer;">
                        Download Selected PDFs
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Error loading cases:', error);
        showToast('Error loading cases: ' + error.message, 'error');
    }
}

/**
 * Download PDFs for selected cases
 */
window.downloadSelectedCases = async function(button) {
    const modal = button.closest('div[style*=fixed]');
    const checkboxes = modal.querySelectorAll('input[type=checkbox]:checked');
    
    if (checkboxes.length === 0) {
        showToast('Please select at least one case', 'error');
        return;
    }
    
    const caseIds = Array.from(checkboxes).map(cb => cb.value);
    
    // Close modal
    modal.remove();
    
    // Download each case PDF
    showToast(`Downloading ${caseIds.length} PDF report(s)...`, 'info');
    
    for (let i = 0; i < caseIds.length; i++) {
        await generateCasePDF(caseIds[i]);
        // Small delay between downloads to avoid overwhelming the browser
        if (i < caseIds.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
};

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

