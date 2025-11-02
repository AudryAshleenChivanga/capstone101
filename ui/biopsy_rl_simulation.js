/**
 * RL-Based 3D Endoscopy/Biopsy Simulation
 * Connects to FastAPI backend with trained Q-Learning agent
 */

// API Configuration
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// Get authentication token
const authToken = localStorage.getItem('token');

// Simulation State
let simulationState = {
    isRunning: false,
    currentStep: 0,
    biopsiesCollected: [],
    tissueGrid: [],
    currentPosition: { x: 5, y: 5 },
    procedureLog: []
};

/**
 * Initialize the application
 */
function init() {
    console.log('Initializing RL Biopsy Simulation...');
    
    // Check authentication (optional - will work without login for demo)
    if (!authToken) {
        console.warn('No auth token found - some features may be limited');
    }
    
    // Generate initial tissue grid
    generateTissueGrid();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load agent statistics (if authenticated)
    if (authToken) {
        loadAgentStats();
    }
    
    console.log('Simulation ready');
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Start simulation button
    document.getElementById('startSimBtn').addEventListener('click', startSimulation);
    
    // Reset button
    document.getElementById('resetBtn').addEventListener('click', resetSimulation);
    
    // View toggle buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const view = e.target.dataset.view;
            if (view === '3d') {
                load3DView();
            } else {
                document.getElementById('tissueGrid').style.display = 'grid';
            }
        });
    });
}

/**
 * Generate tissue grid visualization
 */
function generateTissueGrid() {
    const grid = document.getElementById('tissueGrid');
    grid.innerHTML = '';
    
    // Create 10x10 grid
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < 10; j++) {
            const cell = document.createElement('div');
            cell.className = 'tissue-cell';
            cell.dataset.x = i;
            cell.dataset.y = j;
            cell.innerHTML = `<span>${i},${j}</span>`;
            
            // Highlight starting position
            if (i === 5 && j === 5) {
                cell.classList.add('current');
            }
            
            grid.appendChild(cell);
        }
    }
}

/**
 * Load agent statistics from backend
 */
