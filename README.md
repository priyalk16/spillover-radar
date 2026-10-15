# 📡 Spillover Radar
### A One Health Predictive Surveillance, Geospatial Risk Corridor Tracking, and Explainable Trace-Back Platform

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
