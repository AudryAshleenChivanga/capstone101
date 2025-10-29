# 🎨 Figma Design Prompt - H. pylori CDSS Platform

## **Copy this prompt to update your Figma design:**

---

**Design a stunning, ultra-modern, "out-of-this-world" clinical decision support system for H. pylori management with the following specifications:**

## 🌟 **Overall Design Philosophy**
- **Style**: Modern, clean, professional medical platform with glassmorphism effects
- **Vibe**: Futuristic yet trustworthy, cutting-edge AI meets clinical reliability
- **Aesthetic**: Dark theme with vibrant purple gradients, 3D elements, and glass panels
- **Target Users**: Medical professionals, gastroenterologists, clinical researchers

---

## 🎨 **Color Palette**

### Primary Colors
- **Primary Purple**: `#667eea`
- **Secondary Purple**: `#764ba2`
- **Accent Pink**: `#f093fb`
- **Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)`

### Background Colors
- **Dark Base**: `#0a0a0f`
- **Mid Dark**: `#1a1a2e`
- **Deep Blue**: `#16213e`
- **Background Gradient**: `linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)`

### Text Colors
- **Primary Text**: Pure white `#ffffff`
- **Secondary Text**: `rgba(255, 255, 255, 0.75)`
- **Muted Text**: `rgba(255, 255, 255, 0.6)`
- **Subtle Text**: `rgba(255, 255, 255, 0.4)`

### Glassmorphism
- **Glass Background**: `rgba(255, 255, 255, 0.08)`
- **Glass Border**: `rgba(255, 255, 255, 0.15)`
- **Backdrop Blur**: 30-40px
- **Shadow**: `0 20px 60px rgba(0, 0, 0, 0.3)`

---

## 📱 **Key Screens to Design**

### 1. Landing Page (index.html)
**Layout:**
- Full-screen 3D stomach model as background (20-25% opacity)
- Gradient overlay for readability
- Centered hero section with floating glass cards

**Elements:**
- **Navigation Bar**: 
  - Glassmorphic bar at top
  - Logo with icon (circular bacteria symbol)
  - Navigation links (Features, Workflow)
  - Login button (gradient purple, glassmorphic hover)
  
- **Hero Section**:
  - Badge pill: "AI-Powered Clinical Decision Support" with green dot animation
  - Main heading: "Revolutionizing H. pylori Management" (80px, bold)
  - Gradient text for "H. pylori"
  - Subtitle describing platform (21px)
  - Two CTA buttons:
    - Primary: Purple gradient with shimmer effect
    - Secondary: Glass with border
  - Stats display: 89% Accuracy | 3-Stage Workflow | 24/7 AI Support
  
- **Floating Feature Cards** (3 cards):
  - Card 1: "Real-Time Analysis" (left side)
  - Card 2: "Smart Prescriptions" (bottom left)
  - Card 3: "Telemedicine" (right side)
  - All with mouse-follow parallax effect

- **Features Section**:
  - 6 feature cards in grid
  - Each card: Icon in purple gradient, title, description
  - Hover: Lift effect, enhanced glow
  
- **Workflow Timeline**:
  - 3 stages with numbered badges
  - Stage 1: Symptom Assessment
  - Stage 2: Laboratory Screening
  - Stage 3: RIC Staging
  - Connecting lines between stages

---

### 2. Login/Signup Page (login.html)
**Layout:**
- Same 3D background as landing page
- Centered authentication card (480px wide)
- "Back to Home" button top-left

**Authentication Card:**
- Glassmorphic floating card with subtle animation
- Logo icon at top (gradient purple circle, 68px)
- Card title: "Welcome Back" or "Create Account"
- Subtitle explaining purpose

**Form Elements:**
- Input fields with icons (user, lock, email icons)
- Labels with SVG icons
- Purple glow on focus
- Primary button: Gradient with shimmer and arrow icon
- Secondary button: Glass border for switching forms
- Help text with info icon at bottom

**States:**
- Login form (default)
- Registration form (toggles smoothly)
- Loading states with spinner
- Success/Error messages (colored banners)

---

### 3. Dashboard (dashboard_new.html)
**Layout:**
- Collapsible sidebar navigation (left)
- Main content area (center)
- Top header bar with user info

**Sidebar:**
- Logo at top
- Navigation items with icons:
  - Dashboard Overview
  - Screening (Stage 1)
  - Lab Screening (Stage 2)
  - Staging (Stage 3)
  - Case History
  - Video Consultation
  - Appointments
  - Profile
  - Admin Panel
- Expand/collapse toggle
- Active state highlighting

**Main Dashboard:**
- **Stats Cards** (4 cards in row):
  - Total Cases
  - High Risk Cases
  - Screenings Today
  - Stagings Today
  - Each with icon, number, and mini chart

- **Case History Section**:
  - Advanced filter panel:
    - Search by patient ID/name
    - Filter by case type (dropdown)
    - Filter by risk level (badges)
    - Date range picker
  - Professional table:
    - Columns: Patient ID | Patient Name | Case Type | Risk | Result | Clinician | Date | Actions
    - Risk badges: Color-coded (red=high, yellow=moderate, green=low)
    - Action buttons: View, Edit (admin only), Delete (admin only)
  - Pagination controls at bottom

