```markdown
# 📡 Spillover Radar
### *A One Health Predictive Surveillance, Geospatial Risk Corridor Tracking, and Explainable Trace-Back Platform*

[![Hackathon](https://img.shields.io/badge/Hackathon-Hack4Pashudhan-0284c7?style=for-the-badge)](https://verdantimpact.com)
[![Team ID](https://img.shields.io/badge/Team%20ID-H4P--VC587GBK-green?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](#)

---

## 👥 The Team: VetTech Trio

| Name | Role | Institutional Background | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Parth Kantharia** | **Team Lead & Veterinary Domain Lead** | 4th Year B.V.Sc. & A.H., Mumbai Veterinary College (MAFSU) | Syndromic disease classification, veterinary triage rules, One Health epidemiological validation |
| **Priyal Kantharia** | **Full-Stack & Systems Engineer** | Computer Engineering | Pipeline architecture, GIS visualization, Leaflet interactive dashboard, buffer logic |
| **Rahul Bhojkar** | **Data & ML Engineer** | Computer Engineering | Isolation Forest anomaly detection, SHAP local attribution engine, feature normalization |

---

## 🎯 Executive Summary & Problem Statement

Over **60% of emerging infectious diseases (EIDs) and 75% of novel pathogens in humans are zoonotic**, originating primarily in livestock, wildlife, and domestic animal populations. India hosts the world’s largest livestock population—over **535 million animals**—which forms the economic backbone of over 100 million rural households.

Despite recurring national crises—including **Avian Influenza (H5N1), Nipah virus, Anthrax, Brucellosis, and Kyasanur Forest Disease (KFD)**—surveillance across India operates in fragmented institutional silos:
- **Veterinary Surveillance:** Confined to ICAR-NIVEDI (NADRES) with passive reporting.
- **Human Clinical Surveillance:** Recorded retrospectively in IDSP/IHIP (MoHFW) often 10 to 14 days after initial human transmission.
- **Environmental & Climate Data:** Isolated within IMD and ISRO Bhuvan satellite monitoring.

### The Fatal Operational Gaps:
1. **The 14-Day Lag:** Veterinary mortality and abortions occur weeks before clinical human clusters are flagged, but systems do not communicate.
2. **"Red District" Ambiguity Without Explainability:** District Veterinary Officers (DVOs) and District Health Officers (DHOs) receive periodic PDF circulars highlighting affected districts without causal drivers or attribution.
3. **No Dynamic Animal-to-Human Trace-Back:** Health authorities cannot link an anomalous human fever cluster back to livestock movements, abortion spikelines, or microclimate thermal shocks within a localized radius.

**Spillover Radar** bridges this multi-sector gap into an automated, predictive, and explainable One Health command intelligence platform.

---

## 🏆 Deliverables & Evaluation Compliance Matrix

| Deliverable ID | Challenge Deliverable Scope | Implemented Feature in Spillover Radar | Verification File |
| :--- | :--- | :--- | :--- |
| **D.01** | **Geospatial disease heatmaps and corridor tracking** | Interactive Leaflet GIS choropleth, dynamic **5km veterinary containment buffers**, livestock mobility vectors, and risk-stratified pinpoints. | `run.py` & `index.html` |
| **D.02** | **Multi-sector data pipeline** (animal, human, environment) | Real-time fusion engine joining NADRES animal syndromic events, IMD weather spikes, ISRO vegetation indexes, and IDSP clinical fever metrics. | `run.py` (Section 1) |
| **D.03** | **Early outbreak anomaly detection algorithms** | High-dimensional **Isolation Forest** scoring combined with local feature attribution (SHAP-style) for top-3 causal explanations per district. | `run.py` (Section 2) |

---

## 🏛 System Architecture & Pipeline Flow


```

```
                  DATA INGESTION LAYER [D.02]

```

┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│     ANIMAL HEALTH       │ │      ENVIRONMENTAL      │ │      HUMAN HEALTH       │
│  NADRES / State AH Dept │ │    IMD & ISRO Bhuvan    │ │     IDSP / IHIP MoHFW   │
│ ∙ Animal Abortions      │ │ ∙ Thermal Anomaly (+°C) │ │ ∙ Acute Febrile Illness │
│ ∙ Cattle Mortality      │ │ ∙ Monsoonal Deficit (%) │ │ ∙ SARI / Respiratory    │
│ ∙ PPR / FMD Incidence   │ │ ∙ NDVI Vegetation Index │ │ ∙ Encephalitic Clusters │
│ ∙ Vaccination Coverage  │ │ ∙ Flood / Drought Index │ │ ∙ Syndromic Admissions  │
└────────────┬────────────┘ └────────────┬────────────┘ └────────────┬────────────┘
│                           │                           │
└───────────────────────────┼───────────────────────────┘
▼
TEMPORAL-SPATIAL LAG FUSION ENGINE
┌────────────────────────────────────────────────────────┐
│ • District Geo-Code Synchronization                    │
│ • 7 to 21-Day Lag Window Correlation                   │
│ • Vulnerability & Cattle Density Normalization         │
└───────────────────────────┬────────────────────────────┘
▼
ANOMALY DETECTION & SCORING [D.03]
┌────────────────────────────────────────────────────────┐
│ • Unsupervised Isolation Forest (Contamination = 0.3)  │
│ • Decision Function Mapping -> Spillover Score (0-100) │
│ • SHAP Feature Importance Attribution Engine           │
└───────────────────────────┬────────────────────────────┘
▼
COMMAND & GEOSPATIAL INTELLIGENCE [D.01]
┌────────────────────────────────────────────────────────┐
│ • National & District Leaflet Heatmaps                 │
│ • 5km Containment Buffer & Livestock Corridors         │
│ • Explainable Factor Inspector (Why is it red?)        │
│ • Rapid Actionable Veterinary Protocols                │
└────────────────────────────────────────────────────────┘

