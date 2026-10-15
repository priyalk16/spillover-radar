"""
Spillover Radar — Master Execution & Web Server Runner
Hackathon: Hack4Pashudhan (Verdant Impact) | Team ID: H4P-VC587GBK
Team: VetTech Trio (Parth Kantharia, Priyal Kantharia, Rahul Bhojkar)

Deliverables:
- D.01: Geospatial risk map & 5 km trace-back buffers (Leaflet GIS)
- D.02: Multi-sector data pipeline (animal + climate + human indicators)
- D.03: Outbreak anomaly detection (Isolation Forest + feature-contribution explainability)

Run:  python run.py          -> opens http://localhost:8000
      python run.py --no-browser
"""

import http.server
import json
import os
import socketserver
import sys
import webbrowser

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# 1. [D.02] MULTI-SECTOR DATA INGESTION & PIPELINE
# --------------------------------------------------------------------------
districts_data = [
    {"id": "D01", "name": "Barmer", "state": "Rajasthan", "lat": 25.7532, "lon": 71.3967,
     "abortions": 8, "deaths": 5, "ppr": 14, "vax_cov": 0.32,
     "temp_spike": 3.1, "rain_deficit": 46, "human_fever": 18},
    {"id": "D02", "name": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lon": 73.0243,
     "abortions": 5, "deaths": 3, "ppr": 9, "vax_cov": 0.41,
     "temp_spike": 2.4, "rain_deficit": 38, "human_fever": 11},
    {"id": "D03", "name": "Wayanad", "state": "Kerala", "lat": 11.6854, "lon": 76.1320,
     "abortions": 1, "deaths": 0, "ppr": 1, "vax_cov": 0.89,
     "temp_spike": 0.3, "rain_deficit": -4, "human_fever": 3},
    {"id": "D04", "name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567,
     "abortions": 2, "deaths": 1, "ppr": 0, "vax_cov": 0.74,
     "temp_spike": 1.1, "rain_deficit": 12, "human_fever": 6},
    {"id": "D05", "name": "Bikaner", "state": "Rajasthan", "lat": 28.0229, "lon": 73.3119,
     "abortions": 6, "deaths": 4, "ppr": 11, "vax_cov": 0.38,
     "temp_spike": 2.7, "rain_deficit": 40, "human_fever": 14},
]

df = pd.DataFrame(districts_data)

# Composite indices (heuristic weights — need veterinary expert calibration)
df["vet_distress_idx"] = df["abortions"] * 2.5 + df["deaths"] * 4.0 + df["ppr"] * 1.5
df["climate_stress_idx"] = df["temp_spike"] * 1.8 + df["rain_deficit"].clip(lower=0) / 15.0
df["vax_deficit"] = (1.0 - df["vax_cov"]) * 10.0

features = ["vet_distress_idx", "climate_stress_idx", "vax_deficit"]
factor_names = [
    "Livestock Deaths, Abortions & PPR",
    "Thermal Shock & Rainfall Deficit",
    "Vaccination Coverage Deficit",
]

# --------------------------------------------------------------------------
# 2. [D.03] RISK SCORING + ANOMALY DETECTION
# --------------------------------------------------------------------------
# (a) Direction-aware severity score (0-100): higher distress => higher risk.
#     Each feature is scaled against a fixed reference cap, so scores are
#     absolute (not forced to 0/100 by min-max on a tiny sample).
REF_CAP = np.array([60.0, 10.0, 10.0])      # "very severe" reference level per feature
WEIGHTS = np.array([0.50, 0.25, 0.25])      # heuristic weights (sum = 1)

X = df[features].values
norm = np.clip(X / REF_CAP, 0.0, 1.0)
contrib = norm * WEIGHTS                    # per-feature contribution to the score
df["risk_score"] = np.round(contrib.sum(axis=1) * 100, 1)

