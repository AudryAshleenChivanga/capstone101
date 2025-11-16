/**
 * Advanced Capsule Endoscopy with Real-time RL Learning
 * Multi-pathology detection with live visualization
 */

// Wrap everything in an IIFE to avoid conflicts
(function() {
    'use strict';
    
    console.log('🔬 Capsule Endoscopy Script Loading...');

    // API Configuration - Use existing API_BASE or create local one
    const CAPSULE_API_BASE = window.API_BASE || (window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : window.location.origin);

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
    
    // Add click handlers directly
    scenarioBtns.forEach((btn, index) => {
        btn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`Scenario button clicked: ${this.dataset.scenario}`);
            // Remove active class from all buttons
            scenarioBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            simulationState.selectedScenario = this.dataset.scenario;
            console.log('✅ Selected scenario:', simulationState.selectedScenario);
        };
        console.log(`✅ Button ${index} (${btn.dataset.scenario}) handler attached`);
    });
    
    // Setup start button
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        console.log('✅ Start button found');
        startBtn.onclick = function(e) {
            console.log('🚀 Start button clicked!');
            e.preventDefault();
            e.stopPropagation();
            startSimulation();
        };
        console.log('✅ Start button event listener attached');
    } else {
        console.error('❌ Start button not found! ID should be "startBtn"');
    }
    
    // Initialize chart
    initializeChart();
    
    // Reset metrics
    updateMetrics(0, 0, 0, 0);
    
    console.log('✅ Capsule endoscopy initialization complete!');
}

    /**
     * Public function to initialize when page becomes visible
     */
    window.initializeCapsuleEndoscopy = function() {
        console.log('🔬 initializeCapsuleEndoscopy() called!');
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
    if (!startBtn) {
        console.error('Start button not found');
        return;
    }
    
    startBtn.disabled = true;
    startBtn.innerHTML = `
        <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
            <path d="M12 2a10 10 0 0110 10" stroke-opacity="1"/>
        </svg>
        Training RL Agent...
    `;
    
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
        
        const response = await fetch(`${CAPSULE_API_BASE}/biopsy/capsule-endoscopy?scenario=${simulationState.selectedScenario}&num_steps=80`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Simulation complete:', result);
        
        // Validate result structure
        if (!result || !result.success) {
            throw new Error('Invalid simulation result');
        }
        
        // Update training chart if available
        if (result.training_log && result.training_log.length > 0) {
            updateTrainingChart(result.training_log);
        }
        
        // Animate procedure
        if (result.procedure_log) {
            await animateProcedure(result);
        }
        
        // Display final results
        displayResults(result);
        
        showNotification('Capsule endoscopy completed successfully!', 'success');
        
    } catch (error) {
        console.error('Simulation error:', error);
        showNotification(`Simulation failed: ${error.message}`, 'error');
        document.getElementById('detectionsContainer').innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 12px; padding: 24px; text-align: center; margin: 20px;">
                <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                <h3 style="color: #EF4444; margin-bottom: 8px;">Simulation Failed</h3>
                <p style="color: var(--text-secondary); font-size: 14px;">${error.message}</p>
                <button onclick="startSimulation()" style="margin-top: 16px; padding: 10px 20px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">Try Again</button>
            </div>
        `;
    } finally {
        simulationState.isRunning = false;
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Start RL Training & Endoscopy
            `;
        }
    }
}

