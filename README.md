# 📡 Spillover Radar

### A One Health Predictive Surveillance, Geospatial Risk Corridor Tracking, and Explainable Trace-Back Platform

---

## 👥 The Team: VetTech Trio

| Name | Role | Institutional Background | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Parth Kantharia** | **Team Lead & Veterinary Domain Lead** | 4th Year B.V.Sc. & A.H., Mumbai Veterinary College (MAFSU) | Syndromic disease classification, veterinary triage rules, One Health epidemiological validation |
| **Priyal Kantharia** | **Full-Stack & Systems Engineer** | Computer Engineering | Pipeline architecture, GIS visualization, Leaflet interactive dashboard, buffer logic |
| **Rahul Bhojkar** | **Data & ML Engineer** | Electronics and Telecommunication Engineering | Isolation Forest anomaly detection, SHAP-style local attribution engine, feature normalization |

---

## 🎯 Executive Summary & Problem Statement

Over **60% of emerging infectious diseases (EIDs) and 75% of novel pathogens in humans are zoonotic**, originating primarily in livestock, wildlife, and domestic animal populations. India hosts the world's largest livestock population, with over **535 million animals**, which forms the economic backbone of over 100 million rural households.

Despite recurring national crises, including **Avian Influenza (H5N1), Nipah virus, Anthrax, Brucellosis, and Kyasanur Forest Disease (KFD)**, surveillance across India operates across fragmented institutional systems:

- **Veterinary Surveillance:** Animal disease surveillance through systems such as ICAR-NIVEDI's National Animal Disease Referral Expert System (NADRES).
- **Human Clinical Surveillance:** Disease reporting through IDSP/IHIP under the Ministry of Health and Family Welfare (MoHFW).
- **Environmental & Climate Data:** Weather and environmental observations from agencies such as IMD and satellite-based monitoring platforms such as ISRO Bhuvan.

### The Critical Operational Gaps

1. **The Surveillance Lag:** Veterinary mortality, abortions, and unusual animal syndromes may precede human cases, but disconnected reporting systems can delay cross-sector investigation.
2. **Limited Explainability:** District Veterinary Officers (DVOs) and District Health Officers (DHOs) may receive district-level alerts without clear explanations of the underlying risk factors.
3. **No Integrated Animal-to-Human Trace-Back:** Authorities need better ways to investigate potential links between human fever clusters, livestock movements, animal health events, and localized environmental changes.

**Spillover Radar** addresses these challenges through an integrated, predictive, explainable One Health surveillance and command intelligence platform.

The platform combines animal health, human health, and environmental indicators to identify unusual patterns, visualize geographic risk, explain contributing factors, and support targeted veterinary and public health investigations.

---

## 🏆 Deliverables & Evaluation Compliance Matrix

| Deliverable ID | Challenge Deliverable Scope | Implemented Feature in Spillover Radar | Verification File |
| :--- | :--- | :--- | :--- |
| **D.01** | **Geospatial disease heatmaps and corridor tracking** | Interactive Leaflet GIS visualization, dynamic **5 km veterinary containment buffers**, livestock mobility vectors, and risk-stratified map markers. | `run.py`, `index.html` |
| **D.02** | **Multi-sector data pipeline** covering animal, human, and environmental indicators | Data fusion pipeline designed to combine animal syndromic events, weather indicators, vegetation indexes, and human clinical fever metrics. | `run.py` — Section 1 |
| **D.03** | **Early outbreak anomaly detection algorithms** | Unsupervised Isolation Forest scoring combined with SHAP-style feature attribution to identify the top three contributing factors for each flagged district. | `run.py` — Section 2 |

---

## 🏛 System Architecture & Pipeline Flow