# (b) Isolation Forest on standardised features — secondary "unusual pattern" flag.
#     Flag only counts when the district is on the HIGH-risk side of the sample,
#     so a healthy outlier is never reported as an outbreak signal.
X_std = StandardScaler().fit_transform(X)
iso = IsolationForest(n_estimators=200, contamination=0.4, random_state=42).fit(X_std)
iso_flag = iso.predict(X_std) == -1
above_mean = df["risk_score"].values > df["risk_score"].mean()
df["ml_anomaly"] = iso_flag & above_mean

results = []
for i, row in df.iterrows():
    c = contrib[i]
    share = c / c.sum() * 100 if c.sum() > 0 else np.zeros(3)
    order = np.argsort(c)[::-1]
    factors = [f"{factor_names[j]} — {share[j]:.0f}% of score" for j in order]

    score = float(row["risk_score"])
    status = "CRITICAL" if score >= 70 else "WATCH" if score >= 40 else "NORMAL"
    action = {
        "CRITICAL": "Deploy Veterinary Rapid Response, verify reports & consider targeted 5 km ring vaccination",
        "WATCH": "Increase syndromic surveillance, verify animal reports, review vaccination gaps",
    }.get(status, "Routine Syndromic Monitoring")

    results.append({
        "id": row["id"], "name": row["name"], "state": row["state"],
        "lat": float(row["lat"]), "lon": float(row["lon"]),
        "score": score, "status": status, "factors": factors, "action": action,
        "deaths": int(row["deaths"]), "abortions": int(row["abortions"]),
        "human_fever": int(row["human_fever"]),
        "ml_anomaly": bool(row["ml_anomaly"]),
    })