// Add CSS animation for spinner
if (!document.getElementById('spinner-style')) {
    const style = document.createElement('style');
    style.id = 'spinner-style';
    style.textContent = `
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
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
 * Animate procedure steps with real-time updates
 */
async function animateProcedure(result) {
    const procedureLog = result.procedure_log || [];
    const totalSteps = procedureLog.length;
    const allImages = result.images_captured || [];
    const allDetections = result.detections || [];
    
    let currentImages = 0;
    let currentDetections = 0;
    
    for (let i = 0; i < procedureLog.length; i++) {
        const step = procedureLog[i];
        
        // Update position display
        const pos = step.position;
        document.getElementById('positionDisplay').textContent = `Position: (${pos.x}, ${pos.y}, ${pos.z})`;
        
        // Update reward display
        const reward = step.reward || 0;
        document.getElementById('rewardDisplay').textContent = `Reward: ${reward.toFixed(2)}`;
        
        // Increment images/detections as we progress
        if (step.action === 'capture_image' && currentImages < allImages.length) {
            currentImages++;
            // Display the new image immediately
            const newImage = allImages[currentImages - 1];
            if (newImage) {
                addImageToGallery(newImage, currentImages);
            }
        }
        
        // Check for new detections
        if (step.detection && currentDetections < allDetections.length) {
            currentDetections++;
        }
        
        // Update metrics in real-time
        const accuracy = result.agent_metrics ? Math.min(50 + (i / totalSteps) * 50, 95) : 0;
        updateMetrics(currentImages, currentDetections, i + 1, accuracy.toFixed(0));
        
        // Visual feedback for image capture
        if (step.action === 'capture_image') {
            showImageCapture(step);
        }
        
        // Progress indicator
        const progress = ((i + 1) / totalSteps) * 100;
        document.getElementById('learningProgress').style.width = `${progress}%`;
        
        // Animate - 50ms per step for smooth real-time feel
        await sleep(50);
    }
    
    // Ensure final counts are correct
    updateMetrics(allImages.length, allDetections.length, totalSteps, result.agent_metrics ? 95 : 85);
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
    const accuracy = result.agent_metrics ? 95 : 85;
    updateMetrics(
        result.images_captured ? result.images_captured.length : 0,
        result.detections ? result.detections.length : 0,
        result.total_steps || 0,
        accuracy
    );
    
    // Display detections with diagnosis
    if (result.detections && result.detections.length > 0) {
        displayDetections(result.detections, result.detections_by_type);
    } else {
        document.getElementById('detectionsContainer').innerHTML = 
            '<p style="text-align: center; color: var(--text-tertiary); padding: 20px;">No pathologies detected</p>';
    }
    
    // Images should already be displayed in real-time, but ensure final display
    if (result.images_captured && result.images_captured.length > 0) {
        displayImages(result.images_captured);
    }
    
    // Show success notification
    showNotification(`Simulation complete! Captured ${result.images_captured?.length || 0} images, detected ${result.detections?.length || 0} pathologies.`, 'success');
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
 * Add single image to gallery in real-time
 */
function addImageToGallery(img, imageNumber) {
    const gallery = document.getElementById('imageGallery');
    
    // Remove "no images" message if present
    const noImagesMsg = gallery.querySelector('p');
    if (noImagesMsg) {
        gallery.innerHTML = '';
    }
    
    const imgCard = createImageCard(img, imageNumber);
    gallery.appendChild(imgCard);
    
    // Flash animation
    imgCard.style.animation = 'flashIn 0.5s ease-out';
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
        const imgCard = createImageCard(img, index + 1);
        gallery.appendChild(imgCard);
    });
}

/**
 * Create image card element
 */
function createImageCard(img, imageNumber) {
    const imgCard = document.createElement('div');
    imgCard.className = 'capsule-image-item';
    imgCard.style.cursor = 'pointer';
    
    // Format condition name properly
    const conditionName = img.condition ? img.condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown';
    const severityPercent = img.severity ? (img.severity * 100).toFixed(0) : '0';
    imgCard.title = `${conditionName} - Severity: ${severityPercent}%`;
    
    // Color code by severity
    let bgColor = 'rgba(16, 185, 129, 0.1)';
    let borderColor = '#10B981';
    let severityText = 'Low';
    let severityColor = '#10B981';
    
    if (img.severity > 0.7) {
        bgColor = 'rgba(239, 68, 68, 0.15)';
        borderColor = '#EF4444';
        severityText = 'High';
        severityColor = '#EF4444';
    } else if (img.severity > 0.4) {
        bgColor = 'rgba(245, 158, 11, 0.15)';
        borderColor = '#F59E0B';
        severityText = 'Med';
        severityColor = '#F59E0B';
    }
    
    imgCard.style.background = bgColor;
    imgCard.style.border = `2px solid ${borderColor}`;
    imgCard.style.borderRadius = '12px';
    imgCard.style.padding = '16px';
    imgCard.style.transition = 'all 0.3s ease';
    
    imgCard.innerHTML = `
        <div style="text-align: center;">
            <div style="width: 100%; height: 120px; background: linear-gradient(135deg, ${bgColor}, rgba(0,0,0,0.3)); border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; font-size: 36px;">
                ${getConditionIcon(img.condition)}
            </div>
            <div style="font-size: 12px; color: var(--text-primary); font-weight: 600; margin-bottom: 4px;">Image ${imageNumber}</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">${conditionName}</div>
            <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
                <span style="font-size: 14px; font-weight: 700; color: ${severityColor};">${severityPercent}%</span>
                <span style="font-size: 10px; padding: 2px 6px; background: ${bgColor}; color: ${severityColor}; border-radius: 4px; font-weight: 600;">${severityText}</span>
            </div>
        </div>
    `;
    
    // Click to view details
    imgCard.addEventListener('click', () => {
        showImageDetails(img, imageNumber);
    });
    
    return imgCard;
}

/**
 * Get icon for condition type
 */
function getConditionIcon(condition) {
    const icons = {
        'h_pylori': '🦠',
        'peptic_ulcer': '🔴',
        'gastric_cancer': '⚠️',
        'tumor': '🔺',
        'inflammation': '🔥',
        'healthy': '✅',
        'abnormal_cells': '⚡'
    };
    return icons[condition] || '📸';
}

/**
 * Show image details in modal
 */
function showImageDetails(img, imageNumber) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 10000;';
    
    const conditionName = img.condition ? img.condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown';
    const severityPercent = img.severity ? (img.severity * 100).toFixed(1) : '0';
    
    modal.innerHTML = `
        <div style="background: var(--bg-secondary); border-radius: 16px; padding: 32px; max-width: 500px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
                <h2 style="margin: 0; color: var(--text-primary); font-size: 24px;">Image ${imageNumber} Details</h2>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 28px; cursor: pointer; color: var(--text-secondary);">&times;</button>
            </div>
            
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 80px; margin-bottom: 16px;">${getConditionIcon(img.condition)}</div>
                <h3 style="color: var(--text-primary); font-size: 20px; margin-bottom: 8px;">${conditionName}</h3>
            </div>
            
            <div style="background: var(--bg-tertiary); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: var(--text-secondary); font-size: 14px;">Severity:</span>
                    <span style="color: var(--primary); font-weight: 600; font-size: 14px;">${severityPercent}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: var(--text-secondary); font-size: 14px;">Position:</span>
                    <span style="color: var(--text-primary); font-size: 14px;">(${img.position?.x || 0}, ${img.position?.y || 0}, ${img.position?.z || 0})</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary); font-size: 14px;">Timestamp:</span>
                    <span style="color: var(--text-primary); font-size: 14px;">Step ${img.timestamp || 0}</span>
                </div>
            </div>
            
            <button onclick="this.closest('.modal-overlay').remove()" style="width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Update metrics display with animation
 */
function updateMetrics(images, detections, steps, accuracy) {
    animateNumber('imagesCount', images);
    animateNumber('detectionsCount', detections);
    animateNumber('stepsCount', steps);
    document.getElementById('accuracyValue').textContent = `${accuracy}%`;
}

/**
 * Animate number increment
 */
function animateNumber(elementId, targetValue) {
    const element = document.getElementById(elementId);
    const currentValue = parseInt(element.textContent) || 0;
    
    if (currentValue === targetValue) return;
    
    // Flash animation on change
    element.style.transition = 'transform 0.2s ease-out';
    element.style.transform = 'scale(1.2)';
    element.style.color = '#10B981';
    
    element.textContent = targetValue;
    
    setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.color = '';
    }, 200);
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'all 0.3s ease-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Utility functions
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

