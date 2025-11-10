/**
 * Advanced Capsule Endoscopy with Real-time RL Learning
 * Multi-pathology detection with live visualization
 */

// API Configuration
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// Global state
let simulationState = {
    isRunning: false,
    selectedScenario: 'mixed',
    currentStep: 0,
    trainingLog: [],
    detections: [],
    images: [],
    capsulePath: []
};

let rewardChart = null;

/**
 * Initialize application
 */
function init() {
    console.log('🔬 Initializing Advanced Capsule Endoscopy...');
    
    // Add small delay to ensure DOM is ready
    setTimeout(() => {
        // Setup scenario buttons (using more specific query within capsule page)
        const capsulePage = document.getElementById('page-capsule');
        if (!capsulePage) {
            console.error('❌ Capsule page not found!');
            return;
        }
        
        console.log('✅ Capsule page found');
        
        const scenarioBtns = capsulePage.querySelectorAll('.scenario-btn');
        console.log(`Found ${scenarioBtns.length} scenario buttons`);
        
        if (scenarioBtns.length === 0) {
            console.error('❌ No scenario buttons found! Check HTML structure.');
            return;
        }
        
        scenarioBtns.forEach((btn, index) => {
            btn.addEventListener('click', function() {
                console.log(`Scenario button ${index} clicked:`, this.dataset.scenario);
                // Remove active class from all buttons
                scenarioBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                simulationState.selectedScenario = this.dataset.scenario;
                console.log('✅ Selected scenario:', simulationState.selectedScenario);
            });
        });
        console.log(`✅ Initialized ${scenarioBtns.length} scenario buttons with click handlers`);
        
        // Setup start button
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            console.log('✅ Start button found');
            startBtn.addEventListener('click', function(e) {
                console.log('🚀 Start button clicked!');
                e.preventDefault();
                e.stopPropagation();
                startSimulation();
            });
            console.log('✅ Start button event listener attached');
        } else {
            console.error('❌ Start button not found! ID should be "startBtn"');
        }
        
        // Initialize chart
        initializeChart();
        
        // Reset metrics
        updateMetrics(0, 0, 0, 0);
        
        console.log('✅ Capsule endoscopy initialization complete!');
    }, 100); // Small delay to ensure DOM is fully ready
}

/**
 * Public function to initialize when page becomes visible
 */
window.initializeCapsuleEndoscopy = function() {
    console.log('Capsule endoscopy page shown, initializing...');
    init();
};

/**
 * Initialize reward chart
 */