---

### 4. Multi-Stage Screening Forms

#### **Stage 1: Symptom Assessment**
**Layout:**
- Progress indicator at top (Stage 1 of 3)
- Form sections with clear headings

**Sections:**
1. **Patient Demographics**:
   - Full Name, Age, Gender (Male/Female/Other)
   - Residence, Phone, Email
   - Grid layout, 2 columns

2. **Primary Symptoms**:
   - Checkbox grid (3-4 columns)
   - Light background with dark text
   - Icons for each symptom
   - 11 symptoms total
   - Visual feedback on selection

3. **Risk Factors**:
   - Family history (dropdown: Yes/No)
   - Previous ulcer (checkbox)
   - NSAID use (checkbox)
   - Smoking (checkbox)

4. **Symptom Duration**:
   - Slider or number input
   - Helper text

**Submit Button:**
- Large, gradient purple
- "Submit Assessment" text
- Arrow icon
- Loading spinner state

**Results Display:**
- Card with risk level indicator (colored circle)
- Risk percentage
- Alarm symptoms (if any) in red
- Recommended tests (bullet list)
- Clinical recommendations
- "Proceed to Stage 2" button (if applicable)

---

#### **Stage 2: Laboratory Screening**
**Layout:**
- Progress indicator (Stage 2 of 3)
- Patient ID pre-filled and read-only

**Sections:**
1. **Patient Info Display**:
   - Shows patient ID from Stage 1
   - Name, age (read-only)

2. **H. pylori Specific Tests**:
   - Stool Antigen Test (dropdown: Positive/Negative)
   - H. pylori IgG Serology (dropdown: Positive/Negative)

3. **Blood Markers**:
   - Hemoglobin (number input with unit)
   - WBC count (number input with unit)
   - CRP (number input with unit)
   - ESR (number input with unit)
   - Platelet count (number input with unit)
   - Each with normal range helper text

**Results:**
- Infection probability percentage
- Status (Positive/Negative/Inconclusive)
- Confidence level
- Proceed to Stage 3 recommendation

---

#### **Stage 3: RIC Staging**
**Layout:**
- Progress indicator (Stage 3 of 3)
- Patient ID pre-filled

**Sections:**
1. **MIC Values** (Antibiotic Resistance):
   - Clarithromycin (number input)
   - Metronidazole (number input)
   - Levofloxacin (number input)
   - Each with resistance threshold indicator

2. **Genetic Mutations**:
   - Checkbox list with descriptions
   - 23S rRNA mutations
   - gyrA mutations
   - pbp1 mutations

3. **Histological Assessment** (Optional):
   - Atrophy score (0-3 slider)
   - Intestinal metaplasia score (0-3 slider)
   - Inflammation score (0-3 slider)
   - H. pylori density (0-3 slider)

**Results:**
- Stage determination (Low/Moderate/High resistance)
- Treatment protocol recommendation
- Prescription generation option

---

### 5. Prescription Interface
**Layout:**
- Patient info header
- Prescription form
- Digital signature area
- Action buttons

**Elements:**
1. **Patient Summary**:
   - Patient ID, name, age, gender
   - Diagnosis summary
   - Stage information

2. **Prescription Form**:
   - Medication list (add/remove rows)
   - Each medication: Name, dosage, frequency, duration
   - Clinical recommendations (textarea)
   - Lifestyle advice (textarea)
   - Follow-up days (number input)

3. **Signature Canvas**:
   - Drawing area for digital signature
   - Clear button
   - Name and credentials input

4. **Actions**:
   - Save Draft button
   - Sign & Approve (gradient button)
   - Generate PDF button
   - Send via SMS button (with Twilio icon)

---

## 🎯 **UI Components Library**