```text
                  DATA INGESTION LAYER [D.02]

┌─────────────────────────┐
│      ANIMAL HEALTH      │
│  NADRES / State AH Dept │
│                         │
│  • Animal Abortions     │
│  • Cattle Mortality     │
│  • PPR / FMD Incidence  │
│  • Vaccination Coverage │
└────────────┬────────────┘
             │
             │
┌────────────▼────────────┐
│    ENVIRONMENTAL DATA   │
│      IMD / ISRO Bhuvan  │
│                         │
│  • Temperature Anomaly  │
│  • Precipitation Deficit│
│  • NDVI Vegetation Index│
│  • Flood / Drought Index│
└────────────┬────────────┘
             │
             │
┌────────────▼────────────┐
│      HUMAN HEALTH       │
│     IDSP / IHIP MoHFW   │
│                         │
│  • Acute Febrile Illness│
│  • SARI / Respiratory   │
│  • Encephalitic Clusters│
│  • Syndromic Admissions │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│          TEMPORAL-SPATIAL LAG FUSION ENGINE             │
│                                                        │
│  • District Geo-Code Synchronization                   │
│  • 7–21-Day Lag Window Analysis                        │
│  • Vulnerability and Cattle Density Normalization      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           ANOMALY DETECTION & SCORING [D.03]           │
│                                                        │
│  • Unsupervised Isolation Forest                       │
│  • Anomaly Score Mapping to 0–100 Risk Scale           │
│  • Feature Attribution and Explainability              │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│       COMMAND & GEOSPATIAL INTELLIGENCE [D.01]          │
│                                                        │
│  • National and District-Level Risk Heatmaps           │
│  • 5 km Containment Buffers and Livestock Corridors    │
│  • Explainability Inspector: "Why Is It Red?"          │
│  • Veterinary Triage and Response Recommendations     │
└────────────────────────────────────────────────────────┘
```

### End-to-End Workflow

1. **Data Ingestion:** Collect or load animal health, human health, and environmental indicators.
2. **Data Harmonization:** Align district identifiers, dates, and feature formats across sectors.
3. **Temporal-Spatial Fusion:** Combine indicators over defined observation windows and investigate potential time-lag relationships.
4. **Anomaly Detection:** Apply Isolation Forest to identify districts with unusual combinations of risk indicators.
5. **Risk Scoring:** Transform model outputs into a normalized 0–100 risk score for dashboard interpretation.
6. **Explainability:** Identify the leading indicators associated with each flagged district.
7. **Geospatial Visualization:** Display district-level risk, livestock corridors, and configurable 5 km buffer overlays.
8. **Response Support:** Present risk-informed veterinary surveillance and investigation recommendations.

---

## 🔬 Scientific Methodology & Mathematical Model

### 1. Composite Sector Vulnerability Indexing — VetDistress

A weighted composite distress index is calculated for each district over a rolling 14-day observation window.

**Formula:**

\[
\text{VetDistress} =
2.5 \times \text{Abortions}
+ 4.0 \times \text{Unexplained Cattle Deaths}
+ 1.5 \times \text{PPR/FMD Incidence}
\]

The proposed weights prioritize selected animal health indicators for anomaly screening.

- **Abortions:** May indicate reproductive disease or other animal health problems.
- **Unexplained Cattle Deaths:** May indicate an acute health event requiring investigation.
- **PPR/FMD Incidence:** Represents reported disease activity and contributes to the overall veterinary distress index.

**Important:** These coefficients are initial heuristic weights, not established causal estimates. They require veterinary expert review, calibration, and validation against historical data.

### 2. Environmental Stress Multiplier — ClimateStress

Environmental changes can influence livestock health, vector activity, animal movement, and pathogen transmission conditions.

**Formula:**

\[
\text{ClimateStress} =
1.8 \times \text{Temperature Anomaly}
+ \frac{\text{Precipitation Deficit}}{15}
\]

Where:

- **Temperature Anomaly:** Deviation from a defined local climatological baseline, measured in °C.
- **Precipitation Deficit:** Percentage deviation from the expected precipitation over the selected observation period.

**Important:** The two terms require appropriate normalization before combination. The coefficient values are proposed parameters and must be calibrated using domain knowledge and historical observations.

### 3. Isolation Forest Outbreak Anomaly Scoring

The model uses a multi-sector feature matrix:

\[
X = [\text{VetDistress},\ \text{ClimateStress},\ \text{VaccineGap}]
\]

The **Isolation Forest** algorithm identifies observations that are unusually different from the baseline distribution.

The pipeline includes:

1. Feature preprocessing and normalization where appropriate.
2. Isolation Forest model fitting.
3. Anomaly score extraction using the model's scoring methods.
4. Transformation into a normalized **0–100 Spillover Risk Score**.
5. Feature attribution to support interpretation of flagged observations.

The resulting risk score is intended as a **relative anomaly indicator**, not a calibrated probability of zoonotic transmission.

#### Risk Classification