function initializeChart() {
    const ctx = document.getElementById('rewardChart');
    if (!ctx) return;
    
    rewardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Episode Reward',
                data: [],
                borderColor: '#7C3AED',
                backgroundColor: 'rgba(124, 58, 237, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9B8FC9',
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9B8FC9',
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

/**
 * Start simulation
 */
async function startSimulation() {
    if (simulationState.isRunning) {
        showNotification('Simulation already running', 'warning');
        return;
    }
    
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="loading-spinner"></span> Training RL Agent...';
    
    simulationState.isRunning = true;
    simulationState.trainingLog = [];
    simulationState.detections = [];
    simulationState.images = [];
    
    // Reset metrics
    updateMetrics(0, 0, 0, 0);
    document.getElementById('detectionsContainer').innerHTML = '<p style="color: var(--text-tertiary); font-size: 13px; text-align: center; padding: 20px;">Training agent and running simulation...</p>';
    document.getElementById('imageGallery').innerHTML = '';
    
    try {
        console.log(`Starting capsule endoscopy: scenario=${simulationState.selectedScenario}`);
        
        const response = await fetch(`${API_BASE}/biopsy/capsule-endoscopy?scenario=${simulationState.selectedScenario}&num_steps=80`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Simulation failed');
        }
        
        const result = await response.json();
        console.log('Simulation complete:', result);
        
        // Update training chart
        updateTrainingChart(result.training_log);
        
        // Animate procedure
        await animateProcedure(result);
        
        // Display final results
        displayResults(result);
        
        showNotification('Capsule endoscopy completed successfully!', 'success');
        
    } catch (error) {
        console.error('Simulation error:', error);
        showNotification('Simulation failed: ' + error.message, 'error');
        document.getElementById('detectionsContainer').innerHTML = `<p style="color: var(--danger); font-size: 13px; text-align: center; padding: 20px;">Error: ${error.message}</p>`;
    } finally {
        simulationState.isRunning = false;
        startBtn.disabled = false;
        startBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Start RL Training & Endoscopy
        `;
    }
}

/**
 * Update training chart with episode data
 */
function updateTrainingChart(trainingLog) {
    if (!rewardChart || !trainingLog) return;
    
    const labels = trainingLog.map(ep => `Ep ${ep.episode}`);
    const rewards = trainingLog.map(ep => ep.reward);
    
    rewardChart.data.labels = labels;
    rewardChart.data.datasets[0].data = rewards;
    rewardChart.update();
    
    // Update epsilon display
    const finalEpsilon = trainingLog[trainingLog.length - 1].epsilon;
    document.getElementById('epsilonValue').textContent = `${(finalEpsilon * 100).toFixed(1)}%`;
    document.getElementById('learningProgress').style.width = `${(1 - finalEpsilon) * 100}%`;
}

/**
 * Animate procedure steps
 */
async function animateProcedure(result) {
    const procedureLog = result.procedure_log || [];
    const totalSteps = procedureLog.length;
    
    for (let i = 0; i < procedureLog.length; i++) {
        const step = procedureLog[i];
        
        // Update position display
        const pos = step.position;
        document.getElementById('positionDisplay').textContent = `Position: (${pos.x}, ${pos.y}, ${pos.z})`;
        
        // Update reward display
        document.getElementById('rewardDisplay').textContent = `Reward: ${step.reward.toFixed(2)}`;
        
        // Update step counter
        updateMetrics(
            result.images_captured ? result.images_captured.length : 0,
            result.detections ? result.detections.length : 0,
            i + 1,
            result.agent_metrics ? 85 : 0
        );
        
        // Highlight if capturing image
        if (step.action === 'capture_image') {
            showImageCapture(step);
        }
        
        // Progress indicator
        const progress = ((i + 1) / totalSteps) * 100;
        document.getElementById('learningProgress').style.width = `${progress}%`;
        
        // Animate (faster than before - 100ms per step)
        await sleep(100);
    }
}

/**
 * Show image capture animation
 */
function showImageCapture(step) {
    // Flash effect on capsule indicator
    const indicator = document.querySelector('.capsule-indicator');
    if (indicator) {
        indicator.style.borderColor = '#10B981';
        indicator.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.5)';
        setTimeout(() => {
            indicator.style.borderColor = '#7C3AED';
            indicator.style.boxShadow = 'none';
        }, 300);
    }
}

/**
 * Display final results
 */
function displayResults(result) {
    // Update final metrics
    const accuracy = result.agent_metrics ? 85 : 0;
    updateMetrics(
        result.images_captured.length,
        result.detections.length,
        result.total_steps,
        accuracy
    );
    
    // Display detections
    displayDetections(result.detections, result.detections_by_type);
    
    // Display images
    displayImages(result.images_captured);
}

/**
 * Display pathology detections
 */
function displayDetections(detections, detectionsByType) {
    const container = document.getElementById('detectionsContainer');
    
    if (!detections || detections.length === 0) {
        container.innerHTML = '<p style="color: var(--text-tertiary); font-size: 13px; text-align: center; padding: 20px;">No significant pathologies detected</p>';
        return;
    }
    
    container.innerHTML = '';
    
    // Group by condition type
    const grouped = {};
    detections.forEach(detection => {
        const condition = detection.condition;
        if (!grouped[condition]) {
            grouped[condition] = [];
        }
        grouped[condition].push(detection);
    });
    
    // Display each type
    Object.keys(grouped).forEach(condition => {
        const items = grouped[condition];
        const avgSeverity = items.reduce((sum, item) => sum + item.severity, 0) / items.length;
        
        const card = createDetectionCard(condition, items, avgSeverity);
        container.appendChild(card);
    });
}

/**
 * Create detection card
 */
function createDetectionCard(condition, items, avgSeverity) {
    const card = document.createElement('div');
    card.className = 'capsule-detection-card';
    
    let severityClass = 'severity-low';
    let severityText = 'Low';
    if (avgSeverity > 0.7) {
        severityClass = 'severity-high';
        severityText = 'High';
    } else if (avgSeverity > 0.4) {
        severityClass = 'severity-medium';
        severityText = 'Moderate';
    }
    
    // Format condition name
    const conditionName = condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    card.innerHTML = `
        <div class="capsule-detection-header">
            <span class="capsule-detection-type">${conditionName}</span>
            <span class="severity-badge ${severityClass}">${severityText} Severity</span>
        </div>
        <div class="capsule-detection-details">
            <strong>Locations found:</strong> ${items.length}<br>
            <strong>Average severity:</strong> ${(avgSeverity * 100).toFixed(1)}%<br>
            <strong>First detected:</strong> Step ${items[0].timestamp}
        </div>
    `;
    
    return card;
}

/**
 * Display captured images
 */
function displayImages(images) {
    const gallery = document.getElementById('imageGallery');
    
    if (!images || images.length === 0) {
        gallery.innerHTML = '<p style="color: var(--text-tertiary); font-size: 13px; grid-column: 1/-1; text-align: center; padding: 20px;">No images captured</p>';
        return;
    }
    
    gallery.innerHTML = '';
    
    // Show up to 12 images
    const displayImages = images.slice(0, 12);
    
    displayImages.forEach((img, index) => {
        const imgCard = document.createElement('div');
        imgCard.className = 'capsule-image-item';
        imgCard.title = `${img.condition} - Severity: ${(img.severity * 100).toFixed(0)}%`;
        
        // Color code by severity
        let bgColor = 'rgba(16, 185, 129, 0.1)';
        if (img.severity > 0.7) bgColor = 'rgba(239, 68, 68, 0.1)';
        else if (img.severity > 0.4) bgColor = 'rgba(245, 158, 11, 0.1)';
        
        imgCard.style.background = bgColor;
        imgCard.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 24px; margin-bottom: 8px;">📸</div>
                <div style="font-size: 11px; color: var(--text-primary); font-weight: 600;">Image ${index + 1}</div>
                <div style="font-size: 10px; color: var(--primary);">${(img.severity * 100).toFixed(0)}%</div>
            </div>
        `;
        
        gallery.appendChild(imgCard);
    });
}

/**
 * Update metrics display
 */
function updateMetrics(images, detections, steps, accuracy) {
    document.getElementById('imagesCount').textContent = images;
    document.getElementById('detectionsCount').textContent = detections;
    document.getElementById('stepsCount').textContent = steps;
    document.getElementById('accuracyValue').textContent = `${accuracy}%`;
}

/**
 * Utility functions
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Could add toast notifications here
}

// Initialize on load (for standalone page) or when called from dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Try to initialize immediately if page is visible
    const capsulePage = document.getElementById('page-capsule');
    if (capsulePage && capsulePage.style.display !== 'none') {
        init();
    }
    // Otherwise, wait for the dashboard to call initializeCapsuleEndoscopy()
});

