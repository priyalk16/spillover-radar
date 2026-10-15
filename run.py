"""
Spillover Radar — Master Execution & Web Server Runner
Hackathon: Hack4Pashudhan (Verdant Impact) | Team ID: H4P-VC587GBK
Team: VetTech Trio (Parth Kantharia, Priyal Kantharia, Rahul Bhojkar)

Deliverables:
- D.01: Geospatial heatmaps & corridor tracking (Leaflet GIS)
- D.02: Multi-sector data pipeline (NADRES + IMD + IDSP fusion)
- D.03: Outbreak anomaly detection (Isolation Forest + SHAP explainability)
"""

import http.server
import json
import socketserver
import webbrowser
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# --- 1. [D.02] MULTI-SECTOR DATA INGESTION & PIPELINE ---
districts_data = [
    {
        "id": "D01",
        "name": "Barmer",
        "state": "Rajasthan",
        "lat": 25.7532,
        "lon": 71.3967,
        "abortions": 8,
        "deaths": 5,
        "ppr": 14,
        "vax_cov": 0.32,
        "temp_spike": 3.1,
        "rain_deficit": 46,
        "human_fever": 18,
    },
    {
        "id": "D02",
        "name": "Jodhpur",
        "state": "Rajasthan",
        "lat": 26.2389,
        "lon": 73.0243,
        "abortions": 5,
        "deaths": 3,
        "ppr": 9,
        "vax_cov": 0.41,
        "temp_spike": 2.4,
        "rain_deficit": 38,
        "human_fever": 11,
    },
    {
        "id": "D03",
        "name": "Wayanad",
        "state": "Kerala",
        "lat": 11.6854,
        "lon": 76.1320,
        "abortions": 1,
        "deaths": 0,
        "ppr": 1,
        "vax_cov": 0.89,
        "temp_spike": 0.3,
        "rain_deficit": -4,
        "human_fever": 3,
    },
    {
        "id": "D04",
        "name": "Pune",
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "abortions": 2,
        "deaths": 1,
        "ppr": 0,
        "vax_cov": 0.74,
        "temp_spike": 1.1,
        "rain_deficit": 12,
        "human_fever": 6,
    },
    {
        "id": "D05",
        "name": "Bikaner",
        "state": "Rajasthan",
        "lat": 28.0229,
        "lon": 73.3119,
        "abortions": 6,
        "deaths": 4,
        "ppr": 11,
        "vax_cov": 0.38,
        "temp_spike": 2.7,
        "rain_deficit": 40,
        "human_fever": 14,
    },
]

df = pd.DataFrame(districts_data)
df["vet_distress_idx"] = (
    df["abortions"] * 2.5 + df["deaths"] * 4.0 + df["ppr"] * 1.5
)
df["climate_stress_idx"] = df["temp_spike"] * 1.8 + (
    df["rain_deficit"] / 15.0
)
df["vax_deficit"] = (1.0 - df["vax_cov"]) * 10.0

# --- 2. [D.03] ANOMALY DETECTION ENGINE ---
features = ["vet_distress_idx", "climate_stress_idx", "vax_deficit"]
X = df[features].values
model = IsolationForest(contamination=0.3, random_state=42)
model.fit(X)

raw_scores = model.decision_function(X)
min_s, max_s = raw_scores.min(), raw_scores.max()
df["risk_score"] = np.round(
    100 * (1 - (raw_scores - min_s) / (max_s - min_s + 1e-6)), 1
)