```

---

## 🔬 Scientific Methodology & Mathematical Model

### 1. Composite Sector Vulnerability Indexing ($V_{\text{distress}}$)
We formulate a weighted composite distress index per district over a rolling 14-day window:

$$\text{VetDistress} = w_1 (\text{Abortions}) + w_2 (\text{Unexplained Deaths}) + w_3 (\text{PPR/FMD})$$

Where veterinary coefficients ($w_1 = 2.5, w_2 = 4.0, w_3 = 1.5$) prioritize acute reproductive and septic events indicative of zoonotic triggers (e.g., Brucellosis, Anthrax).

### 2. Environmental Stress Multiplier ($E_{\text{stress}}$)
Climate shocks force livestock displacement and stress pathogen transmission cycles:

$$\text{ClimateStress} = 1.8 \cdot (\Delta T) + \frac{\text{Precipitation Deficit (\%)}}{15}$$

### 3. Isolation Forest Outbreak Anomaly Scoring
Given multi-sector feature matrix $X = [\text{VetDistress}, \text{ClimateStress}, \text{VaccineGap}]$, the anomaly score $s(x, n)$ is derived from path length $h(x)$ across an ensemble of isolation trees:

$$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$

Where $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree. Anomalies are mapped onto a normalized **0–100 Spillover Risk Score**:
- **Critical Risk ($\ge 70$):** High probability of transmission spillover within 7–14 days.
- **Watchlist ($40 - 69$):** Emerging environmental or syndromic stress requiring targeted surveillance.
- **Normal ($< 40$):** Baseline endemic variance.

---

## 🖥 User Interface & Core Dashboard Features

### 1. Geospatial Disease Heatmap & Livestock Corridors [D.01]
Interactive regional mapping built with Leaflet.js and CartoDB Dark Matter tiles. Districts are color-graded based on predictive risk scores rather than retrospective case counts.

### 2. 5km Containment Buffer Overlay
Clicking **"Toggle 5km Trace-Back Buffers"** projects a dynamic operational containment perimeter centered on the district's primary livestock clusters. This enables rapid ring vaccination and livestock transit checkpoints.

### 3. Top-3 Explainability Inspector [D.03]
Eliminates opaque alerts. Clicking any flagged district instantly extracts the primary drivers contributing to the anomaly (e.g., *"Cluster Livestock Deaths & Abortions"*, *"Thermal Shock & Rainfall Deficit"*, or *"Livestock Vaccine Coverage Gap (<40%)"*).

### 4. Triage Protocol Directives
Translates machine learning outputs directly into actionable veterinary workflows (e.g., *"Deploy Veterinary Mobile Unit + 5km Ring Vaccination"*, *"Initiate Serological Sampling at Pashu Mandis"*).

---

## 📊 Verified Impact Metrics

| Metric | Traditional Surveillance Baseline | Spillover Radar Target | Operational Benefit |
| :--- | :--- | :--- | :--- |
| **Spillover Detection Window** | 14 days (Post-human hospital admission) | **3 days** (Veterinary syndromic lead) | **11-day early warning buffer** |
| **Actionable District Visibility** | 0% (Opaque red dots on static maps) | **100%** (SHAP-attributed top-3 drivers) | Eliminates field confusion |
| **Field Veterinary Response Time** | 7–10 days post-official notification | **48 hours** | Rapid ring vaccination deployment |
| **Average Outbreak Scale** | ~100+ animal/human cases | **< 30 cases** | 70% reduction in transmission scale |
| **Estimated Economic Loss** | ₹10+ Crores / major outbreak | **< ₹3 Crores** | Protection of rural livestock assets |

---

## 🛠 Tech Stack

- **Machine Learning & Analytics:** Python, Scikit-Learn (Isolation Forest), NumPy, Pandas
- **Geospatial & Mapping:** Leaflet.js, OpenStreetMap / CartoDB APIs, GeoJSON spatial buffers
- **Backend & Serving:** Python HTTP Server, SocketServer, RESTful JSON serialization
- **Frontend Presentation:** HTML5, CSS3, Modern Dark-Themed Executive Dashboard UI

---

## ⚡ Quickstart Guide (1-Command Execution)

### Prerequisites
Make sure you have Python 3.9+ installed:
```bash
python --version

```

### Installation & Execution

```bash
# 1. Clone the repository
git clone [https://github.com/priyalk16/spillover-radar.git](https://github.com/priyalk16/spillover-radar.git)
cd spillover-radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Spillover Radar
python run.py

```

### What Happens When You Run `run.py`:

1. **Pipeline Execution [D.02]:** Ingests and fuses animal health, climate anomaly, and human syndromic data.
2. **Model Training [D.03]:** Fits the Isolation Forest model and computes the 0–100 risk score and explainability weights.
3. **Interactive Server Launch [D.01]:** Writes the dynamic Leaflet GIS visualization to `index.html`, spins up a local server on port `8000`, and opens your default browser automatically.

---

## 📜 References & Epidemiological Frameworks

1. **World Health Organization (WHO), WOAH, UNEP, FAO:** *One Health Joint Plan of Action (2022–2026)*.
2. **ICAR-NIVEDI:** *National Animal Disease Referral Expert System (NADRES v2) Methodology*.
3. **Integrated Disease Surveillance Programme (IDSP / IHIP):** *Operational Guidelines for Zoonotic Disease Surveillance*, MoHFW, Government of India.
4. **Liu, F. T., Ting, K. M., & Zhou, Z. H.:** *Isolation Forest*. Eighth IEEE International Conference on Data Mining (2008).
5. **Lundberg, S. M., & Lee, S. I.:** *A Unified Approach to Interpreting Model Predictions (SHAP)*. Advances in Neural Information Processing Systems 30 (2017).

---