async function loadAgentStats() {
    try {
        const headers = {};
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        const response = await fetch(`${API_BASE}/biopsy/agent-stats`, {
            headers: headers
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Agent stats:', data);
            
            // Update UI with agent info
            const agentInfo = data.agent_info;
            console.log(`Q-Learning Agent: ${agentInfo.q_table_size} states learned`);
        } else {
            console.warn('Could not load agent stats (authentication may be required)');
        }
    } catch (error) {
        console.error('Failed to load agent stats:', error);
    }
}

/**
 * Start RL-based simulation
 */
async function startSimulation() {
    if (simulationState.isRunning) {
        showNotification('Simulation already running', 'warning');
        return;
    }
    
    const startBtn = document.getElementById('startSimBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="loading-spinner"></span> Running Simulation...';
    
    simulationState.isRunning = true;
    
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        const response = await fetch(`${API_BASE}/biopsy/simulate`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                simulation_steps: 30,
                difficulty: 'medium'
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Simulation request failed');
        }
        
        const result = await response.json();
        console.log('Simulation complete:', result);
        
        // Animate simulation steps
        await animateSimulation(result);
        
        // Show final results
        displayResults(result);
        
        showNotification('Simulation completed successfully', 'success');
        
    } catch (error) {
        console.error('Simulation error:', error);
        showNotification('Simulation failed: ' + error.message, 'error');
    } finally {
        simulationState.isRunning = false;
        startBtn.disabled = false;
        startBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Start RL Simulation
        `;
    }
}

/**
 * Animate simulation steps with visual feedback
 */
async function animateSimulation(result) {
    const procedureLog = result.procedure_log;
    const grid = document.getElementById('tissueGrid');
    
    for (let i = 0; i < procedureLog.length; i++) {
        const step = procedureLog[i];
        
        // Update current position
        updatePosition(step.position);
        
        // Update step counter
        document.getElementById('stepCount').textContent = step.step + 1;
        
        // If biopsy action, mark cell
        if (step.action === 'biopsy') {
            const cell = grid.querySelector(`[data-x="${step.position[0]}"][data-y="${step.position[1]}"]`);
            if (cell) {
                cell.classList.add('sampled');
                
                // Check infection level
                if (step.tissue_value > 0.6) {
                    cell.classList.add('high-infection');
                }
            }
        }
        
        // Wait for animation
        await sleep(200);
    }
    
    // Update final metrics
    document.getElementById('biopsyCount').textContent = result.biopsies_collected.length;
    
    if (result.analysis) {
        const avgInfection = (result.analysis.average_infection_probability * 100).toFixed(1);
        const confidence = (result.analysis.confidence * 100).toFixed(0);
        
        document.getElementById('avgInfection').textContent = avgInfection + '%';
        document.getElementById('confidence').textContent = confidence + '%';
    }
}

/**
 * Update position visualization
 */
function updatePosition(position) {
    const [x, y] = position;
    const grid = document.getElementById('tissueGrid');
    
    // Remove previous current marker
    grid.querySelectorAll('.tissue-cell.current').forEach(cell => {
        cell.classList.remove('current');
    });
    
    // Add current marker
    const cell = grid.querySelector(`[data-x="${x}"][data-y="${y}"]`);
    if (cell) {
        cell.classList.add('current');
    }
}

/**
 * Display final results and analysis
 */
function displayResults(result) {
    const resultsDiv = document.getElementById('biopsyResults');
    const analysisDiv = document.getElementById('analysisReport');
    
    // Display biopsy cards
    const biopsies = result.biopsies_collected;
    resultsDiv.innerHTML = '';
    
    biopsies.forEach((biopsy, index) => {
        const card = createBiopsyCard(biopsy, index + 1);
        resultsDiv.appendChild(card);
    });
    
    // Display analysis report
    const analysis = result.analysis;
    analysisDiv.classList.remove('hidden');
    analysisDiv.innerHTML = `
        <h4>Clinical Analysis Report</h4>
        <div class="biopsy-details">
            <strong>Severity:</strong> <span style="color: ${getSeverityColor(analysis.risk_level)}">${analysis.severity}</span><br>
            <strong>Infection Probability:</strong> ${(analysis.maximum_infection_probability * 100).toFixed(1)}%<br>
            <strong>Sample Quality:</strong> ${analysis.findings.sample_quality}<br>
            <strong>H. pylori Detected:</strong> ${analysis.findings.h_pylori_detected ? 'Yes' : 'No'}<br>
            <strong>Inflammation:</strong> ${analysis.findings.inflammation_present ? 'Present' : 'Absent'}<br>
            <strong>Tissue Integrity:</strong> ${analysis.findings.tissue_integrity}
        </div>
        <div class="recommendation">
            <strong>Clinical Recommendation:</strong><br>
            ${analysis.recommendation}
        </div>
    `;
}

/**
 * Create biopsy card element
 */
function createBiopsyCard(biopsy, index) {
    const card = document.createElement('div');
    card.className = 'biopsy-card';
    
    const infectionLevel = biopsy.infection_probability;
    let badgeClass = 'low';
    let badgeText = 'Low';
    
    if (infectionLevel > 0.6) {
        badgeClass = 'high';
        badgeText = 'High';
    } else if (infectionLevel > 0.3) {
        badgeClass = 'moderate';
        badgeText = 'Moderate';
    }
    
    card.innerHTML = `
        <div class="biopsy-header">
            <span class="biopsy-id">Sample ${index}</span>
            <span class="infection-badge ${badgeClass}">${badgeText} Risk</span>
        </div>
        <div class="biopsy-details">
            <strong>Position:</strong> (${biopsy.position[0]}, ${biopsy.position[1]})<br>
            <strong>Infection Probability:</strong> ${(infectionLevel * 100).toFixed(1)}%<br>
            <strong>Tissue Quality:</strong> ${biopsy.tissue_quality.charAt(0).toUpperCase() + biopsy.tissue_quality.slice(1)}
        </div>
    `;
    
    return card;
}

/**
 * Reset simulation to initial state
 */
function resetSimulation() {
    simulationState = {
        isRunning: false,
        currentStep: 0,
        biopsiesCollected: [],
        tissueGrid: [],
        currentPosition: { x: 5, y: 5 },
        procedureLog: []
    };
    
    // Reset UI
    document.getElementById('biopsyCount').textContent = '0';
    document.getElementById('stepCount').textContent = '0';
    document.getElementById('avgInfection').textContent = '0%';
    document.getElementById('confidence').textContent = '0%';
    
    document.getElementById('biopsyResults').innerHTML = 
        '<p style="color: #9B8FC9; font-size: 13px;">Start simulation to collect biopsy samples and view results.</p>';
    
    document.getElementById('analysisReport').classList.add('hidden');
    
    // Regenerate grid
    generateTissueGrid();
    
    showNotification('Simulation reset', 'info');
}

/**
 * Load 3D view (Sketchfab model)
 */
function load3DView() {
    const gridDiv = document.getElementById('tissueGrid');
    gridDiv.style.display = 'none';
    
    const container = document.getElementById('canvas-container');
    
    // Check if iframe already exists
    if (!document.getElementById('sketchfab-embed')) {
        const iframe = document.createElement('iframe');
        iframe.id = 'sketchfab-embed';
        iframe.title = '3D H. pylori Model';
        iframe.frameBorder = '0';
        iframe.allowFullscreen = true;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.src = 'https://sketchfab.com/models/c98532301b3f42f8b5ecf2e0063e9d73/embed?autostart=1&autospin=0.3&camera=0&ui_theme=dark&ui_hint=0&ui_controls=1&ui_infos=0&ui_inspector=0&ui_stop=0&ui_watermark=0&ui_watermark_link=0&ui_help=0&ui_settings=0&ui_vr=0&ui_ar=0&ui_fullscreen=1&ui_annotations=0&transparent=1&preload=1&dnt=1';
        
        container.appendChild(iframe);
    } else {
        document.getElementById('sketchfab-embed').style.display = 'block';
    }
}

/**
 * Utility functions
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getSeverityColor(riskLevel) {
    switch(riskLevel) {
        case 'high': return '#EF4444';
        case 'moderate': return '#F59E0B';
        case 'low': return '#10B981';
        default: return '#9B8FC9';
    }
}

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Could add toast notifications here
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