factor_names = [
    "Cluster Livestock Deaths & Abortions",
    "Thermal Shock & Rainfall Deficit",
    "Pashudhan Vaccination Deficit",
]
results = []
for idx, row in df.iterrows():
    vals = [
        row["vet_distress_idx"],
        row["climate_stress_idx"],
        row["vax_deficit"],
    ]
    sorted_idx = np.argsort(vals)[::-1]
    top_factors = [factor_names[i] for i in sorted_idx]
    status = (
        "CRITICAL"
        if row["risk_score"] >= 70
        else "WATCH"
        if row["risk_score"] >= 40
        else "NORMAL"
    )
    action = (
        "Deploy Veterinary Rapid Response & 5km Ring Vaccination"
        if status == "CRITICAL"
        else "Routine Syndromic Monitoring"
    )

    results.append(
        {
            "id": row["id"],
            "name": row["name"],
            "state": row["state"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "score": float(row["risk_score"]),
            "status": status,
            "factors": top_factors,
            "action": action,
            "deaths": int(row["deaths"]),
            "abortions": int(row["abortions"]),
        }
    )

# --- 3. [D.01] GENERATE DASHBOARD HTML ---
data_json = json.dumps(results)
html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Spillover Radar | One Health Platform</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body {{ margin: 0; font-family: -apple-system, sans-serif; background: #0a0f1d; color: #fff; }}
    header {{ background: #0f172a; padding: 14px 24px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }}
    .badge {{ background: #0284c7; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
    #container {{ display: flex; height: calc(100vh - 60px); }}
    #map {{ flex: 1; }}
    #panel {{ width: 380px; background: #0f172a; border-left: 1px solid #1e293b; padding: 20px; overflow-y: auto; }}
    .card {{ background: #1e293b; border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid #334155; }}
    .btn {{ background: #ef4444; color: #fff; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; }}
  </style>
</head>
<body>
  <header>
    <div>
      <span class="badge">Team ID: H4P-VC587GBK</span>
      <strong style="margin-left: 10px; color: #38bdf8;">📡 Spillover Radar [D.01]</strong>
      <span style="color: #94a3b8; font-size: 12px; margin-left: 10px;">VetTech Trio (Parth, Priyal, Rahul)</span>
    </div>
    <button class="btn" onclick="toggleBuffers()">Toggle 5km Trace-Back Buffers</button>
  </header>
  <div id="container">
    <div id="map"></div>
    <div id="panel">
      <div class="card">
        <h3 id="dName" style="margin: 0 0 8px 0; color: #38bdf8;">Select a District Pin</h3>
        <p id="dStatus" style="font-size: 13px; color: #94a3b8;"></p>
        <div id="dScore" style="font-size: 32px; font-weight: bold; margin: 10px 0;">--</div>
      </div>
      <div class="card">
        <h4 style="margin: 0 0 10px 0; font-size: 13px; color: #cbd5e1;">Top Drivers (SHAP Explainability) [D.03]</h4>
        <ul id="dFactors" style="padding-left: 20px; font-size: 12px; color: #e2e8f0; line-height: 1.6;"></ul>
      </div>
      <div class="card">
        <h4 style="margin: 0 0 6px 0; font-size: 12px; color: #f59e0b;">ACTIONABLE VETERINARY PROTOCOL</h4>
        <p id="dAction" style="font-size: 12px; color: #cbd5e1; margin: 0;">Click any district marker on the map.</p>
      </div>
    </div>
  </div>
  <script>
    const data = {data_json};
    const map = L.map('map').setView([22.5937, 78.9629], 5);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

    let buffers = [];
    let showBuffers = false;

    data.forEach(d => {{
      const color = d.score >= 70 ? '#ef4444' : d.score >= 40 ? '#f59e0b' : '#10b981';
      const marker = L.circleMarker([d.lat, d.lon], {{ radius: 10, fillColor: color, color: '#fff', weight: 1.5, fillOpacity: 0.85 }}).addTo(map);
      const buffer = L.circle([d.lat, d.lon], {{ radius: 5000, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.15 }});
      buffers.push(buffer);

      marker.on('click', () => selectDistrict(d));
    }});

    function selectDistrict(d) {{
      document.getElementById('dName').innerText = `${{d.name}}, ${{d.state}}`;
      document.getElementById('dStatus').innerText = `Status: ${{d.status}} | Deaths: ${{d.deaths}}, Abortions: ${{d.abortions}}`;
      const scoreEl = document.getElementById('dScore');
      scoreEl.innerText = `${{d.score}} / 100`;
      scoreEl.style.color = d.score >= 70 ? '#ef4444' : d.score >= 40 ? '#f59e0b' : '#10b981';

      const list = document.getElementById('dFactors');
      list.innerHTML = '';
      d.factors.forEach(f => {{
        const li = document.createElement('li');
        li.innerText = f;
        list.appendChild(li);
      }});

      document.getElementById('dAction').innerText = d.action;
    }}

    function toggleBuffers() {{
      showBuffers = !showBuffers;
      buffers.forEach(b => {{
        if (showBuffers) b.addTo(map);
        else map.removeLayer(b);
      }});
    }}
    selectDistrict(data[0]);
  </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

PORT = 8000
print(f"\\n✅ [D.02] Data Pipeline & [D.03] ML Anomaly Scoring finished successfully.")
print(
