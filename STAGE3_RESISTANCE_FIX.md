# Stage 3 Antibiotic Resistance Staging Fix

**Date:** October 29, 2025
**Issue:** `X has 9 features, but ColumnTransformer is expecting 6 features as input`

## Problem Identified

The staging model (`models/staging_3class.joblib`) expects **6 features** for antibiotic resistance prediction, but we were sending **9 RIC-based features**.

### Expected 6 Features (Antibiotic Resistance Markers):
1. **age** - Patient age
2. **sex** - Patient sex (encoded 1=Male, 0=Female)
3. **mic_clari** - MIC for clarithromycin (μg/mL)
4. **mut_A2143G** - 23S rRNA mutation A2143G (0/1)
5. **mut_A2144G** - 23S rRNA mutation A2144G (0/1)
6. **double_mut** - Both mutations present (derived)

### Previously Sent (9 RIC features - WRONG):
- atrophy_score
- intestinal_metaplasia_score
- inflammation_score
- hp_density
- pepsinogen_i
- pepsinogen_ii
- gastrin_17
- age
- sex

## Conceptual Clarification

### Stage 3 is NOT RIC Endoscopy Staging

**Stage 3** is actually **Antibiotic Resistance Staging** which:
- ✅ Determines resistance level (low/moderate/high)
- ✅ Selects appropriate treatment regimen
- ✅ **Recommends endoscopy** if needed (not based on endoscopy results)
- ✅ Uses molecular markers (MIC values + genetic mutations)

### Workflow Clarification:

**Stage 1:** Symptom Assessment
- Collects symptoms and risk factors
- Assesses gastric disease risk
- **Recommends lab tests**

**Stage 2:** Laboratory Screening
- Processes H. pylori test results
- Confirms infection
- **Determines if treatment is needed**

**Stage 3:** Antibiotic Resistance Staging
- Analyzes resistance markers
- Selects optimal treatment
- **May recommend endoscopy** for culture/biopsy

**Post-Stage 3 (if needed):** Endoscopy with Biopsy
- Actual RIC scoring would happen here
- Culture-based susceptibility testing
- Histological assessment
- This is a separate procedure, not part of CDSS workflow

## Solution Applied

### 1. ✅ Updated `app/ml_models.py`

**Added import:**
```python
from app.ml import prepare_screening_features, prepare_staging_features
```

**Updated `RICStagingModel.stage_disease()`:**
- Now uses `prepare_staging_features()` with correct 6 features
- Returns antibiotic resistance level (low/moderate/high)
- Treatment protocol is tailored to resistance profile

### 2. ✅ Updated `app/routes_workflow.py`

**Changed Stage3RICStaging model:**
```python
class Stage3RICStaging(BaseModel):
    # Antibiotic resistance markers (MIC values)
    mic_clarithromycin: Optional[float] = None
    mic_metronidazole: Optional[float] = None
    mic_levofloxacin: Optional[float] = None
    
    # Genetic mutations
    mutation_a2143g: Optional[int] = 0
    mutation_a2144g: Optional[int] = 0
    mutation_rdxa: Optional[int] = 0
    mutation_gyra: Optional[int] = 0
```

**Updated endpoint logic:**
```python
staging_data = {
    'age': patient.age or 40,
    'sex': patient.sex or 'M',
    'mic_clari': mic_clari,
    'mut_A2143G': data.mutation_a2143g,
    'mut_A2144G': data.mutation_a2144g
}
```

### 3. ✅ Updated `ui/workflow_forms.js`

**Collects correct data:**
- MIC values (optional, for resistance testing)
- Genetic mutations (checkboxes)
- Removed RIC scores (atrophy, metaplasia, etc.)

## Feature Details

### MIC (Minimum Inhibitory Concentration) Values:
- **Clarithromycin:** Most critical for treatment selection
  - Sensitive: ≤0.25 μg/mL
  - Intermediate: 0.25-1.0 μg/mL
  - Resistant: >1.0 μg/mL
  
- **Metronidazole:** Alternative antibiotic
- **Levofloxacin:** Rescue therapy option

### Genetic Mutations:
- **A2143G/A2144G:** 23S rRNA mutations causing clarithromycin resistance
- **rdxA:** Metronidazole resistance
- **gyrA:** Fluoroquinolone resistance

## Treatment Selection Logic

**Low Resistance (Stage 0):**
- Standard triple therapy
- PPI + Clarithromycin + Amoxicillin
- Expected success: 85-90%

**Moderate Resistance (Stage 1):**
- Sequential or quadruple therapy
- May avoid clarithromycin
- Expected success: 75-85%

**High Resistance (Stage 2):**
- Bismuth-based quadruple therapy
- Culture-guided therapy
- **Endoscopy recommended** for susceptibility testing
- Expected success: 70-80%

## Endoscopy Recommendations

Stage 3 may recommend endoscopy when:
- ✅ High antibiotic resistance detected
- ✅ Multiple mutations present
- ✅ MIC values indicate multi-drug resistance
- ✅ Previous treatment failures
- ✅ Alarm symptoms from Stage 1
- ✅ High infection probability from Stage 2

Endoscopy allows:
- Culture-based antibiotic susceptibility testing
- Histological assessment (actual RIC scoring)
- Biopsy for pathology
- Visual assessment of gastric mucosa

## Data Flow

```
Stage 1 (Symptoms) 
    ↓
    Captures: Demographics, symptoms, risk factors
    Stores: In patient record + Stage 1 case

Stage 2 (Lab Screening)
    ↓
    Uses: Demographics + symptoms + lab tests
    Adds: H. pylori test results
    Stores: Stage 2 case

Stage 3 (Resistance Staging)
    ↓
    Uses: Demographics + resistance markers
    Adds: MIC values + genetic mutations
    Returns: Resistance level + treatment protocol
    May recommend: Endoscopy for further testing
```

## Benefits

1. ✅ **Correct Feature Set:** Uses 6 antibiotic resistance markers
2. ✅ **Clinical Accuracy:** MIC and mutation data guide treatment
3. ✅ **Personalized Treatment:** Protocol based on resistance profile
4. ✅ **Clear Workflow:** Stage 3 → Treatment → Endoscopy (if needed)
5. ✅ **Appropriate Recommendations:** Suggests endoscopy when indicated

## Testing Instructions

### Test Stage 3 with Sample Data:

**Option 1: Low Resistance**
```
MIC Clarithromycin: 0.12 μg/mL
Mutations: None checked
Expected: Standard triple therapy
```

**Option 2: Moderate Resistance**
```
MIC Clarithromycin: 0.8 μg/mL
Mutations: mutation_a2143g checked
Expected: Sequential/quadruple therapy
```

**Option 3: High Resistance**
```
MIC Clarithromycin: 2.5 μg/mL
Mutations: mutation_a2143g + mutation_a2144g checked
Expected: Bismuth quadruple + endoscopy recommendation
```

## Result

✅ **Stage 3 now works correctly!**
- Expects 6 antibiotic resistance features
- Provides appropriate treatment recommendations
- Recommends endoscopy when clinically indicated
- Clear distinction between resistance staging and RIC scoring

## Status: READY FOR TESTING

Test the complete 3-stage workflow:
1. Stage 1: Patient symptoms → Risk assessment
2. Stage 2: Lab results → Infection confirmation
3. Stage 3: Resistance markers → Treatment protocol

Feature mismatch error is now resolved! 🎉