# --------------------------------------------------------------------------
# 3. [D.01] GENERATE DASHBOARD HTML
# --------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Spillover Radar | One Health Platform</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body { margin: 0; font-family: -apple-system, 'Segoe UI', sans-serif; background: #0a0f1d; color: #fff; }
    header { background: #0f172a; padding: 14px 24px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }
    .badge { background: #0284c7; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    #container { display: flex; height: calc(100vh - 60px); }
    #map { flex: 1; }
    #panel { width: 380px; background: #0f172a; border-left: 1px solid #1e293b; padding: 20px; overflow-y: auto; }
    .card { background: #1e293b; border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid #334155; }
    .btn { background: #ef4444; color: #fff; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; }
    .legend span { display: inline-block; margin-right: 12px; font-size: 12px; color: #cbd5e1; }
    .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
    .note { font-size: 11px; color: #64748b; margin-top: 8px; }
  </style>
</head>
<body>
  <header>
    <div>
      <span class="badge">Team ID: H4P-VC587GBK</span>
      <strong style="margin-left: 10px; color: #38bdf8;">&#128225; Spillover Radar [D.01]</strong>
      <span style="color: #94a3b8; font-size: 12px; margin-left: 10px;">VetTech Trio (Parth, Priyal, Rahul)</span>
    </div>
    <button class="btn" onclick="toggleBuffers()">Toggle 5km Trace-Back Buffers</button>
  </header>
  <div id="container">
    <div id="map"></div>
    <div id="panel">
      <div class="card">
        <h3 id="dName" style="margin: 0 0 8px 0; color: #38bdf8;">Select a District Pin</h3>
        <p id="dStatus" style="font-size: 13px; color: #94a3b8; margin: 0;"></p>
        <div id="dScore" style="font-size: 32px; font-weight: bold; margin: 10px 0;">--</div>
        <div id="dMeta" style="font-size: 12px; color: #94a3b8;"></div>
      </div>
      <div class="card">
        <h4 style="margin: 0 0 10px 0; font-size: 13px; color: #cbd5e1;">Top Drivers (Feature Contribution) [D.03]</h4>
        <ul id="dFactors" style="padding-left: 20px; font-size: 12px; color: #e2e8f0; line-height: 1.6; margin: 0;"></ul>
        <div class="note">Share of each indicator in the risk score. Not causal evidence.</div>
      </div>
      <div class="card">
        <h4 style="margin: 0 0 6px 0; font-size: 12px; color: #f59e0b;">ACTIONABLE VETERINARY PROTOCOL</h4>
        <p id="dAction" style="font-size: 12px; color: #cbd5e1; margin: 0;">Click any district marker on the map.</p>
      </div>
      <div class="card legend">
        <span><i class="dot" style="background:#ef4444"></i>Critical &ge; 70</span>
        <span><i class="dot" style="background:#f59e0b"></i>Watch 40&ndash;69</span>
        <span><i class="dot" style="background:#10b981"></i>Normal &lt; 40</span>
        <div class="note">Prototype decision-support tool. Scores are relative indicators, not calibrated probabilities.</div>
      </div>
    </div>
  </div>
  <script>
    const data = __DATA__;
    const map = L.map('map').setView([22.5937, 78.9629], 5);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 18
    }).addTo(map);

    const colorFor = s => s >= 70 ? '#ef4444' : s >= 40 ? '#f59e0b' : '#10b981';
    let buffers = [];
    let showBuffers = false;

    data.forEach(d => {
      const color = colorFor(d.score);
      const marker = L.circleMarker([d.lat, d.lon], { radius: 10, fillColor: color, color: '#fff', weight: 1.5, fillOpacity: 0.85 }).addTo(map);
      marker.bindTooltip(d.name + ' (' + d.score + ')');
      buffers.push(L.circle([d.lat, d.lon], { radius: 5000, color: color, fillColor: color, fillOpacity: 0.2 }));
      marker.on('click', () => selectDistrict(d));
    });

    function selectDistrict(d) {
      document.getElementById('dName').innerText = d.name + ', ' + d.state;
      document.getElementById('dStatus').innerText = 'Status: ' + d.status + ' | Deaths: ' + d.deaths + ', Abortions: ' + d.abortions;
      const scoreEl = document.getElementById('dScore');
      scoreEl.innerText = d.score + ' / 100';
      scoreEl.style.color = colorFor(d.score);
      document.getElementById('dMeta').innerText =
        'Human fever cases: ' + d.human_fever + ' | ML anomaly flag: ' + (d.ml_anomaly ? 'YES' : 'no');
      const list = document.getElementById('dFactors');
      list.innerHTML = '';
      d.factors.forEach(f => { const li = document.createElement('li'); li.innerText = f; list.appendChild(li); });
      document.getElementById('dAction').innerText = d.action;
    }

    function toggleBuffers() {
      showBuffers = !showBuffers;
      buffers.forEach(b => { if (showBuffers) b.addTo(map); else map.removeLayer(b); });
    }

    const top = data.reduce((a, b) => (b.score > a.score ? b : a), data[0]);
    selectDistrict(top);
  </script>
</body>
</html>"""

html_content = HTML_TEMPLATE.replace("__DATA__", json.dumps(results))
index_path = os.path.join(BASE_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# --------------------------------------------------------------------------
# 4. TERMINAL REPORT + LOCAL WEB SERVER
# --------------------------------------------------------------------------
print("\n[D.02] Data pipeline & [D.03] ML anomaly scoring finished successfully.")
print(f"{'District':<10}{'State':<13}{'Score':>6}  {'Status':<9}{'ML flag':<8}Top driver")
for r in sorted(results, key=lambda x: -x["score"]):
    print(f"{r['name']:<10}{r['state']:<13}{r['score']:>6}  {r['status']:<9}"
          f"{'YES' if r['ml_anomaly'] else '-':<8}{r['factors'][0]}")
print(f"\n[D.01] Dashboard written to: {index_path}")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):  # quieter console
        pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    try:
        with ReusableTCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print(f"Serving at {url}  (Ctrl+C to stop)")
            if "--no-browser" not in sys.argv:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
            httpd.serve_forever()
    except OSError as e:
        print(f"Could not start server on port {PORT}: {e}\nClose whatever is using it or change PORT.")
    except KeyboardInterrupt:
        print("\nServer stopped.")