### Buttons
1. **Primary Button**:
   - Gradient background (#667eea → #764ba2)
   - White text, 16-18px, bold
   - 18px padding, 14-16px border radius
   - Hover: Lift 3px, enhanced shadow
   - Shimmer effect on hover

2. **Secondary Button**:
   - Glass background with blur
   - Border: 2px solid glass color
   - White text
   - Hover: Lighter background, lift 2px

3. **Icon Button**:
   - Small circular or square
   - Glass background
   - Icon only
   - Hover: Glow effect

### Cards
1. **Glass Card**:
   - Background: rgba(255, 255, 255, 0.08)
   - Backdrop blur: 40px
   - Border: 1px solid rgba(255, 255, 255, 0.15)
   - Border radius: 20-24px
   - Shadow: 0 20px 60px rgba(0, 0, 0, 0.3)
   - Hover: Lift, enhanced glow

2. **Stat Card**:
   - Smaller glass card
   - Icon in gradient circle
   - Large number (bold, gradient text)
   - Label (small, muted)
   - Mini chart/sparkline

3. **Feature Card**:
   - Medium-large card
   - Icon in gradient box (top)
   - Title (22-24px, bold)
   - Description (15px, muted)
   - Hover: Float animation

### Form Elements
1. **Input Field**:
   - Background: rgba(255, 255, 255, 0.05)
   - Border: 2px solid rgba(255, 255, 255, 0.1)
   - Border radius: 12-14px
   - Padding: 16px 20px
   - Focus: Purple glow, enhanced background

2. **Dropdown/Select**:
   - Same style as input
   - Arrow icon on right
   - Dropdown menu: Glass panel

3. **Checkbox**:
   - Custom styled
   - Accent color: #00d4ff or purple gradient
   - Checkmark animation

4. **Radio Button**:
   - Custom styled
   - Gradient when selected

### Icons
- Use Feather Icons or similar modern icon set
- Medical icons: stethoscope, pill, test tube, heart
- UI icons: chevrons, check, X, search, filter
- Size: 20-24px for standard, 32-36px for features

### Typography
- **Font Family**: Inter (or similar modern sans-serif)
- **Headings**:
  - H1: 56-80px, weight 800, -0.03em letter-spacing
  - H2: 42-54px, weight 800, -0.02em letter-spacing
  - H3: 28-32px, weight 700
  - H4: 20-24px, weight 700
- **Body Text**: 15-16px, weight 400-500
- **Small Text**: 13-14px
- **Buttons**: 15-17px, weight 600-700

---

## 🎬 **Animations & Interactions**

### Micro-Animations
- **Button Hover**: 
  - Lift 2-4px
  - Shadow enhancement
  - Shimmer sweep (0.5s)
  
- **Card Hover**:
  - Lift 8-10px
  - Glow effect
  - Scale 1.02
  
- **Input Focus**:
  - Glow animation (0.3s ease)
  - Border color change
  - Background lighten

### Page Transitions
- **Fade In Up**: Hero content, cards (0.8s ease, stagger 0.1s)
- **Fade In Down**: Navigation (0.8s ease)
- **Slide In**: Sidebar (0.3s ease)
- **Pulse**: Badge dots, alerts (2-3s infinite)
- **Float**: Floating cards (6-8s ease-in-out infinite)

### Loading States
- **Spinner**: Gradient border, rotating
- **Skeleton**: Pulsing glass panels
- **Progress Bar**: Gradient fill, smooth animation

---

## 📐 **Layout & Spacing**

### Grid System
- **Desktop**: 12-column grid, 1400px max-width
- **Tablet**: 8-column grid, 768px breakpoint
- **Mobile**: 4-column grid, 640px breakpoint

### Spacing Scale
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px
- **2XL**: 48px
- **3XL**: 64px

### Border Radius Scale
- **Small**: 8-10px (inputs, small buttons)
- **Medium**: 12-16px (cards, buttons)
- **Large**: 20-24px (large cards, modals)
- **XLarge**: 30px+ (pills, badges)

---

## 🖼️ **Additional Elements**

### 3D Background
- Include screenshot/reference of 3D stomach model
- Opacity: 20-25%
- Slight blur: 1-2px
- Subtle rotation/animation

### Gradient Overlays
- Radial gradients for depth
- Linear gradients for flow
- Multiple layers for richness

### Illustrations
- Medical icons in gradient style
- Abstract shapes for decoration
- Minimal, clean line art

---

## 📱 **Responsive Breakpoints**

- **Desktop**: 1440px+ (full feature set)
- **Laptop**: 1024px-1439px (slightly compressed)
- **Tablet**: 768px-1023px (simplified layout)
- **Mobile**: 320px-767px (stacked, collapsible elements)

---

## ✨ **Special Features to Highlight**

1. **3D Model Integration**: Show how 3D stomach model appears in background
2. **Glassmorphism**: Demonstrate blur, transparency, layering
3. **Gradient Magic**: Show various gradient applications
4. **Micro-Interactions**: Animate hover states, clicks, loading
5. **Dark Theme Excellence**: Ensure proper contrast, readability
6. **Professional Medical Context**: Balance modern tech with medical trust
7. **Data Visualization**: Charts, graphs, progress indicators
8. **Accessibility**: Proper contrast ratios, focus states, keyboard navigation

---

## 🎨 **Mood Board References**
- Apple's modern web design (glassmorphism)
- Stripe Dashboard (data visualization)
- Linear App (clean, modern UI)
- Epic EHR (medical professionalism)
- Dribbble: Search "medical dashboard dark theme"

---

## 📝 **Notes for Designer**
- Maintain consistent 16px grid alignment
- Use auto-layout in Figma for responsive design
- Create component library for reusability
- Include hover/active/disabled states for all interactive elements
- Design both light and dark theme variants (focus on dark)
- Ensure WCAG AA accessibility standards
- Include loading/error/empty states for all screens

---

**Export Specifications:**
- **Format**: Figma file with organized layers
- **Naming**: Use consistent naming conventions
- **Components**: Create reusable component library
- **Variants**: Include all button/input states
- **Assets**: Export icons as SVG, images as PNG/WebP
- **Spacing**: Use Figma's auto-layout with 8px grid

---

**Deliverables:**
1. Complete Figma file with all screens
2. Component library
3. Style guide document
4. Prototype with interactions
5. Developer handoff specifications

