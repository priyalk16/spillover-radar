# 📡 Spillover Radar

### One Health surveillance dashboard: geospatial risk, livestock corridors, explainable anomaly detection and a 48-hour response workflow

**Hack4Pashudhan | Verdant Impact National Hackathon · Team ID `H4P-VC587GBK`**

> **Prototype status:** animal and human numbers are **simulated** unless you supply real data (see [Using real data](#-using-real-data)). Scores are relative anomaly indicators, not diagnoses or probabilities of spillover.

---

## 👥 Team: VetTech Trio

| Name | Role | Background | Responsibilities |
| :-- | :-- | :-- | :-- |
| **Parth Kantharia** | Team Lead & Veterinary Domain Lead | 4th Year B.V.Sc. & A.H., Mumbai Veterinary College (MAFSU) | Syndromic classification, triage rules, One Health validation |
| **Priyal Kantharia** | ML Engineer | Computer Engineering | Pipeline, server, GIS dashboard, alert workflow |
| **Rahul Bhojkar** | Data & ML Engineer | Electronics & Telecommunication Engineering | Isolation Forest, change-point detection, model attribution |

---

## 🎯 Problem

More than 60% of emerging infectious diseases are zoonotic. India has the world's largest livestock population, yet animal health (NADRES), human health (IDSP/IHIP) and climate data (IMD) are reported through separate systems. Three gaps follow:

1. **Surveillance lag:** abnormal animal deaths or abortions can precede human cases, but disconnected systems delay cross-sector investigation.
2. **Unexplained alerts:** district officers get a flag without knowing why.
3. **No trace-forward:** it is hard to see where infected animals may be moving next.

Spillover Radar fuses animal, climate and human indicators per district, flags unusual patterns, explains them, shows where risk may travel, and tracks the response against a 48-hour target.

---

## 🏆 Deliverables

| ID | Challenge deliverable | What is implemented | Where |
| :-- | :-- | :-- | :-- |
| **D.01** | Geospatial disease heatmaps and corridor tracking | Leaflet map with risk-scored markers, heatmap, curved livestock corridors (width = volume), 5 km buffer circles, week-by-week replay, downstream **corridor exposure index** | `run.py` (HTML template section 3) |
| **D.02** | Multi-sector data pipeline (animal, human, environment) | Fusion of animal, climate and human series per district-week; **live climate** from Open-Meteo; **CSV adapter** for real data; **case-replay** loader; data-completeness tracking; lag-correlation analysis | `run.py` sections 1–2 |
| **D.03** | Early outbreak anomaly detection | Weighted risk score + **Isolation Forest** + **CUSUM change-point** detector; two explanation views (score composition and Isolation Forest occlusion attribution); 2-week trend projection | `run.py` section 2 |

---

## ✨ Feature overview

### Detection and explanation
- **Risk score (0–100)** from a transparent weighted composite of animal distress, climate stress and vaccination gap.
- **Isolation Forest** trained on all district-weeks gives an independent anomaly score (0–100) and flag.
- **CUSUM** change-point detection on animal distress, and on human fever counts to measure lead time.
- **Two explanations per district:** (A) share of each indicator in the risk score; (B) Isolation Forest occlusion attribution (how much more "normal" the district looks if that indicator is set to the median).
- **Trend projection:** linear extrapolation of the last 4 weeks, 2 weeks ahead, with "could reach CRITICAL in ~N weeks".
- **Expert calibration:** sliders and three presets (general, vector-borne/climate-driven, vaccine-preventable) re-weight the score live.
- **Ring-vaccination what-if:** add 0–40% coverage to a district and see the projected score.

### Geospatial intelligence
- Score-labelled, size-scaled markers; critical districts pulse; labels, hover cards, legend, scale bar, fit-all and zoom-to-critical buttons.
- Curved corridors coloured by risk; selecting a district highlights its corridors.
- **Corridor exposure index:** downstream risk from origin score × corridor volume × destination unvaccinated share.
- 5 km buffers (true 5 km circle; use *Zoom to 5 km buffer*).
- Key-free basemaps (Esri Dark Gray, OpenStreetMap fallback, layer switcher). Optional official boundary overlay: place a GeoJSON at `data/india_boundary.geojson`.

### Response workflow
- **Alert Center** (🔔 in the header, red banner, pop-up): alerts open automatically when a district reaches CRITICAL (≥70). Workflow: *Flagged → Verified → Team dispatched → Samples sent → Closed*, with a **48-hour SLA clock** to dispatch.
- New-alert toast, sound and optional desktop notification.
- **Webhook** (`--webhook URL`) posts JSON when a new alert opens (works with Slack/Teams/n8n/Twilio functions).
- **Field-report intake:** submit abortions/deaths/PPR-FMD for a district; the pipeline re-runs and the map updates immediately.
- **Exports:** situation report (.txt), scores (.csv), copy-ready alert message for the District Veterinary Officer.
- **Languages:** English, हिन्दी, मराठी (UI, protocols, alert messages). Translations should be reviewed by native-speaking veterinarians before field use.

### Data quality and evidence
- **Data completeness** per district (last 3 weeks). Missing reports are **not** treated as zero disease: the last known value is carried forward and the district is flagged ⚠.
- **Data-source chips** in the header show whether each feed is *live*, *CSV*, *scenario* or *simulated*.
- **Evidence panel:** median lead of the animal change-point over the human change-point, and lag correlations (0–4 weeks).
- **Case-replay mode:** replay a documented outbreak and measure lead time against the official confirmation week.

---

## 🧮 How the score works

All series are **weekly** district values.

```text
VetDistress   = 2.5 × Abortions + 4.0 × Unexplained cattle deaths + 1.5 × PPR/FMD cases
ClimateStress = 1.8 × TempSpike(°C) + max(RainDeficit %, 0) / 15
VaccineGap    = (1 − VaccinationCoverage) × 10

Risk (0–100)  = 100 × ( 0.50 × min(VetDistress / 60, 1)
                      + 0.25 × min(ClimateStress / 10, 1)
                      + 0.25 × min(VaccineGap   / 10, 1) )

CRITICAL ≥ 70   |   WATCH 40–69   |   NORMAL < 40
```

- **Isolation Forest:** 300 trees, contamination 0.12, fitted on standardised features of **all district-weeks**. Its score is min-max scaled to 0–100. A district is flagged ML-anomalous only if the forest isolates it **and** its risk is above the cohort mean (direction-aware).
- **CUSUM:** baseline = first 3 weeks (standard deviation floored at 1), slack k = 0.5, threshold h = 4.
- **Occlusion attribution:** for each feature, set it to the median and measure how much more normal the Isolation Forest score becomes. This is an approximation for interpretation, not exact SHAP values.
- **Live climate (`--live`):** temperature spike = mean Tmax of the last 7 days minus mean of the prior 28 days; rainfall deficit = shortfall of the last 14 days against the prior 21-day rate. These are **short-baseline anomalies, not true climatology.**
- All coefficients and weights are **heuristic** and need veterinary-expert calibration and validation against historical outbreaks.

---

## 🏛 Architecture

```text
 DATA (animal · human · climate)            INGESTION [D.02]
 ├─ simulated demo series (default)         build_demo_data()
 ├─ data/surveillance.csv  (real data)      CSV adapter
 ├─ --scenario file.csv    (case replay)    scenario loader
 └─ Open-Meteo API (--live)                 live climate, auto-fallback
                    │
                    ▼
 FEATURE ENGINEERING + COMPLETENESS         VetDistress · ClimateStress · VaccineGap
                    │
                    ▼
 DETECTION & EXPLANATION [D.03]             weighted risk · Isolation Forest · CUSUM
                                            occlusion attribution · lag correlation
                    │
                    ▼
 PYTHON SERVER (127.0.0.1)                  GET  /api/districts.json
                                            POST /api/report · /api/ack · /api/refresh
                    │
                    ▼
 DASHBOARD [D.01]                           map · explainability · Alert Center
                                            calibration · what-if · exposure · exports
```

The dashboard polls `api/districts.json` every 30 seconds and re-renders when new data arrives.

---

## ⚡ Quickstart

**Requirements:** Python 3.10+, `numpy`, `pandas`, `scikit-learn`. Internet access is needed for map tiles (and for `--live`).

```bash
git clone https://github.com/priyalk16/spillover-radar.git
cd spillover-radar
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                      # opens http://localhost:8000
```

### Command-line options

| Command | What it does |
| :-- | :-- |
| `python run.py` | Simulated data, local server on port 8000 |
| `python run.py --live` | Fetch real weather from Open-Meteo, refresh every 30 min (`--refresh-min N`) |
| `python run.py --scenario FILE.csv` | Replay a documented outbreak with confirmation-week lead time |
| `python run.py --write-scenario-sample` | Write a synthetic example to `data/scenarios/` |
| `python run.py --webhook URL` | POST JSON to `URL` whenever a new CRITICAL alert opens |
| `python run.py --port 8080` | Use a different port |
| `python run.py --no-browser` | Do not open a browser tab |
| `python run.py --build-only` | Write `index.html` and `api/districts.json`, print the report, exit |

The server binds to `127.0.0.1` only, because the POST endpoints are unauthenticated.

---

## 📥 Using real data

Create `data/surveillance.csv` (a schema example is auto-written to `data/surveillance_sample.csv`). One row per district per week:

| Column | Meaning |
| :-- | :-- |
| `name`, `state`, `lat`, `lon` | District identity and centroid |
| `week` | Integer, 0 = oldest week |
| `abortions`, `deaths`, `ppr` | Weekly animal counts (leave blank if not reported) |
| `vax_cov` | Vaccination coverage, 0–1 |
| `temp_spike`, `rain_deficit` | Climate anomalies (°C, %) |
| `human_fever` | Weekly human febrile-illness count |

**Case replay:** save the same CSV plus a JSON with the same base name:

```json
{ "title": "…", "illustrative": false, "focus_district": "…",
  "confirmed_week": 9, "source": "citation or URL", "notes": "…" }
```

`confirmed_week` is 1-indexed (the week of official confirmation). The dashboard shows radar-flag and CUSUM lead time against it.

---

## 🔌 API

| Endpoint | Method | Purpose |
| :-- | :-- | :-- |
| `/api/districts.json` | GET | Full payload: scores, features, attribution, alerts, events, sources |
| `/api/report` | POST | `{"district","abortions","deaths","ppr"}` (0–500) added to the latest week, then re-scored |
| `/api/ack` | POST | `{"district": "<id>"}` advances that alert one workflow step |
| `/api/refresh` | POST | Re-fetch live climate (if `--live`) and recompute |

---


---

## 📊 Impact targets (illustrative, not verified)

These are **project goals**, not measured results. The baselines are illustrative assumptions and **must be replaced with cited sources** or removed before presenting as fact.

| Metric | Baseline (illustrative) | Target |
| :-- | :-- | :-- |
| Time from first veterinary signal to cross-sector alert | To be established with a cited source | Within 48 hours |
| Veterinary team dispatch after alert | To be established | Within 48 hours (tracked by the SLA clock) |
| Explanation shown for every flagged district | Not available | 100% |

**Validation plan:** retrospective reconstruction of documented outbreaks, lead-time measurement against confirmation dates, precision/recall and false-alert rate, geographic generalisation tests, and field response-time measurement.

---

## 🚧 Limitations and roadmap

**Current limitations**
- Default data is **synthetic**; the evidence panel then validates the pipeline, not the biology (the simulated human series is built with a 2-week lag).
- The risk score is a **heuristic composite**. With default weights, animal signals alone contribute at most 50 points, so reaching CRITICAL also needs climate or vaccination stress. Tune weights with veterinary experts.
- Isolation Forest is a second opinion on a small feature set (3 features); it is not a validated predictor of spillover.
- Server-side alerts use the default weights; calibration slider changes affect the dashboard view only.
- Livestock corridors and their volumes are illustrative until transport-permit or BAHIS data is linked.
- The 5 km buffer is a configurable circle around the district centroid, **not** a validated containment perimeter.
- `--live` climate uses short-baseline anomalies and requires internet access; NADRES and IDSP have no public live API, so animal and human data come from CSV.
- Basemap boundary depiction comes from the tile provider; use the Survey of India boundary overlay where official depiction is required.

**Not yet implemented (planned)**
- NDVI/vegetation and flood/drought indices, cattle-density normalisation, and a 7–21-day lag-window analysis on real data.
- Exact SHAP values; district choropleth polygons; vector-borne disease-specific models.
- Authenticated multi-user access and persistent alert storage.

---

## 🔐 Responsible use

- Record data provenance; never read missing data as zero disease (the dashboard tracks completeness).
- Use aggregated or de-identified health data under applicable governance.
- Every alert needs human verification by veterinary and public-health professionals before escalation.
- Monitor false alarms, missed outbreaks and geographic bias.

---

## 📜 References

1. WHO, WOAH, UNEP, FAO. *One Health Joint Plan of Action (2022–2026).*
2. ICAR-NIVEDI. National Animal Disease Referral Expert System (NADRES).
3. MoHFW, Government of India. IDSP / IHIP resources.
4. Liu, Ting & Zhou (2008). *Isolation Forest.* IEEE ICDM.
5. Page, E. S. (1954). *Continuous inspection schemes* (CUSUM). Biometrika 41.
6. Open-Meteo. Free weather API: https://open-meteo.com

---

## ⚠️ Disclaimer

Spillover Radar is a prototype for decision support. Its scores, thresholds, coefficients and targets require validation against real epidemiological data before any operational use. It does not replace laboratory confirmation, veterinary diagnosis, public-health investigation or official outbreak response.
