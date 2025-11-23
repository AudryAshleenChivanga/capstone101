"""
Generate a professional flow diagram showing the synthetic data generation process
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Define colors (medical theme)
color_input = '#E8F4F8'  # Light blue
color_process = '#B8E6F0'  # Medium blue
color_math = '#FFF4E6'  # Light orange
color_output = '#D4EDDA'  # Light green
color_arrow = '#2C5F82'  # Dark blue

# Title
ax.text(5, 11.5, 'Synthetic Dataset Generation Process', 
        fontsize=20, fontweight='bold', ha='center', va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#2C5F82', edgecolor='black', linewidth=2),
        color='white')
ax.text(5, 11, 'Mathematical Framework for 25,000 H. pylori Screening Samples', 
        fontsize=12, ha='center', va='top', style='italic', color='#555')

# ============= STEP 1: INPUT FEATURES =============
y_start = 9.5
box1 = FancyBboxPatch((0.2, y_start), 2.7, 1.4, boxstyle="round,pad=0.1", 
                       facecolor=color_input, edgecolor='black', linewidth=2.5)
ax.add_patch(box1)
ax.text(1.55, y_start + 1.15, 'STEP 1: Input Features', fontsize=12, fontweight='bold', ha='center')
ax.text(1.55, y_start + 0.85, 'Demographics:', fontsize=9, ha='center', fontweight='bold')
ax.text(1.55, y_start + 0.65, 'age, sex', fontsize=8, ha='center')
ax.text(1.55, y_start + 0.4, 'Socioeconomic:', fontsize=9, ha='center', fontweight='bold')
ax.text(1.55, y_start + 0.2, 'residence, sanitation,', fontsize=8, ha='center')
ax.text(1.55, y_start + 0.02, 'water, crowding', fontsize=8, ha='center')

# Demographics distribution
y_demo = y_start - 0.8
box_demo = FancyBboxPatch((0.2, y_demo), 2.7, 0.7, boxstyle="round,pad=0.05", 
                          facecolor='white', edgecolor='gray', linewidth=1.5, linestyle='--')
ax.add_patch(box_demo)
ax.text(1.55, y_demo + 0.5, 'Random Sampling:', fontsize=9, ha='center', fontweight='bold')
ax.text(1.55, y_demo + 0.28, 'age ~ Uniform(16, 75)', fontsize=8, ha='center', family='monospace')
ax.text(1.55, y_demo + 0.08, 'sex ~ Categorical(M/F)', fontsize=8, ha='center', family='monospace')

# ============= STEP 2: LINEAR PREDICTOR =============
y_linear = 7.5
box2 = FancyBboxPatch((3.3, y_linear), 3.4, 1.8, boxstyle="round,pad=0.1", 
                       facecolor=color_math, edgecolor='black', linewidth=2.5)
ax.add_patch(box2)
ax.text(5, y_linear + 1.55, 'STEP 2: Linear Predictor', fontsize=12, fontweight='bold', ha='center')
ax.text(5, y_linear + 1.25, 'Combine feature effects with coefficients:', fontsize=8.5, ha='center', fontstyle='italic')

# Mathematical formula
formula_text = r'$\mathbf{LP} = \beta_0 + \sum_{i=1}^{n} \beta_i x_i$'
ax.text(5, y_linear + 0.85, formula_text, fontsize=13, ha='center', 
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5))

# Coefficient examples
ax.text(5, y_linear + 0.45, 'β₀ = -0.1 (baseline)', fontsize=8, ha='center', family='monospace')
ax.text(5, y_linear + 0.3, 'β_age = 0.01 × (age - 35)', fontsize=8, ha='center', family='monospace')
ax.text(5, y_linear + 0.15, 'β_rural = +0.15, β_urban = -0.10', fontsize=8, ha='center', family='monospace')
ax.text(5, y_linear + 0.0, 'β_symptoms = Σ wᵢ × symptomᵢ', fontsize=8, ha='center', family='monospace')

# Arrow 1 -> 2
arrow1 = FancyArrowPatch((2.9, y_start + 0.5), (3.3, y_linear + 1.3),
                         arrowstyle='->', mutation_scale=20, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow1)
ax.text(3.1, y_start - 0.4, '20 features\n× n=25,000', fontsize=8, ha='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', edgecolor='orange', alpha=0.8))

# ============= STEP 3: LOGISTIC FUNCTION =============
y_logit = 5.0
box3 = FancyBboxPatch((3.3, y_logit), 3.4, 1.5, boxstyle="round,pad=0.1", 
                       facecolor=color_process, edgecolor='black', linewidth=2.5)
ax.add_patch(box3)
ax.text(5, y_logit + 1.25, 'STEP 3: Logistic Function', fontsize=12, fontweight='bold', ha='center')
ax.text(5, y_logit + 1.0, 'Transform to probability [0, 1]:', fontsize=8.5, ha='center', fontstyle='italic')

# Sigmoid formula
sigmoid_formula = r'$P(infection) = \frac{1}{1 + e^{-LP}}$'
ax.text(5, y_logit + 0.6, sigmoid_formula, fontsize=14, ha='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='black', linewidth=2))

ax.text(5, y_logit + 0.15, 'Sigmoid/Logistic Function', fontsize=8.5, ha='center', style='italic', color='#555')

# Arrow 2 -> 3
arrow2 = FancyArrowPatch((5, y_linear), (5, y_logit + 1.5),
                         arrowstyle='->', mutation_scale=20, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow2)
ax.text(5.5, y_linear - 0.4, 'Apply\nsigmoid', fontsize=8, ha='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='yellow', edgecolor='orange', alpha=0.8))

# ============= STEP 4: BERNOULLI SAMPLING =============
y_bern = 3.2
box4 = FancyBboxPatch((3.3, y_bern), 3.4, 1.0, boxstyle="round,pad=0.1", 
                       facecolor=color_process, edgecolor='black', linewidth=2.5)
ax.add_patch(box4)
ax.text(5, y_bern + 0.75, 'STEP 4: True Infection Status', fontsize=12, fontweight='bold', ha='center')

# Bernoulli formula
bern_formula = r'$hp\_true_i \sim Bernoulli(P_i)$'
ax.text(5, y_bern + 0.3, bern_formula, fontsize=12, ha='center',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='black', linewidth=1.5))

# Arrow 3 -> 4
arrow3 = FancyArrowPatch((5, y_logit), (5, y_bern + 1.0),
                         arrowstyle='->', mutation_scale=20, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow3)
ax.text(5.5, y_logit - 0.4, 'Random\nsampling', fontsize=8, ha='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='yellow', edgecolor='orange', alpha=0.8))

# ============= STEP 5: TEST SIMULATION (LEFT) =============
y_test = 1.2
box5a = FancyBboxPatch((0.2, y_test), 2.5, 1.3, boxstyle="round,pad=0.1", 
                        facecolor=color_math, edgecolor='black', linewidth=2.5)
ax.add_patch(box5a)
ax.text(1.45, y_test + 1.05, 'STEP 5A: Stool Tests', fontsize=11, fontweight='bold', ha='center')
ax.text(1.45, y_test + 0.8, 'Sensitivity & Specificity:', fontsize=8, ha='center', fontstyle='italic')

# Test formulas
ax.text(1.45, y_test + 0.55, 'Stool Antigen:', fontsize=8, ha='center', fontweight='bold')
ax.text(1.45, y_test + 0.38, 'Sens = 88%, Spec = 93%', fontsize=7.5, ha='center', family='monospace')
ax.text(1.45, y_test + 0.18, 'Stool Antibody:', fontsize=8, ha='center', fontweight='bold')
ax.text(1.45, y_test + 0.02, 'Sens = 78%, Spec = 96%', fontsize=7.5, ha='center', family='monospace')

# Arrow 4 -> 5a
arrow4a = FancyArrowPatch((3.5, y_bern + 0.3), (2.7, y_test + 1.0),
                          arrowstyle='->', mutation_scale=20, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow4a)

# ============= STEP 5: LAB VALUES (RIGHT) =============
box5b = FancyBboxPatch((7.15, y_test), 2.65, 1.3, boxstyle="round,pad=0.1", 
                        facecolor=color_math, edgecolor='black', linewidth=2.5)
ax.add_patch(box5b)
ax.text(8.48, y_test + 1.05, 'STEP 5B: Lab Values', fontsize=11, fontweight='bold', ha='center')
ax.text(8.48, y_test + 0.8, 'Normal distributions + effects:', fontsize=8, ha='center', fontstyle='italic')

# Lab formulas
ax.text(8.48, y_test + 0.55, 'Hb ~ N(13.8 - 0.6×infected, 1.5²)', fontsize=7.5, ha='center', family='monospace')
ax.text(8.48, y_test + 0.35, 'CRP ~ N(2.5 + 1.0×infected, 1.2²)', fontsize=7.5, ha='center', family='monospace')
ax.text(8.48, y_test + 0.15, 'WBC ~ N(6.5 + 0.3×infected, 1.2²)', fontsize=7.5, ha='center', family='monospace')

# Arrow 4 -> 5b
arrow4b = FancyArrowPatch((6.5, y_bern + 0.3), (7.2, y_test + 1.0),
                          arrowstyle='->', mutation_scale=20, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow4b)

# ============= STEP 6: FINAL OUTPUT =============
y_output = 0.2
box6 = FancyBboxPatch((3.3, y_output - 0.5), 3.4, 1.2, boxstyle="round,pad=0.1", 
                       facecolor=color_output, edgecolor='black', linewidth=3)
ax.add_patch(box6)
ax.text(5, y_output + 0.5, 'FINAL OUTPUT', fontsize=13, fontweight='bold', ha='center')
ax.text(5, y_output + 0.2, '25,000 Synthetic Patient Records', fontsize=10.5, ha='center', fontweight='bold')
ax.text(5, y_output - 0.05, '21 features: demographics + symptoms + labs + tests', fontsize=8, ha='center')
ax.text(5, y_output - 0.25, 'Target: hp_pos (63.7% positive, 36.3% negative)', fontsize=8, ha='center',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='green', linewidth=2))

# Arrows 5 -> 6
arrow5a = FancyArrowPatch((1.45, y_test), (3.8, y_output + 0.5),
                          arrowstyle='->', mutation_scale=22, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow5a)

arrow5b = FancyArrowPatch((8.48, y_test), (6.2, y_output + 0.5),
                          arrowstyle='->', mutation_scale=22, linewidth=2.5, color=color_arrow)
ax.add_artist(arrow5b)

# ============= KEY/LEGEND (MOVED TO BOTTOM LEFT) =============
legend_y = 8.3
legend_box = FancyBboxPatch((0.2, legend_y - 1.0), 2.7, 1.0, boxstyle="round,pad=0.1",
                            facecolor='#F0F8FF', edgecolor='gray', linewidth=1.5)
ax.add_patch(legend_box)
ax.text(1.55, legend_y - 0.1, 'Key Concepts:', fontsize=9, fontweight='bold', ha='center')
ax.text(0.35, legend_y - 0.35, '• Linear Predictor: Σ βᵢxᵢ', fontsize=7.5, va='top')
ax.text(0.35, legend_y - 0.55, '• Logistic: Real → Probability', fontsize=7.5, va='top')
ax.text(0.35, legend_y - 0.75, '• Bernoulli: Binary (0 or 1)', fontsize=7.5, va='top')
ax.text(0.35, legend_y - 0.95, '• Normal: Lab values N(μ,σ²)', fontsize=7.5, va='top')

# Statistics box (TOP RIGHT)
stats_y = 10.5
stats_box = FancyBboxPatch((7.0, stats_y - 1.1), 2.8, 1.1, boxstyle="round,pad=0.1",
                           facecolor='#FFF9E6', edgecolor='black', linewidth=1.5)
ax.add_patch(stats_box)
ax.text(8.4, stats_y - 0.1, 'Dataset Statistics', fontsize=9, fontweight='bold', ha='center')
ax.text(8.4, stats_y - 0.35, '> Total samples: 25,000', fontsize=7.5, ha='center')
ax.text(8.4, stats_y - 0.55, '> Positive cases: 15,933 (63.7%)', fontsize=7.5, ha='center')
ax.text(8.4, stats_y - 0.75, '> Negative cases: 9,067 (36.3%)', fontsize=7.5, ha='center')
ax.text(8.4, stats_y - 0.95, '> Features: 20 clinical variables', fontsize=7.5, ha='center')

# Footer
ax.text(5, -0.3, 'Africa-Contextualized Synthetic Data Generation for H. pylori Screening Model', 
        fontsize=8, ha='center', style='italic', color='#666',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8))

plt.tight_layout()
plt.savefig('presentation_graphs/synthetic_data_generation_flow.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("SUCCESS: Diagram saved to presentation_graphs/synthetic_data_generation_flow.png")
plt.close()

