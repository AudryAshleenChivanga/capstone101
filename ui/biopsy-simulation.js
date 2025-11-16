// =========================================
// 3D BIOPSY SIMULATION WITH AI ANALYSIS
// Reinforcement Learning for Tissue Analysis
// =========================================

let scene, camera, renderer, tissue, particles;
let animationId, rotationSpeed = 0.01;
let isAnimating = true;
let analysisInProgress = false;

// RL Agent State
let rlAgent = {
    state: 'idle',
    observations: [],
    confidence: 0,
    findings: [],
    learningRate: 0.001,
    epsilon: 0.1, // Exploration rate
    qTable: {}
};

// Initialize the simulation
function init() {
    console.log('Initializing 3D Biopsy Simulation...');
    
    // Check if THREE.js is loaded
    if (typeof THREE === 'undefined') {
        console.error('THREE.js library not loaded!');
        document.getElementById('statusText').textContent = 'Error: THREE.js not loaded';
        return;
    }
    
    try {
        // Create scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a);
        scene.fog = new THREE.Fog(0x0f172a, 50, 200);
        
        // Setup camera
        camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.z = 30;
        
        // Setup renderer
        const canvas = document.getElementById('canvas-3d');
        if (!canvas) {
            console.error('Canvas element not found!');
            return;
        }
        
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        // Create tissue sample (complex geometry)
        createTissueSample();
        
        // Add particles (simulating cells)
        createCellParticles();
        
        console.log('3D scene initialized successfully');
    } catch (error) {
        console.error('Error initializing 3D scene:', error);
        document.getElementById('statusText').textContent = 'Error: ' + error.message;
    }
    
    // Add lights
    setupLights();
    
    // Setup controls
    setupControls();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
    
    // Start animation
    animate();
    
    // Hide loading overlay
    setTimeout(() => {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }, 1500);
}

function createTissueSample() {
    // Create organic-looking tissue geometry
    const geometry = new THREE.SphereGeometry(10, 64, 64);
    
    // Deform vertices to create irregular tissue shape
    const positions = geometry.attributes.position;
    for (let i = 0; i < positions.count; i++) {
        const x = positions.getX(i);
        const y = positions.getY(i);
        const z = positions.getZ(i);
        
        const noise = Math.sin(x * 0.3) * Math.cos(y * 0.3) * Math.sin(z * 0.3);
        const scale = 1 + noise * 0.3;
        
        positions.setXYZ(i, x * scale, y * scale, z * scale);
    }
    geometry.computeVertexNormals();
    
    // Create material with subsurface scattering effect
    const material = new THREE.MeshPhysicalMaterial({
        color: 0xffccaa,
        metalness: 0.1,
        roughness: 0.8,
        transmission: 0.3,
        thickness: 2,
        opacity: 0.9,
        transparent: true,
        side: THREE.DoubleSide
    });
    
    tissue = new THREE.Mesh(geometry, material);
    scene.add(tissue);
    
    // Add wireframe overlay
    const wireframe = new THREE.WireframeGeometry(geometry);
    const line = new THREE.LineSegments(wireframe);
    line.material.color.setHex(0x0ea5e9);
    line.material.opacity = 0.1;
    line.material.transparent = true;
    tissue.add(line);
}

function createCellParticles() {
    const particleCount = 500;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
        // Random positions within tissue
        const radius = Math.random() * 8 + 2;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        
        positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = radius * Math.cos(phi);
        
        // Color variation (healthy vs abnormal cells)
        const isAbnormal = Math.random() < 0.15;
        colors[i * 3] = isAbnormal ? 1.0 : 0.2;
        colors[i * 3 + 1] = isAbnormal ? 0.2 : 0.8;
        colors[i * 3 + 2] = 0.3;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.PointsMaterial({
        size: 0.3,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });
    
    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

function setupLights() {
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambient);
    
    // Directional lights
    const light1 = new THREE.DirectionalLight(0x0ea5e9, 1);
    light1.position.set(10, 10, 10);
    scene.add(light1);
    
    const light2 = new THREE.DirectionalLight(0x10b981, 0.8);
    light2.position.set(-10, -10, -10);
    scene.add(light2);
    
    // Point light (simulating microscope illumination)
    const pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(0, 0, 20);
    scene.add(pointLight);
}

