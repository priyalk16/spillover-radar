# 📡 Spillover Radar
> **A One Health Predictive Surveillance & Explainable Trace-Back Platform**  
> **Competition:** Hack4Pashudhan (Verdant Impact) | **Team ID:** `H4P-VC587GBK`  
> **Team VetTech Trio:**  
> - **Parth Kantharia** (Team Lead, 4th Year B.V.Sc. & A.H., Mumbai Veterinary College)  
> - **Priyal Kantharia** (Software & Systems Engineer)  
> - **Rahul Bhojkar** (Data & ML Engineer)

---

## 🏆 Deliverables Compliance

| Deliverable ID | Requirement | Implementation |
| :--- | :--- | :--- |
| **D.01** | Geospatial disease heatmaps & corridor tracking | Interactive Leaflet GIS, dynamic 5km buffer zones, livestock corridors (`run.py` & UI) |
| **D.02** | Multi-sector data pipeline | Cross-sector fusion of NADRES veterinary data, IMD climate anomalies, and IDSP human syndromic data |
| **D.03** | Early outbreak anomaly detection | Isolation Forest unsupervised detection + factor attribution explainability (SHAP style) |

---

## 🚀 How to Run (1-Command Execution)

```bash
# 1. Clone the repository
git clone [https://github.com/priyalk16/spillover-radar.git](https://github.com/priyalk16/spillover-radar.git)
cd spillover-radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the platform
python run.py
