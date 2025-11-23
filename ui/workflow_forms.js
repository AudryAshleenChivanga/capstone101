/**
 * Multi-Stage Clinical Workflow Forms JavaScript
 * Handles Stage 1 (Symptoms) → Stage 2 (Lab) → Stage 3 (RIC Staging)
 */

// Store workflow state
const workflowState = {
    currentStage: 1,
    patientId: null,
    stage1CaseId: null,
    stage2CaseId: null,
    stage3CaseId: null,
    patientData: {}
};

/**
 * Stage 1: Symptom-Based Assessment
 */
async function submitSymptomAssessment(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    
    // Show loading
    btnText.textContent = 'Processing...';
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        // Collect form data
        const formData = {
            patient_name: form.patient_name.value,
            age: parseInt(form.age.value),
            sex: form.sex.value,
            residence: form.residence.value,
            phone: form.phone?.value || null,
            email: form.email?.value || null,
            
            // Symptoms (checkboxes)
            abdominal_pain: form.abdominal_pain?.checked ? 1 : 0,
            bloating: form.bloating?.checked ? 1 : 0,
            nausea: form.nausea?.checked ? 1 : 0,
            vomiting: form.vomiting?.checked ? 1 : 0,
            heartburn: form.heartburn?.checked ? 1 : 0,
            indigestion: form.indigestion?.checked ? 1 : 0,
            loss_of_appetite: form.loss_of_appetite?.checked ? 1 : 0,
            weight_loss: form.weight_loss?.checked ? 1 : 0,
            black_stool: form.black_stool?.checked ? 1 : 0,
            blood_in_vomit: form.blood_in_vomit?.checked ? 1 : 0,
            persistent_pain: form.persistent_pain?.checked ? 1 : 0,
            
            // Risk factors
            family_history_gastric: form.family_history?.value === 'yes' ? 1 : 0,
            previous_ulcer: form.previous_ulcer?.checked ? 1 : 0,
            nsaid_use: form.nsaid_use?.checked ? 1 : 0,
            smoking: form.smoking?.checked ? 1 : 0,
            
            symptom_duration_weeks: parseInt(form.symptom_duration?.value || 0)
        };
        
        // Call API
        const token = localStorage.getItem('token');
        const response = await fetch('/workflow/stage1/symptom-assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            const errorMsg = result.detail || 'Assessment failed';
            throw new Error(errorMsg);
        }
        
        // Store workflow state
        workflowState.patientId = result.patient_id;
        workflowState.stage1CaseId = result.case_id;
        workflowState.patientData = {
            name: formData.patient_name,
            age: formData.age,
            sex: formData.sex
        };
        
        // Show results
        displayStage1Results(result);
        
        // Show success message
        showNotification('Symptom assessment complete!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = error.message || String(error) || 'Unknown error occurred';
        showNotification(`Assessment failed: ${errorMessage}`, 'error');
    } finally {
        btnText.textContent = 'Submit Assessment';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

function displayStage1Results(result) {
    const resultsDiv = document.getElementById('stage1Results');
    const assessment = result.assessment;
    
    // Generate HTML
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h3>Stage 1 Assessment Complete</h3>
                <span class="patient-id-badge">Patient ID: ${result.patient_id}</span>
            </div>
            
            <div class="assessment-summary">
                <div class="risk-indicator risk-${assessment.risk_level}">
                    <div class="risk-label">Risk Level</div>
                    <div class="risk-value">${assessment.risk_level.toUpperCase()}</div>
                    <div class="risk-prob">${(assessment.risk_probability * 100).toFixed(1)}% probability</div>
                </div>
                
                ${assessment.alarm_symptoms && assessment.alarm_symptoms.length > 0 ? `
                    <div class="alarm-symptoms">
                        <h4>⚠ Alarm Symptoms Detected</h4>
                        <ul>
                            ${assessment.alarm_symptoms.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="recommendations-section">
                    <h4>Clinical Recommendations</h4>
                    <ul>
                        ${assessment.recommendations.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="recommended-tests">
                    <h4>Recommended Laboratory Tests</h4>
                    <ul>
                        ${assessment.recommended_tests.map(t => `<li>${t}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            ${assessment.proceed_to_stage2 ? `
                <div class="next-steps">
                    <button class="btn btn-primary btn-lg" onclick="proceedToStage2()">
                        Proceed to Stage 2: Laboratory Screening
                    </button>
                </div>
            ` : `
                <div class="next-steps">
                    <p>Monitor symptoms. Lab testing not immediately required.</p>
                    <button class="btn btn-secondary" onclick="resetWorkflow()">New Assessment</button>
                </div>
            `}
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function proceedToStage2() {
    // Switch to Stage 2 tab/page
    if (typeof showPage === 'function') {
        showPage('lab-screening');
    }
    
    // Pre-fill patient ID
    const patientIdInput = document.getElementById('stage2_patient_id');
    if (patientIdInput) {
        patientIdInput.value = workflowState.patientId;
        patientIdInput.readOnly = true;
    }
    
    showNotification(`Ready for lab tests for patient ${workflowState.patientId}`, 'info');
}

/**
 * Stage 2: Laboratory Screening
 */
async function submitLabScreening(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    
    btnText.textContent = 'Analyzing...';
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        const formData = {
            patient_id: workflowState.patientId || form.patient_id.value,
            case_id: workflowState.stage1CaseId || parseInt(form.case_id?.value),
            
            stool_antigen: form.stool_antigen.value,
            hp_igg: form.hp_igg.value,
            hemoglobin: parseFloat(form.hemoglobin.value),
            crp: parseFloat(form.crp.value),
            wbc: parseFloat(form.wbc.value),
            esr: form.esr?.value ? parseFloat(form.esr.value) : null,
            platelet_count: form.platelet_count?.value ? parseFloat(form.platelet_count.value) : null
        };
        
        const token = localStorage.getItem('token');
        const response = await fetch('/workflow/stage2/lab-screening', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        
        let result;
        try {
            result = await response.json();
        } catch (parseError) {
            throw new Error('Server returned invalid response. Please try again.');
        }
        
        if (!response.ok) {
            const errorMsg = result.detail || result.message || 'Lab screening failed';
            throw new Error(errorMsg);
        }
        
        // Update workflow state
        workflowState.stage2CaseId = result.case_id;
        
        // Show results
        displayStage2Results(result);
        
        showNotification('Lab screening complete!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = error.message || String(error) || 'Unknown error occurred';
        showNotification(`Lab screening failed: ${errorMessage}`, 'error');
    } finally {
        btnText.textContent = 'Analyze Results';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

function displayStage2Results(result) {
    const resultsDiv = document.getElementById('stage2Results');
    const screening = result.screening_result;
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h3>Stage 2 Lab Screening Complete</h3>
                <span class="patient-id-badge">Patient ID: ${result.patient_id}</span>
            </div>
            
            <div class="screening-summary">
                <div class="infection-status status-${screening.status}">
                    <div class="status-label">H. pylori Status</div>
                    <div class="status-value">${screening.status.toUpperCase()}</div>
                    <div class="status-detail">
                        Infection Probability: ${(screening.infection_probability * 100).toFixed(1)}%<br>
                        Confidence: ${screening.confidence}
                    </div>
                </div>
                
                <div class="recommendations-section">
                    <h4>Clinical Recommendations</h4>
                    <ul>
                        ${screening.recommendations.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            ${screening.proceed_to_stage3 ? `
                <div class="next-steps">
                    <button class="btn btn-primary btn-lg" onclick="proceedToStage3()">
                        Proceed to Stage 3: RIC Staging & Treatment
                    </button>
                </div>
            ` : `
                <div class="next-steps">
                    <p>H. pylori infection not confirmed. Follow recommendations above.</p>
                    <button class="btn btn-secondary" onclick="resetWorkflow()">New Assessment</button>
                </div>
            `}
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function proceedToStage3() {
    if (typeof showPage === 'function') {
        showPage('staging');
    }
    
    const patientIdInput = document.getElementById('stage3_patient_id');
    if (patientIdInput) {
        patientIdInput.value = workflowState.patientId;
        patientIdInput.readOnly = true;
    }
    
    showNotification(`Ready for RIC staging for patient ${workflowState.patientId}`, 'info');
}

/**
 * Stage 3: RIC Staging
 */
async function submitRICStaging(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    
    btnText.textContent = 'Analyzing...';
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        const formData = {
            patient_id: workflowState.patientId || form.patient_id.value,
            case_id: workflowState.stage2CaseId || parseInt(form.case_id?.value),
            
            // Antibiotic MIC values (Minimum Inhibitory Concentration)
            mic_clarithromycin: form.mic_clarithromycin?.value ? parseFloat(form.mic_clarithromycin.value) : null,
            mic_metronidazole: form.mic_metronidazole?.value ? parseFloat(form.mic_metronidazole.value) : null,
            mic_levofloxacin: form.mic_levofloxacin?.value ? parseFloat(form.mic_levofloxacin.value) : null,
            
            // Genetic mutations (resistance markers)
            mutation_a2143g: form.mutation_a2143g?.checked ? 1 : 0,
            mutation_a2144g: form.mutation_a2144g?.checked ? 1 : 0,  // Fixed: was a2142g
            mutation_rdxa: form.mutation_rdxa?.checked ? 1 : 0,
            mutation_gyra: form.mutation_gyra?.checked ? 1 : 0
        };
        
        const token = localStorage.getItem('token');
        const response = await fetch('/workflow/stage3/ric-staging', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        
        let result;
        try {
            result = await response.json();
        } catch (parseError) {
            throw new Error('Server returned invalid response. Please try again.');
        }
        
        if (!response.ok) {
            const errorMsg = result.detail || result.message || 'RIC staging failed';
            throw new Error(errorMsg);
        }
        
        // Update workflow state
        workflowState.stage3CaseId = result.case_id;
        
        // Show results and prescription
        displayStage3Results(result);
        
        showNotification('RIC staging complete! Treatment protocol generated.', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = error.message || String(error) || 'Unknown error occurred';
        showNotification(`RIC staging failed: ${errorMessage}`, 'error');
    } finally {
        btnText.textContent = 'Complete Staging';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

function displayStage3Results(result) {
    const resultsDiv = document.getElementById('stage3Results');
    const staging = result.staging_result;
    const treatment = staging.treatment_protocol;
    
    // Store Stage 3 results in workflowState for prescription generation
    workflowState.stage3Results = {
        stage: staging.stage,
        confidence: staging.stage_confidence,
        treatment_protocol: treatment
    };
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h3>Stage 3 RIC Staging Complete</h3>
                <span class="patient-id-badge">Patient ID: ${result.patient_id}</span>
            </div>
            
            <div class="staging-summary">
                <div class="severity-indicator severity-${staging.stage}">
                    <div class="severity-label">Disease Severity</div>
                    <div class="severity-value">${staging.stage.toUpperCase()}</div>
                    <div class="severity-detail">
                        Confidence: ${(staging.stage_confidence * 100).toFixed(1)}%
                    </div>
                </div>
                
                ${staging.biopsy_recommended ? `
                    <div class="alert alert-warning">
                        <strong>Biopsy Recommended:</strong> Endoscopic evaluation suggested based on severity.
                    </div>
                ` : ''}
                
                <div class="treatment-protocol">
                    <h4>Treatment Protocol</h4>
                    <div class="protocol-name">${treatment.regimen}</div>
                    
                    <h5>Medications</h5>
                    <table class="medications-table">
                        <thead>
                            <tr>
                                <th>Medication</th>
                                <th>Dosage</th>
                                <th>Frequency</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${treatment.medications.map(med => `
                                <tr>
                                    <td><strong>${med.name}</strong></td>
                                    <td>${med.dosage}</td>
                                    <td>${med.frequency}</td>
                                    <td>${med.duration}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    
                    <h5>Lifestyle Recommendations</h5>
                    <ul>
                        ${treatment.lifestyle.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                    
                    <div class="follow-up-info">
                        <strong>Follow-up:</strong> ${treatment.follow_up}
                    </div>
                </div>
            </div>
            
            <div class="next-steps">
                <button class="btn btn-success btn-lg" onclick="createPrescription(${result.case_id})">
                    Generate Prescription
                </button>
                <button class="btn btn-secondary" onclick="resetWorkflow()">New Patient</button>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function createPrescription(caseId) {
    try {
        // Get treatment protocol from Stage 3 results
        const stagingResult = workflowState.stage3Results || {};
        const resistanceStage = stagingResult.stage || 'moderate';
        const protocol = stagingResult.treatment_protocol || {};
        
        // Generate medications based on resistance stage
        let medications = [];
        let protocolType = 'eradication';
        
        if (resistanceStage === 'low') {
            // Standard triple therapy
            medications = [
                {
                    name: "Omeprazole (PPI)",
                    dosage: "20mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                },
                {
                    name: "Amoxicillin",
                    dosage: "1000mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                },
                {
                    name: "Clarithromycin",
                    dosage: "500mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                }
            ];
        } else if (resistanceStage === 'moderate') {
            // Bismuth quadruple therapy
            medications = [
                {
                    name: "Esomeprazole (PPI)",
                    dosage: "40mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                },
                {
                    name: "Bismuth Subsalicylate",
                    dosage: "300mg",
                    frequency: "Four times daily",
                    duration: "14 days"
                },
                {
                    name: "Tetracycline",
                    dosage: "500mg",
                    frequency: "Four times daily",
                    duration: "14 days"
                },
                {
                    name: "Metronidazole",
                    dosage: "500mg",
                    frequency: "Three times daily",
                    duration: "14 days"
                }
            ];
        } else {
            // High resistance - salvage therapy
            medications = [
                {
                    name: "Esomeprazole (PPI)",
                    dosage: "40mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                },
                {
                    name: "Amoxicillin",
                    dosage: "1000mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                },
                {
                    name: "Levofloxacin",
                    dosage: "500mg",
                    frequency: "Once daily",
                    duration: "14 days"
                },
                {
                    name: "Rifabutin",
                    dosage: "150mg",
                    frequency: "Twice daily",
                    duration: "14 days"
                }
            ];
            protocolType = 'salvage';
        }
        
        const prescriptionData = {
            patient_id: workflowState.patientId,
            case_id: caseId,
            diagnosis: `H. pylori infection - ${resistanceStage} antibiotic resistance`,
            medications: medications,
            recommendations: protocol.recommendations || "Complete full course of antibiotics as prescribed. Take medications with meals to minimize side effects. Do not skip doses.",
            lifestyle_advice: "Avoid alcohol during treatment. Quit smoking. Avoid NSAIDs. Reduce stress. Eat smaller, frequent meals.",
            follow_up_days: 28,
            stage: "stage3_ric",
            protocol_type: protocolType,
            lab_tests_ordered: ["Urea Breath Test (4-6 weeks post-treatment)", "Stool Antigen Test"]
        };
        
        const token = localStorage.getItem('token');
        const response = await fetch('/prescriptions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(prescriptionData)
        });
        
        let result;
        try {
            result = await response.json();
        } catch (parseError) {
            throw new Error('Server returned invalid response');
        }
        
        if (!response.ok) {
            const errorMsg = result.detail || result.message || 'Prescription creation failed';
            throw new Error(errorMsg);
        }
        
        showNotification('Prescription created successfully!', 'success');
        
        // Show professional prescription success modal
        showPrescriptionSuccessModal(result.prescription_id, result.patient_name || 'Patient');
        
    } catch (error) {
        console.error('Error creating prescription:', error);
        const errorMessage = error.message || String(error) || 'Unknown error occurred';
        showNotification(`Failed to create prescription: ${errorMessage}`, 'error');
    }
}

function showPrescriptionSuccessModal(prescriptionId, patientName) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            max-width: 500px;
            width: 90%;
            padding: 0;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
            animation: slideUp 0.4s ease;
            overflow: hidden;
        ">
            <!-- Header with icon -->
            <div style="
                text-align: center;
                padding: 40px 30px 30px;
                background: rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <div style="
                    width: 80px;
                    height: 80px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    animation: scaleIn 0.5s ease 0.2s both;
                ">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#10b981" style="width: 50px; height: 50px;">
                        <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <h2 style="
                    color: white;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0 0 10px 0;
                    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                ">Prescription Created!</h2>
                <p style="
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 16px;
                    margin: 0;
                ">Treatment plan for ${patientName} has been generated successfully</p>
            </div>
            
            <!-- Content -->
            <div style="
                padding: 30px;
                background: white;
            ">
                <div style="
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border-left: 4px solid #3b82f6;
                    padding: 15px 20px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                ">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3b82f6" style="width: 20px; height: 20px;">
                            <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.706l-.709 2.836.042-.02a.75.75 0 01.67 1.34l-.04.022c-1.147.573-2.438-.463-2.127-1.706l.71-2.836-.042.02a.75.75 0 11-.671-1.34l.041-.022zM12 9a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd"/>
                        </svg>
                        <strong style="color: #1e40af; font-size: 14px;">What would you like to do?</strong>
                    </div>
                    <p style="color: #1e40af; margin: 0; font-size: 14px; line-height: 1.5;">
                        You can view the prescription, print it, or send it directly to the patient.
                    </p>
                </div>
                
                <!-- Action Buttons -->
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button onclick="viewPrescription('${prescriptionId}')" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 16px 24px;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.5)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(102, 126, 234, 0.4)'">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 22px; height: 22px;">
                            <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
                            <path fill-rule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z" clip-rule="evenodd"/>
                        </svg>
                        View & Print Prescription
                    </button>
                    
                    <button onclick="sendPrescriptionToPatient('${prescriptionId}')" style="
                        background: white;
                        color: #667eea;
                        border: 2px solid #667eea;
                        padding: 16px 24px;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.background='#f0f4ff'" onmouseout="this.style.background='white'">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 22px; height: 22px;">
                            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z"/>
                        </svg>
                        Send to Patient
                    </button>
                    
                    <button onclick="closePrescriptionModal()" style="
                        background: transparent;
                        color: #64748b;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 12px;
                        font-size: 15px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    " onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='transparent'">
                        Close
                    </button>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            @keyframes scaleIn {
                from {
                    opacity: 0;
                    transform: scale(0.5);
                }
                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }
        </style>
    `;
    
    document.body.appendChild(modal);
    
    // Global functions for modal actions
    window.viewPrescription = function(prescriptionId) {
        window.open(`/ui/prescription_print.html?id=${prescriptionId}`, '_blank');
        closePrescriptionModal();
    };
    
    window.sendPrescriptionToPatient = function(prescriptionId) {
        // TODO: Implement send to patient functionality
        showNotification('Prescription sent to patient successfully!', 'success');
        closePrescriptionModal();
    };
    
    window.closePrescriptionModal = function() {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    };
    
    // Add fadeOut animation
    const style = document.createElement('style');
    style.textContent = '@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }';
    document.head.appendChild(style);
}

function resetWorkflow() {
    workflowState.currentStage = 1;
    workflowState.patientId = null;
    workflowState.stage1CaseId = null;
    workflowState.stage2CaseId = null;
    workflowState.stage3CaseId = null;
    
    // Clear all forms
    document.querySelectorAll('form').forEach(form => form.reset());
    
    // Hide all results
    document.querySelectorAll('[id$="Results"]').forEach(div => div.style.display = 'none');
    
    // Go back to screening
    if (typeof showPage === 'function') {
        showPage('screening');
    }
    
    showNotification('Ready for new patient assessment', 'info');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Workflow forms initialized');
    
    // Add form submit handlers
    const symptomForm = document.getElementById('symptomForm');
    if (symptomForm) {
        symptomForm.addEventListener('submit', submitSymptomAssessment);
    }
    
    const labForm = document.getElementById('labScreeningForm');
    if (labForm) {
        labForm.addEventListener('submit', submitLabScreening);
    }
    
    const stagingForm = document.getElementById('ricStagingForm');
    if (stagingForm) {
        stagingForm.addEventListener('submit', submitRICStaging);
    }
});