function setupControls() {
    // Zoom control
    document.getElementById('zoomSlider').addEventListener('input', (e) => {
        const zoom = parseFloat(e.target.value);
        camera.position.z = 30 / zoom;
        document.getElementById('zoomValue').textContent = zoom.toFixed(1) + 'x';
    });
    
    // Rotation speed
    document.getElementById('rotationSlider').addEventListener('input', (e) => {
        rotationSpeed = parseFloat(e.target.value) * 0.01;
        const labels = ['Slow', 'Medium', 'Fast'];
        const index = Math.floor(parseFloat(e.target.value));
        document.getElementById('rotationValue').textContent = labels[Math.min(index, 2)];
    });
    
    // View mode
    document.getElementById('viewMode').addEventListener('change', (e) => {
        changeViewMode(e.target.value);
    });
}

function changeViewMode(mode) {
    switch (mode) {
        case 'xray':
            tissue.material.color.setHex(0xaaaaaa);
            tissue.material.transmission = 0.8;
            tissue.material.opacity = 0.3;
            particles.material.opacity = 0.9;
            break;
        case 'thermal':
            tissue.material.color.setHex(0xff4444);
            tissue.material.emissive = new THREE.Color(0x330000);
            tissue.material.emissiveIntensity = 0.5;
            break;
        case 'molecular':
            tissue.material.color.setHex(0x4488ff);
            tissue.material.wireframe = true;
            particles.material.size = 0.5;
            break;
        default:
            tissue.material.color.setHex(0xffccaa);
            tissue.material.transmission = 0.3;
            tissue.material.opacity = 0.9;
            tissue.material.wireframe = false;
            tissue.material.emissive = new THREE.Color(0x000000);
            particles.material.size = 0.3;
            particles.material.opacity = 0.6;
    }
}

function animate() {
    animationId = requestAnimationFrame(animate);
    
    if (isAnimating) {
        // Rotate tissue
        tissue.rotation.y += rotationSpeed;
        tissue.rotation.x += rotationSpeed * 0.3;
        
        // Animate particles
        const time = Date.now() * 0.001;
        const positions = particles.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
            positions[i + 1] += Math.sin(time + positions[i]) * 0.01;
        }
        particles.geometry.attributes.position.needsUpdate = true;
        particles.rotation.y += rotationSpeed * 0.5;
    }
    
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function toggleAnimation() {
    isAnimating = !isAnimating;
    const btn = document.getElementById('animToggleText');
    btn.textContent = isAnimating ? '⏸️ Pause Animation' : '▶️ Resume Animation';
}

function resetSimulation() {
    // Reset RL agent
    rlAgent = {
        state: 'idle',
        observations: [],
        confidence: 0,
        findings: [],
        learningRate: 0.001,
        epsilon: 0.1,
        qTable: {}
    };
    
    // Reset UI
    document.getElementById('analysisResults').innerHTML = `
        <div class="analysis-item">
            <h4>🤖 Simulation Reset</h4>
            <p>Ready for new analysis. Click "Run AI Analysis" to begin.</p>
        </div>
    `;
    
    document.getElementById('samplePoints').textContent = '0';
    document.getElementById('analysisTime').textContent = '0.0s';
    document.getElementById('confidence').textContent = '--';
    document.getElementById('findings').textContent = '0';
    
    // Reset view
    document.getElementById('viewMode').value = 'standard';
    changeViewMode('standard');
}

// =========================================
// AI ANALYSIS WITH REINFORCEMENT LEARNING
// =========================================