| Risk Level | Proposed Score | Interpretation |
| :--- | :--- | :--- |
| 🔴 **Critical Risk** | **70–100** | High-priority anomaly requiring prompt verification and targeted surveillance. |
| 🟠 **Watchlist** | **40–69** | Unusual environmental or syndromic patterns requiring further assessment. |
| 🟢 **Normal** | **0–39** | No anomaly exceeding the defined operational threshold. |

**Scientific limitation:** Anomaly detection alone cannot establish that a zoonotic spillover will occur within 7–14 days. That prediction requires prospective validation, representative historical data, and a clearly defined outbreak outcome.

---

## 🖥 User Interface & Core Dashboard Features

### 1. Geospatial Disease Heatmap & Livestock Corridors [D.01]

Interactive geographic visualization using Leaflet.js.

- Districts are color-coded according to their computed risk scores.
- Risk-stratified markers highlight districts requiring further investigation.
- Livestock movement corridors can be visualized when movement data is available.
- Map layers support geographic exploration of potential animal–environment–human health relationships.

### 2. 5 km Containment Buffer Overlay

The **"Toggle 5km Trace-Back Buffers"** control displays a 5 km radius around selected livestock clusters or geographic points.

Potential uses include:

- Identifying nearby veterinary facilities and animal populations.
- Prioritizing field investigation areas.
- Supporting targeted sampling and surveillance planning.
- Assisting veterinary authorities in evaluating possible ring-vaccination strategies where appropriate.

**Operational note:** A 5 km buffer is a configurable geographic search radius, not proof of an epidemiologically valid containment perimeter. Intervention boundaries must reflect the disease, transmission route, local conditions, and official veterinary guidance.

### 3. Top-3 Explainability Inspector [D.03]

Selecting a flagged district displays the leading indicators associated with its anomaly score.

Example explanations include:

- **Animal Health:** Elevated livestock mortality and abortion reports.
- **Environmental Stress:** Temperature anomalies and precipitation deficits.
- **Vaccination Gap:** Lower vaccination coverage relative to the relevant target or baseline.

The purpose is to help decision-makers understand why an observation was flagged and determine which data sources and field conditions require verification.

**Interpretability note:** SHAP-style explanations must be calculated using an appropriate attribution method. The top three indicators should not be described as causal drivers unless causal evidence supports that interpretation.

### 4. Triage Protocol Directives

The dashboard translates risk categories into proposed response recommendations, such as:

- Verify animal mortality and abortion reports.
- Deploy veterinary personnel for targeted field investigation.
- Increase surveillance in nearby animal populations.
- Review vaccination coverage and disease history.
- Coordinate with public health authorities when human syndromic signals are detected.
- Consider targeted sampling and vaccination according to disease-specific veterinary protocols.

Recommendations are intended to support expert decision-making, not replace veterinary or public health authority.

---

## 📊 Impact Metrics

The following values represent **proposed project targets**, not verified field outcomes.

| Metric | Traditional Baseline | Spillover Radar Target | Intended Operational Benefit |
| :--- | :--- | :--- | :--- |
| **Spillover Detection Window** | Illustrative 14-day post-admission baseline | Target of 3 days after a detectable veterinary signal | Potential 11-day earlier warning opportunity |
| **Actionable District Visibility** | Baseline to be established | Target of 100% of flagged districts displaying top-three indicators | Reduced ambiguity during investigation |
| **Field Veterinary Response Time** | Illustrative 7–10 days after notification | Target of 48 hours | Faster investigation and response coordination |
| **Average Outbreak Scale** | Illustrative 100+ cases | Target of fewer than 30 cases | Potential reduction in transmission if interventions are effective |
| **Estimated Economic Loss** | Illustrative ₹10+ crore per outbreak | Target of less than ₹3 crore | Potential reduction in livestock and economic losses |

### Impact Validation Plan

To determine whether these targets are achievable, the platform should be evaluated using:

- Historical outbreak and surveillance records.
- Retrospective anomaly detection and event reconstruction.
- Lead-time measurement against verified outbreak dates.
- Precision, recall, F1-score, and false-alert rates.
- District-level calibration and geographic generalization tests.
- Field response-time measurements.
- Economic impact estimates supported by documented assumptions and observed outcomes.

---

## 🛠 Tech Stack

### Machine Learning & Analytics
- Python
- Scikit-learn
- Isolation Forest
- NumPy
- Pandas
- Feature engineering and anomaly scoring
- SHAP-style feature attribution

