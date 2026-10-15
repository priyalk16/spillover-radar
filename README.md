# 📡 Spillover Radar
### A One Health Predictive Surveillance, Geospatial Risk Corridor Tracking, and Explainable Trace-Back Platform

---

## 👥 The Team: VetTech Trio

| Name | Role | Institutional Background | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Parth Kantharia** | **Team Lead & Veterinary Domain Lead** | 4th Year B.V.Sc. & A.H., Mumbai Veterinary College (MAFSU) | Syndromic disease classification, veterinary triage rules, One Health epidemiological validation |
| **Priyal Kantharia** | **Full-Stack & Systems Engineer** | Computer Engineering | Pipeline architecture, GIS visualization, Leaflet interactive dashboard, buffer logic |
| **Rahul Bhojkar** | **Data & ML Engineer** | Electronics and Telecommunication Engineering | Isolation Forest anomaly detection, SHAP local attribution engine, feature normalization |

---

## 🎯 Executive Summary & Problem Statement

Over **60% of emerging infectious diseases (EIDs) and 75% of novel pathogens in humans are zoonotic**, originating primarily in livestock, wildlife, and domestic animal populations. India hosts the world’s largest livestock population—over **535 million animals**—which forms the economic backbone of over 100 million rural households.

Despite recurring national crises—including **Avian Influenza (H5N1), Nipah virus, Anthrax, Brucellosis, and Kyasanur Forest Disease (KFD)**—surveillance across India operates in fragmented institutional silos:
* **Veterinary Surveillance:** Confined to ICAR-NIVEDI (NADRES) with passive reporting.
* **Human Clinical Surveillance:** Recorded retrospectively in IDSP/IHIP (MoHFW) often 10 to 14 days after initial human transmission.
* **Environmental & Climate Data:** Isolated within IMD and ISRO Bhuvan satellite monitoring.

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

```text
                      DATA INGESTION LAYER [D.02]
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
             │ • Feature Importance Attribution Engine                │
             └───────────────────────────┬────────────────────────────┘
                                         ▼
                     COMMAND & GEOSPATIAL INTELLIGENCE [D.01]
             ┌────────────────────────────────────────────────────────┐
             │ • National & District Leaflet Heatmaps                 │
             │ • 5km Containment Buffer & Livestock Corridors         │
             │ • Explainable Factor Inspector (Why is it red?)        │
             │ • Rapid Actionable Veterinary Protocols                │
             └───────────────────────────┬────────────────────────────┘



🔬 Scientific Methodology & Mathematical Model1. Composite Sector Vulnerability Indexing (VetDistress)A weighted composite distress index per district over a rolling 14-day window:VetDistress = 2.5 × (Abortions) + 4.0 × (Unexplained Cattle Deaths) + 1.5 × (PPR/FMD Incidence)These veterinary coefficients prioritize acute reproductive and septic events indicative of zoonotic triggers (e.g., Brucellosis, Anthrax).2. Environmental Stress Multiplier (ClimateStress)Climate shocks force livestock displacement and stress pathogen transmission cycles:ClimateStress = 1.8 × (Temperature Anomaly °C) + (Precipitation Deficit % / 15)3. Isolation Forest Outbreak Anomaly ScoringGiven multi-sector feature matrix X = [VetDistress, ClimateStress, VaccineGap], the anomaly score is computed across an ensemble of isolation trees. The raw scores are mapped to an intuitive 0–100 Spillover Risk Score:Critical Risk (≥ 70): High probability of spillover transmission within 7–14 days.Watchlist (40 – 69): Emerging environmental or syndromic stress requiring targeted surveillance.Normal (< 40): Baseline endemic variance.🖥 User Interface & Core Dashboard FeaturesGeospatial Disease Heatmap & Livestock Corridors [D.01]: Interactive regional mapping with Leaflet.js. Districts are color-graded based on predictive risk scores.5km Containment Buffer Overlay: The "Toggle 5km Trace-Back Buffers" control projects an operational containment perimeter centered on primary livestock clusters for rapid ring vaccination.Top-3 Explainability Inspector [D.03]: Clicking any flagged district extracts the primary drivers contributing to the anomaly (e.g., Cluster Livestock Deaths & Abortions, Thermal Shock & Rainfall Deficit, or Vaccine Coverage Gap).Triage Protocol Directives: Translates outputs into actionable field instructions (e.g., Deploy Veterinary Mobile Unit + 5km Ring Vaccination).📊 Impact MetricsMetricTraditional BaselineSpillover Radar TargetOperational BenefitSpillover Detection Window14 days (Post-human hospital admission)3 days (Veterinary syndromic lead)11-day early warning bufferActionable District Visibility0% (Static map reports)100% (Attributed top-3 drivers)Eliminates field ambiguityField Veterinary Response Time7–10 days post-notification48 hoursRapid ring vaccination deploymentAverage Outbreak Scale~100+ cases< 30 cases70% reduction in transmissionEstimated Economic Loss₹10+ Crores / outbreak< ₹3 CroresProtection of rural livestock assets🛠 Tech StackMachine Learning & Analytics: Python, Scikit-Learn (Isolation Forest), NumPy, PandasGeospatial & Mapping: Leaflet.js, OpenStreetMap / CartoDB APIs, GeoJSON spatial buffersBackend & Serving: Python HTTP Server, SocketServer, RESTful JSON serializationFrontend Presentation: HTML5, CSS3, Responsive Dark Theme Dashboard⚡ Quickstart Guide (1-Command Execution)Bash# 1. Clone the repository
git clone [https://github.com/priyalk16/spillover-radar.git](https://github.com/priyalk16/spillover-radar.git)
cd spillover-radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Spillover Radar
python run.py
Running run.py executes the pipeline [D.02], trains the anomaly scoring engine [D.03], and opens the interactive GIS dashboard [D.01] at http://localhost:8000.📜 References & Epidemiological FrameworksWorld Health Organization (WHO), WOAH, UNEP, FAO: One Health Joint Plan of Action (2022–2026).ICAR-NIVEDI: National Animal Disease Referral Expert System (NADRES v2) Methodology.Integrated Disease Surveillance Programme (IDSP / IHIP): Operational Guidelines for Zoonotic Disease Surveillance, MoHFW, Government of India.Liu, F. T., Ting, K. M., & Zhou, Z. H.: Isolation Forest. Eighth IEEE International Conference on Data Mining (2008).Lundberg, S. M., & Lee, S. I.: A Unified Approach to Interpreting Model Predictions (SHAP). Advances in Neural Information Processing Systems 30 (2017).Developed for Hack4Pashudhan | Verdant Impact National Hackathon | Team ID: H4P-VC587GBK


