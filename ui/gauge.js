/**
 * Simple canvas gauge for probability visualization
 */

function drawGauge(canvasId, value) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height - 20;
    const radius = 80;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background arc
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.lineWidth = 20;
    ctx.strokeStyle = '#e2e8f0';
    ctx.stroke();
    
    // Determine color based on value
    let color;
    if (value < 0.4) {
        color = '#10b981'; // Green (low risk)
    } else if (value < 0.6) {
        color = '#f59e0b'; // Amber (moderate risk)
    } else {
        color = '#ef4444'; // Red (high risk)
    }
    
    // Draw value arc
    const angle = Math.PI + (value * Math.PI);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, angle);
    ctx.lineWidth = 20;
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    // Draw percentage text
    ctx.font = 'bold 28px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
    ctx.fillStyle = '#1e293b';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const percentage = (value * 100).toFixed(1) + '%';
    ctx.fillText(percentage, centerX, centerY - 10);
    
    // Draw label
    ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
    ctx.fillStyle = '#64748b';
    let label;
    if (value < 0.4) {
        label = 'LOW RISK';
    } else if (value < 0.6) {
        label = 'MODERATE';
    } else {
        label = 'HIGH RISK';
    }
    ctx.fillText(label, centerX, centerY + 15);
}