### Geospatial & Mapping
- Leaflet.js
- OpenStreetMap
- CartoDB basemaps
- GeoJSON
- Geographic buffer calculations
- District-level spatial visualization

### Backend & Serving
- Python HTTP server
- `http.server`
- `socketserver`
- REST-style JSON serialization

### Frontend Presentation
- HTML5
- CSS3
- JavaScript
- Leaflet.js
- Responsive dark-theme dashboard

---

## ⚡ Quickstart Guide

### Prerequisites

- Python 3.10 or a compatible version specified by the project.
- Git.
- An internet connection for external map tiles, if required.
- The project repository and its dependency files.

### 1. Clone the Repository

```bash
git clone https://github.com/priyalk16/spillover-radar.git
cd spillover-radar
```

### 2. Create and Activate a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch Spillover Radar

```bash
python run.py
```

If the server starts successfully, open:

**http://localhost:8000**

The intended execution flow is:

- Run the multi-sector data pipeline [D.02].
- Generate anomaly scores and feature explanations [D.03].
- Serve the interactive geospatial dashboard [D.01].

**Note:** This quickstart assumes that `run.py`, `requirements.txt`, the dashboard assets, and the required input data are present in the repository. The actual startup behavior depends on the implemented code.

---

## 📁 Project Structure

The following is a suggested repository structure. Adjust it to match the actual files in your repository.

```text
spillover-radar/
├── run.py                  # Pipeline execution and application entry point
├── requirements.txt        # Python dependencies
├── index.html              # Interactive Leaflet dashboard
├── data/
│   ├── animal_health/      # Animal health indicators
│   ├── human_health/       # Human syndromic indicators
│   └── environmental/      # Climate and environmental indicators
├── models/                 # Anomaly detection and scoring components
├── assets/                 # CSS, JavaScript, and other frontend assets
├── README.md               # Project documentation
└── .gitignore              # Files excluded from version control
```

This structure is illustrative and should not be treated as a verified inventory of existing repository files.

---

## 🔐 Data Quality, Privacy & Responsible Use

Reliable surveillance depends on the quality and provenance of the input data.

- **Data Provenance:** Record the source, collection date, reporting period, and geographic coverage of each dataset.
- **Missing Data:** Identify incomplete reports and avoid interpreting missing observations as zero disease incidence.
- **Temporal Alignment:** Use consistent observation windows and explicitly document any lag assumptions.
- **Geographic Alignment:** Standardize district identifiers and account for administrative boundary changes.
- **Privacy:** Use appropriately aggregated or de-identified health data and follow applicable data governance requirements.
- **False Positives:** Provide a verification workflow before escalating model-generated alerts.
- **Human Oversight:** Require qualified veterinary and public health professionals to validate alerts and select interventions.
- **Model Validation:** Monitor false alarms, missed outbreaks, geographic bias, and performance drift.

The system is a decision-support prototype. Its anomaly scores should not be interpreted as confirmed diagnoses or definitive predictions of human infection.

---

## 📜 References & Epidemiological Frameworks

1. **World Health Organization (WHO), World Organisation for Animal Health (WOAH), United Nations Environment Programme (UNEP), and Food and Agriculture Organization of the United Nations (FAO).** *One Health Joint Plan of Action (2022–2026).*
2. **ICAR-NIVEDI.** National Animal Disease Referral Expert System (NADRES) and associated animal disease surveillance resources.
3. **Ministry of Health and Family Welfare, Government of India.** Integrated Disease Surveillance Programme (IDSP) and Integrated Health Information Platform (IHIP) resources.
4. **Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008).** *Isolation Forest.* Eighth IEEE International Conference on Data Mining.
5. **Lundberg, S. M., & Lee, S.-I. (2017).** *A Unified Approach to Interpreting Model Predictions.* Advances in Neural Information Processing Systems 30.

---

## 🏁 Hackathon Information

**Developed for:** Hack4Pashudhan | Verdant Impact National Hackathon

**Team:** VetTech Trio

**Team ID:** `H4P-VC587GBK`

**Repository:** [Spillover Radar on GitHub](https://github.com/priyalk16/spillover-radar)

---

## ⚠️ Disclaimer

Spillover Radar is a prototype for One Health surveillance, anomaly detection, geospatial visualization, and decision support.

Its scores, thresholds, coefficients, and impact targets require validation against appropriate epidemiological data before operational deployment. The platform does not replace laboratory confirmation, veterinary diagnosis, public health investigation, or official outbreak response procedures.