async function runAIAnalysis() {
    if (analysisInProgress) return;
    
    analysisInProgress = true;
    document.getElementById('statusText').textContent = 'Analyzing...';
    
    const sampleType = document.getElementById('sampleType').value;
    const startTime = Date.now();
    
    // Show initial analysis state
    showAnalysisProgress('Initializing RL Agent...');
    
    // Simulate RL analysis phases
    await simulateRLAnalysis(sampleType, startTime);
    
    analysisInProgress = false;
    document.getElementById('statusText').textContent = 'Analysis Complete';
}

async function simulateRLAnalysis(sampleType, startTime) {
    // Phase 1: Environment Setup
    await delay(500);
    showAnalysisProgress('Setting up environment...');
    rlAgent.state = 'exploring';
    
    // Phase 2: Data Collection
    await delay(800);
    showAnalysisProgress('Collecting sample data...');
    const samplePoints = Math.floor(Math.random() * 400) + 300;
    document.getElementById('samplePoints').textContent = samplePoints;
    
    // Phase 3: Feature Extraction
    await delay(1000);
    showAnalysisProgress('Extracting features...');
    const features = extractFeatures(sampleType);
    
    // Phase 4: RL Policy Execution
    await delay(1200);
    showAnalysisProgress('Running reinforcement learning...');
    const policy = await executeRLPolicy(features);
    
    // Phase 5: Analysis
    await delay(1000);
    const results = analyzeWithRL(policy, features, sampleType);
    
    // Update UI with results
    const analysisTime = ((Date.now() - startTime) / 1000).toFixed(1);
    document.getElementById('analysisTime').textContent = analysisTime + 's';
    document.getElementById('confidence').textContent = results.confidence + '%';
    document.getElementById('findings').textContent = results.findings.length;
    
    // Display findings
    displayAnalysisResults(results);
}

function extractFeatures(sampleType) {
    // Simulate feature extraction
    return {
        cellDensity: Math.random() * 100,
        inflammation: Math.random(),
        abnormalCells: Math.random() * 30,
        vascularization: Math.random(),
        tissueIntegrity: Math.random(),
        bacterialPresence: Math.random(),
        ulceration: Math.random(),
        dysplasia: Math.random(),
        sampleType: sampleType
    };
}

async function executeRLPolicy(features) {
    // Simulate RL policy decision making
    // Using Q-learning-inspired approach
    
    const states = ['healthy', 'inflamed', 'ulcerated', 'dysplastic', 'infected'];
    const actions = ['continue', 'investigate', 'flag_concern', 'urgent'];
    
    // Simulate Q-value calculations
    const qValues = {};
    
    for (const state of states) {
        qValues[state] = {};
        for (const action of actions) {
            // Simulate Q-value based on features
            qValues[state][action] = Math.random() * features.cellDensity * 
                                     (1 + features.abnormalCells / 100);
        }
    }
    
    // Select best actions (exploitation vs exploration)
    const policy = {};
    for (const state of states) {
        if (Math.random() < rlAgent.epsilon) {
            // Exploration: random action
            policy[state] = actions[Math.floor(Math.random() * actions.length)];
        } else {
            // Exploitation: best action
            policy[state] = Object.keys(qValues[state]).reduce((a, b) => 
                qValues[state][a] > qValues[state][b] ? a : b
            );
        }
    }
    
    return policy;
}

function analyzeWithRL(policy, features, sampleType) {
    const findings = [];
    let maxConfidence = 0;
    
    // H. pylori Detection
    if (features.bacterialPresence > 0.6) {
        findings.push({
            type: 'danger',
            title: '🦠 H. pylori Detected',
            description: `Bacterial colonization observed (${(features.bacterialPresence * 100).toFixed(0)}% confidence). Recommend eradication therapy.`,
            confidence: features.bacterialPresence * 100
        });
        maxConfidence = Math.max(maxConfidence, features.bacterialPresence * 100);
    }
    
    // Peptic Ulcer Detection
    if (features.ulceration > 0.5 || features.tissueIntegrity < 0.4) {
        findings.push({
            type: 'warning',
            title: '🔴 Peptic Ulcer Detected',
            description: `Evidence of ulceration in ${sampleType} tissue. Tissue integrity: ${(features.tissueIntegrity * 100).toFixed(0)}%. Monitor for healing progress.`,
            confidence: Math.max(features.ulceration, 1 - features.tissueIntegrity) * 100
        });
        maxConfidence = Math.max(maxConfidence, features.ulceration * 100);
    }
    
    // Inflammation Assessment
    if (features.inflammation > 0.4) {
        findings.push({
            type: 'warning',
            title: '⚠️ Inflammation Detected',
            description: `${features.inflammation > 0.7 ? 'Severe' : 'Moderate'} inflammatory response observed. Consider anti-inflammatory treatment.`,
            confidence: features.inflammation * 100
        });
        maxConfidence = Math.max(maxConfidence, features.inflammation * 100);
    }
    
    // Dysplasia/Cancer Detection
    if (features.dysplasia > 0.6 || features.abnormalCells > 20) {
        findings.push({
            type: 'danger',
            title: '⚠️ Abnormal Cells Detected',
            description: `${features.abnormalCells.toFixed(0)} abnormal cells identified. Dysplasia score: ${(features.dysplasia * 100).toFixed(0)}%. Possible pre-cancerous or cancerous changes. URGENT: Recommend immediate specialist consultation.`,
            confidence: Math.max(features.dysplasia, features.abnormalCells / 30) * 100
        });
        maxConfidence = Math.max(maxConfidence, features.dysplasia * 100);
    }
    
    // Vascular Changes
    if (features.vascularization > 0.7) {
        findings.push({
            type: 'warning',
            title: '🩸 Increased Vascularization',
            description: 'Abnormal blood vessel formation detected. May indicate active healing or neoplastic changes.',
            confidence: features.vascularization * 100
        });
    }
    
    // Normal findings
    if (findings.length === 0) {
        findings.push({
            type: 'success',
            title: '✅ No Significant Abnormalities',
            description: `${sampleType} tissue appears within normal limits. Recommend routine follow-up.`,
            confidence: 95
        });
        maxConfidence = 95;
    }
    
    return {
        findings: findings,
        confidence: Math.round(maxConfidence),
        policy: policy,
        features: features
    };
}

function displayAnalysisResults(results) {
    const container = document.getElementById('analysisResults');
    
    let html = '';
    results.findings.forEach(finding => {
        html += `
            <div class="analysis-item ${finding.type}">
                <h4>${finding.title}</h4>
                <p>${finding.description}</p>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${finding.confidence}%"></div>
                </div>
                <p style="margin-top: 4px; font-size: 11px;">Confidence: ${finding.confidence.toFixed(0)}%</p>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Highlight affected areas on the 3D model
    highlightFindings(results.findings);
}

function highlightFindings(findings) {
    // Visual feedback on 3D model
    findings.forEach((finding, index) => {
        if (finding.type === 'danger') {
            // Pulse red color for critical findings
            const interval = setInterval(() => {
                const intensity = Math.sin(Date.now() * 0.005) * 0.5 + 0.5;
                tissue.material.emissive = new THREE.Color(0xff0000);
                tissue.material.emissiveIntensity = intensity * 0.3;
            }, 50);
            
            setTimeout(() => clearInterval(interval), 3000);
        }
    });
}

function showAnalysisProgress(message) {
    const container = document.getElementById('analysisResults');
    container.innerHTML = `
        <div class="analysis-item">
            <h4>🔄 Processing...</h4>
            <p>${message}</p>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: 100%; animation: pulse 1s infinite;"></div>
            </div>
        </div>
    `;
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize on load
window.addEventListener('load', () => {
    console.log('🔬 3D Biopsy Simulation with RL Analysis Loading...');
    
    // Small delay to ensure DOM is fully ready
    setTimeout(() => {
        try {
            init();
        } catch (error) {
            console.error('Failed to initialize simulation:', error);
            alert('Failed to initialize 3D simulation. Please refresh the page or check console for details.');
        }
    }, 100);
});

console.log('🔬 Biopsy Simulation Script Loaded');

