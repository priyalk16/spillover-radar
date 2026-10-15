"""
Spillover Radar v2 — One Health Surveillance Dashboard (pipeline + web server)
Hackathon: Hack4Pashudhan (Verdant Impact) | Team ID: H4P-VC587GBK
Team: VetTech Trio (Parth Kantharia, Priyal Kantharia, Rahul Bhojkar)

Deliverables:
- D.01: Geospatial risk map: heatmap, 5 km trace-back buffers, livestock corridors, week timeline
- D.02: Multi-sector pipeline: animal + climate + human indicators, lag fusion analysis
- D.03: Anomaly detection: Isolation Forest + direction-aware risk score + feature contribution

NOTE: all district numbers, weekly series and corridors are SIMULATED demo data.
Replace `build_demo_data()` with NADRES / IMD / IDSP feeds for real use.

Run:  python run.py              -> http://localhost:8000
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
WEEKS = 8
HUMAN_LAG_WEEKS = 2          # demo assumption: human fever trails vet distress by ~2 weeks
REF_CAP = np.array([60.0, 10.0, 10.0])     # "very severe" reference level per feature
WEIGHTS = np.array([0.50, 0.25, 0.25])     # heuristic weights (need vet-expert calibration)
FACTOR_NAMES = [
    "Livestock Deaths, Abortions & PPR",
    "Thermal Shock & Rainfall Deficit",
    "Vaccination Coverage Deficit",
]

# --------------------------------------------------------------------------
# 1. [D.02] MULTI-SECTOR DATA INGESTION (simulated demo feeds)
# --------------------------------------------------------------------------
# name, state, lat, lon, abortions, deaths, ppr, vax_cov, temp_spike, rain_deficit, start_factor
# start_factor = how severe the district was 7 weeks ago relative to now (<1 means rising)
DISTRICTS = [
    ("Barmer",     "Rajasthan",   25.7532, 71.3967, 8, 5, 14, 0.32, 3.1, 46, 0.35),
    ("Jodhpur",    "Rajasthan",   26.2389, 73.0243, 5, 3,  9, 0.41, 2.4, 38, 0.60),
    ("Bikaner",    "Rajasthan",   28.0229, 73.3119, 6, 4, 11, 0.38, 2.7, 40, 0.55),
    ("Jaisalmer",  "Rajasthan",   26.9157, 70.9083, 5, 3,  8, 0.44, 2.9, 44, 0.50),
    ("Jaipur",     "Rajasthan",   26.9124, 75.7873, 3, 1,  4, 0.63, 1.6, 22, 0.80),
    ("Kutch",      "Gujarat",     23.2420, 69.6669, 4, 2,  7, 0.52, 2.2, 31, 0.65),
    ("Ahmednagar", "Maharashtra", 19.0948, 74.7480, 3, 2,  3, 0.66, 1.4, 18, 0.85),
    ("Pune",       "Maharashtra", 18.5204, 73.8567, 2, 1,  0, 0.74, 1.1, 12, 1.00),
    ("Latur",      "Maharashtra", 18.4088, 76.5604, 3, 1,  5, 0.58, 1.8, 26, 0.75),
    ("Bhopal",     "Madhya Pradesh", 23.2599, 77.4126, 2, 1, 2, 0.71, 1.2, 14, 0.95),
    ("Wayanad",    "Kerala",      11.6854, 76.1320, 1, 0, 1, 0.89, 0.3, -4, 1.00),
    ("Kozhikode",  "Kerala",      11.2588, 75.7804, 1, 1, 1, 0.86, 0.5,  2, 1.05),
]

# Illustrative livestock movement corridors (replace with transport-permit / BAHIS data)
CORRIDORS = [
    ("Barmer", "Jodhpur", "Marwar cattle route"),
    ("Barmer", "Jaisalmer", "Thar border route"),
    ("Barmer", "Kutch", "Kutch–Barmer trade route"),
    ("Jodhpur", "Bikaner", "Western Rajasthan fair route"),
    ("Jodhpur", "Jaipur", "Jaipur mandi route"),
    ("Jaipur", "Bhopal", "Central India transit"),
    ("Pune", "Ahmednagar", "Deccan route"),
    ("Ahmednagar", "Latur", "Marathwada route"),
    ("Bhopal", "Ahmednagar", "Satpura transit"),
    ("Kozhikode", "Wayanad", "Malabar hill route"),
]


def build_demo_data():
    """Return a long dataframe: one row per district per week."""
    rng = np.random.RandomState(42)
    rows = []
    for (name, state, lat, lon, ab, de, pp, vc, ts, rd, start) in DISTRICTS:
        ramp = np.linspace(start, 1.0, WEEKS)
        vet_hist = []
        for w in range(WEEKS):
            f = ramp[w]
            noise = (lambda: 1 + rng.normal(0, 0.08)) if w < WEEKS - 1 else (lambda: 1.0)
            abortions = max(0, int(round(ab * f * noise())))
            deaths = max(0, int(round(de * f * noise())))
            ppr = max(0, int(round(pp * f * noise())))
            temp = round(ts * f * noise(), 2)
            rain = round(rd * f * noise(), 1)
            vet = abortions * 2.5 + deaths * 4.0 + ppr * 1.5
            vet_hist.append(vet)
            lagged = vet_hist[max(w - HUMAN_LAG_WEEKS, 0)]
            human = max(0, int(round(0.28 * lagged + rng.normal(0, 0.6))))
            rows.append(dict(name=name, state=state, lat=lat, lon=lon, week=w,
                             abortions=abortions, deaths=deaths, ppr=ppr, vax_cov=vc,
                             temp_spike=temp, rain_deficit=rain, human_fever=human))
    return pd.DataFrame(rows)


df = build_demo_data()

# --------------------------------------------------------------------------
# 2. [D.03] FEATURE ENGINEERING, RISK SCORING, ANOMALY DETECTION
# --------------------------------------------------------------------------
df["vet_distress_idx"] = df["abortions"] * 2.5 + df["deaths"] * 4.0 + df["ppr"] * 1.5
df["climate_stress_idx"] = df["temp_spike"] * 1.8 + df["rain_deficit"].clip(lower=0) / 15.0
df["vax_deficit"] = (1.0 - df["vax_cov"]) * 10.0
FEATURES = ["vet_distress_idx", "climate_stress_idx", "vax_deficit"]

norm = np.clip(df[FEATURES].values / REF_CAP, 0.0, 1.0)
contrib = norm * WEIGHTS
df["risk_score"] = np.round(contrib.sum(axis=1) * 100, 1)
shares = contrib / np.where(contrib.sum(axis=1, keepdims=True) == 0, 1, contrib.sum(axis=1, keepdims=True))
for j in range(3):
    df[f"share{j}"] = np.round(shares[:, j] * 100, 0)

# Isolation Forest on the latest week (standardised), flag only counts on the high-risk side
latest = df[df["week"] == WEEKS - 1].reset_index(drop=True)
Xs = StandardScaler().fit_transform(latest[FEATURES].values)
iso = IsolationForest(n_estimators=200, contamination=0.25, random_state=42).fit(Xs)
latest["ml_anomaly"] = (iso.predict(Xs) == -1) & (latest["risk_score"].values > latest["risk_score"].mean())

# Lag fusion: does human fever trail vet distress? (pooled, within-district demeaned)
def lag_correlations(max_lag=4):
    out = []
    for L in range(max_lag + 1):
        xs, ys = [], []
        for _, g in df.groupby("name"):
            v = g["vet_distress_idx"].values
            h = g["human_fever"].values
            t = np.arange(max_lag, WEEKS)
            x = v[t - L]; y = h[t]
            xs.extend(x - x.mean()); ys.extend(y - y.mean())
        r = float(np.corrcoef(xs, ys)[0, 1]) if np.std(xs) > 0 and np.std(ys) > 0 else 0.0
        out.append({"lag": L, "r": round(r, 3)})
    return out

lag_stats = lag_correlations()
best_lag = max(lag_stats, key=lambda d: d["r"])

# Package for the dashboard / API
districts_out = []
for name, g in df.groupby("name", sort=False):
    g = g.sort_values("week")
    last = latest[latest["name"] == name].iloc[0]
    districts_out.append({
        "id": name.lower(), "name": name, "state": g["state"].iloc[0],
        "lat": float(g["lat"].iloc[0]), "lon": float(g["lon"].iloc[0]),
        "scores": [float(x) for x in g["risk_score"]],
        "human": [int(x) for x in g["human_fever"]],
        "deaths": [int(x) for x in g["deaths"]],
        "abortions": [int(x) for x in g["abortions"]],
        "shares": [[int(g[f"share{j}"].iloc[w]) for j in range(3)] for w in range(WEEKS)],
        "vax_cov": float(g["vax_cov"].iloc[0]),
        "ml_anomaly": bool(last["ml_anomaly"]),
    })

payload = {
    "weeks": [f"Wk {w + 1}" for w in range(WEEKS)],
    "factorNames": FACTOR_NAMES,
    "districts": districts_out,
    "corridors": [{"from": a.lower(), "to": b.lower(), "name": n} for a, b, n in CORRIDORS],
    "lag": {"stats": lag_stats, "best": best_lag["lag"], "assumed": HUMAN_LAG_WEEKS},
}

# --------------------------------------------------------------------------
# 3. [D.01] DASHBOARD HTML
# --------------------------------------------------------------------------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spillover Radar | One Health Platform</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', sans-serif; background: #0a0f1d; color: #fff; }
  header { background: #0f172a; padding: 12px 20px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; height: 56px; }
  .badge { background: #0284c7; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
  .demo { background: #78350f; color: #fde68a; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
  #container { display: flex; height: calc(100vh - 56px); }
  #mapwrap { flex: 1; display: flex; flex-direction: column; min-width: 0; }
  #controls { background: #0f172a; border-bottom: 1px solid #1e293b; padding: 8px 14px; display: flex; gap: 14px; align-items: center; flex-wrap: wrap; font-size: 12px; color: #cbd5e1; }
  #controls label { cursor: pointer; display: flex; align-items: center; gap: 4px; }
  #map { flex: 1; }
  #panel { width: 400px; background: #0f172a; border-left: 1px solid #1e293b; padding: 14px; overflow-y: auto; }
  .card { background: #1e293b; border-radius: 8px; padding: 14px; margin-bottom: 12px; border: 1px solid #334155; }
  .card h4 { margin: 0 0 8px 0; font-size: 12px; color: #cbd5e1; letter-spacing: .3px; }
  .btn { background: #ef4444; color: #fff; border: none; padding: 7px 12px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 12px; }
  .btn.alt { background: #334155; }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
  .kpi { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px; text-align: center; }
  .kpi b { display: block; font-size: 20px; } .kpi span { font-size: 10px; color: #94a3b8; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  td, th { padding: 5px 4px; text-align: left; border-bottom: 1px solid #334155; }
  tr.row { cursor: pointer; } tr.row:hover { background: #273449; } tr.sel { background: #2b3b55; }
  .pill { padding: 1px 7px; border-radius: 10px; font-size: 10px; font-weight: 700; color: #0a0f1d; }
  .bar { height: 8px; border-radius: 4px; background: #334155; overflow: hidden; margin: 3px 0 7px; }
  .bar i { display: block; height: 100%; }
  .note { font-size: 11px; color: #64748b; margin-top: 6px; line-height: 1.4; }
  .flow { animation: dash 1.2s linear infinite; }
  @keyframes dash { to { stroke-dashoffset: -20; } }
  .legend span { display: inline-block; margin-right: 12px; font-size: 12px; color: #cbd5e1; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
  input[type=range] { width: 180px; }
</style>
</head>
<body>
<header>
  <div>
    <span class="badge">Team ID: H4P-VC587GBK</span>
    <strong style="margin-left: 10px; color: #38bdf8;">&#128225; Spillover Radar</strong>
    <span style="color: #94a3b8; font-size: 12px; margin-left: 10px;">VetTech Trio (Parth, Priyal, Rahul)</span>
    <span class="demo">SIMULATED DEMO DATA</span>
  </div>
  <div>
    <button class="btn alt" onclick="exportCSV()">Export CSV</button>
  </div>
</header>
<div id="container">
  <div id="mapwrap">
    <div id="controls">
      <label><input type="checkbox" id="lMarkers" checked> Risk markers</label>
      <label><input type="checkbox" id="lHeat" checked> Heatmap</label>
      <label><input type="checkbox" id="lBuf"> 5 km buffers</label>
      <label><input type="checkbox" id="lCor" checked> Livestock corridors</label>
      <span style="margin-left:auto"></span>
      <button class="btn alt" id="playBtn" onclick="togglePlay()">&#9654; Play</button>
      <input type="range" id="week" min="0" max="__LASTWEEK__" value="__LASTWEEK__">
      <b id="weekLbl" style="min-width:42px"></b>
    </div>
    <div id="map"></div>
  </div>
  <div id="panel">
    <div class="kpis">
      <div class="kpi"><b id="kCrit" style="color:#ef4444">0</b><span>CRITICAL</span></div>
      <div class="kpi"><b id="kWatch" style="color:#f59e0b">0</b><span>WATCH</span></div>
      <div class="kpi"><b id="kAnimal">0</b><span>ANIMAL DEATHS</span></div>
      <div class="kpi"><b id="kHuman">0</b><span>HUMAN FEVER</span></div>
    </div>

    <div class="card">
      <h3 id="dName" style="margin: 0 0 6px 0; color: #38bdf8;"></h3>
      <div id="dStatus" style="font-size: 12px; color: #94a3b8;"></div>
      <div id="dScore" style="font-size: 32px; font-weight: bold; margin: 8px 0 2px;">--</div>
      <div id="dMeta" style="font-size: 12px; color: #94a3b8;"></div>
      <svg id="spark" viewBox="0 0 360 90" width="100%" style="margin-top:8px"></svg>
      <div class="note">Blue: risk score &middot; Purple dashed: human fever (scaled). Dot = selected week.</div>
    </div>

    <div class="card">
      <h4>TOP DRIVERS (FEATURE CONTRIBUTION)</h4>
      <div id="dFactors"></div>
      <div class="note">Share of each indicator in the score. Not causal evidence.</div>
    </div>

    <div class="card">
      <h4 style="color:#f59e0b">ACTIONABLE VETERINARY PROTOCOL</h4>
      <p id="dAction" style="font-size: 12px; color: #cbd5e1; margin: 0;"></p>
    </div>

    <div class="card">
      <h4>CORRIDOR EXPOSURE (downstream of CRITICAL districts)</h4>
      <div id="exposure" style="font-size:12px; color:#e2e8f0; line-height:1.6"></div>
    </div>

    <div class="card">
      <h4>HUMAN&ndash;ANIMAL LAG FUSION (demo series)</h4>
      <div id="lagBox"></div>
      <div class="note">Correlation of vet distress (t&minus;lag) with human fever (t), pooled across districts. Computed on simulated data built with a 2-week lag, so it validates the pipeline, not the biology.</div>
    </div>

    <div class="card">
      <h4>DISTRICT RANKING &mdash; <span id="rankWk"></span></h4>
      <table id="rank"></table>
    </div>

    <div class="card legend">
      <span><i class="dot" style="background:#ef4444"></i>Critical &ge; 70</span>
      <span><i class="dot" style="background:#f59e0b"></i>Watch 40&ndash;69</span>
      <span><i class="dot" style="background:#10b981"></i>Normal &lt; 40</span>
      <div class="note">Prototype decision-support tool. Scores are relative indicators, not calibrated probabilities or diagnoses. Weights and thresholds need veterinary-expert calibration.</div>
    </div>
  </div>
</div>

<script>
const P = __DATA__;
const D = P.districts;
const byId = Object.fromEntries(D.map(d => [d.id, d]));
const LAST = P.weeks.length - 1;
let wk = LAST, selected = null, playing = null;

const colorFor = s => s >= 70 ? '#ef4444' : s >= 40 ? '#f59e0b' : '#10b981';
const statusFor = s => s >= 70 ? 'CRITICAL' : s >= 40 ? 'WATCH' : 'NORMAL';
const actionFor = st => st === 'CRITICAL'
  ? 'Deploy Veterinary Rapid Response, verify reports and consider targeted 5 km ring vaccination per disease protocol.'
  : st === 'WATCH' ? 'Increase syndromic surveillance, verify animal reports, review vaccination gaps.'
  : 'Routine syndromic monitoring.';

const map = L.map('map').setView([22.5937, 76.9629], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 18 }).addTo(map);

const markers = {}, buffers = {}, corridors = [];
let heat = null;
const grp = { markers: L.layerGroup().addTo(map), buf: L.layerGroup(), cor: L.layerGroup().addTo(map) };

D.forEach(d => {
  markers[d.id] = L.circleMarker([d.lat, d.lon], { radius: 10, weight: 1.5, color: '#fff', fillOpacity: 0.9 })
    .on('click', () => select(d.id)).addTo(grp.markers);
  buffers[d.id] = L.circle([d.lat, d.lon], { radius: 5000, weight: 1, fillOpacity: 0.25 }).addTo(grp.buf);
});
P.corridors.forEach(c => {
  const a = byId[c.from], b = byId[c.to];
  const line = L.polyline([[a.lat, a.lon], [b.lat, b.lon]], { weight: 2.5, dashArray: '8 6', className: 'flow', opacity: 0.85 }).addTo(grp.cor);
  corridors.push({ c, line });
});

function render() {
  document.getElementById('weekLbl').innerText = P.weeks[wk];
  document.getElementById('rankWk').innerText = P.weeks[wk];
  let crit = 0, watch = 0, animal = 0, human = 0;
  const pts = [];
  D.forEach(d => {
    const s = d.scores[wk], col = colorFor(s);
    markers[d.id].setStyle({ fillColor: col });
    markers[d.id].unbindTooltip().bindTooltip(d.name + ' (' + s + ')');
    buffers[d.id].setStyle({ color: col, fillColor: col });
    if (s >= 70) crit++; else if (s >= 40) watch++;
    animal += d.deaths[wk]; human += d.human[wk];
    pts.push([d.lat, d.lon, Math.max(0.05, s / 100)]);
  });
  document.getElementById('kCrit').innerText = crit;
  document.getElementById('kWatch').innerText = watch;
  document.getElementById('kAnimal').innerText = animal;
  document.getElementById('kHuman').innerText = human;

  if (L.heatLayer) {
    if (heat) map.removeLayer(heat);
    heat = L.heatLayer(pts, { radius: 55, blur: 40, minOpacity: 0.3,
      gradient: { 0.3: '#10b981', 0.55: '#f59e0b', 0.8: '#ef4444' } });
    if (document.getElementById('lHeat').checked) heat.addTo(map);
  }

  const exposed = [];
  corridors.forEach(({ c, line }) => {
    const a = byId[c.from], b = byId[c.to];
    const sa = a.scores[wk], sb = b.scores[wk];
    line.setStyle({ color: colorFor(Math.max(sa, sb)) });
    line.unbindTooltip().bindTooltip(c.name + ': ' + a.name + ' \u2194 ' + b.name);
    if (sa >= 70 && sb < 70) exposed.push(a.name + ' \u2192 ' + b.name + ' (' + c.name + ')');
    if (sb >= 70 && sa < 70) exposed.push(b.name + ' \u2192 ' + a.name + ' (' + c.name + ')');
  });
  document.getElementById('exposure').innerHTML = exposed.length
    ? exposed.map(e => '&bull; ' + e).join('<br>') : 'No exposed downstream districts this week.';

  const rows = D.slice().sort((x, y) => y.scores[wk] - x.scores[wk]).map(d => {
    const s = d.scores[wk], st = statusFor(s), delta = s - d.scores[Math.max(0, wk - 2)];
    const arrow = delta >= 8 ? ' <span style="color:#ef4444">&#9650; rising</span>' : '';
    return '<tr class="row' + (selected === d.id ? ' sel' : '') + '" onclick="select(\'' + d.id + '\')"><td>' + d.name +
      arrow + '</td><td><b style="color:' + colorFor(s) + '">' + s + '</b></td><td><span class="pill" style="background:' +
      colorFor(s) + '">' + st + '</span></td></tr>';
  }).join('');
  document.getElementById('rank').innerHTML = '<tr><th>District</th><th>Score</th><th>Status</th></tr>' + rows;

  if (!selected) selected = D.slice().sort((x, y) => y.scores[LAST] - x.scores[LAST])[0].id;
  showDistrict(byId[selected]);
}

function select(id) { selected = id; render(); const d = byId[id]; map.panTo([d.lat, d.lon]); }

function showDistrict(d) {
  const s = d.scores[wk], st = statusFor(s);
  document.getElementById('dName').innerText = d.name + ', ' + d.state;
  document.getElementById('dStatus').innerText = 'Status: ' + st + ' | Deaths: ' + d.deaths[wk] + ', Abortions: ' + d.abortions[wk];
  const sc = document.getElementById('dScore'); sc.innerText = s + ' / 100'; sc.style.color = colorFor(s);
  document.getElementById('dMeta').innerText = 'Human fever cases: ' + d.human[wk] +
    ' | Vaccination coverage: ' + Math.round(d.vax_cov * 100) + '% | ML anomaly flag (latest wk): ' + (d.ml_anomaly ? 'YES' : 'no');
  const order = d.shares[wk].map((v, i) => [v, i]).sort((a, b) => b[0] - a[0]);
  document.getElementById('dFactors').innerHTML = order.map(([v, i]) =>
    '<div style="font-size:12px">' + P.factorNames[i] + ' &mdash; ' + v + '%</div><div class="bar"><i style="width:' + v +
    '%; background:#38bdf8"></i></div>').join('');
  document.getElementById('dAction').innerText = actionFor(st);

  const W = 360, H = 90, n = d.scores.length, hmax = Math.max(1, ...d.human);
  const x = i => 10 + i * (W - 20) / (n - 1);
  const ys = v => H - 8 - (v / 100) * (H - 16);
  const yh = v => H - 8 - (v / hmax) * (H - 16);
  const l1 = d.scores.map((v, i) => x(i) + ',' + ys(v)).join(' ');
  const l2 = d.human.map((v, i) => x(i) + ',' + yh(v)).join(' ');
  document.getElementById('spark').innerHTML =
    '<line x1="10" x2="350" y1="' + ys(70) + '" y2="' + ys(70) + '" stroke="#ef4444" stroke-dasharray="3 4" opacity=".5"/>' +
    '<polyline fill="none" stroke="#38bdf8" stroke-width="2" points="' + l1 + '"/>' +
    '<polyline fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="4 3" points="' + l2 + '"/>' +
    '<circle cx="' + x(wk) + '" cy="' + ys(d.scores[wk]) + '" r="4" fill="' + colorFor(s) + '" stroke="#fff"/>';
}

function lagBox() {
  const mx = Math.max(0.01, ...P.lag.stats.map(s => Math.abs(s.r)));
  document.getElementById('lagBox').innerHTML = P.lag.stats.map(s =>
    '<div style="font-size:12px">Lag ' + s.lag + ' wk &mdash; r = ' + s.r + (s.lag === P.lag.best ? ' &#9733; strongest' : '') +
    '</div><div class="bar"><i style="width:' + Math.max(0, s.r) / mx * 100 + '%; background:' +
    (s.lag === P.lag.best ? '#a78bfa' : '#475569') + '"></i></div>').join('');
}

function exportCSV() {
  const head = ['district', 'state', 'week', 'risk_score', 'status', 'deaths', 'abortions', 'human_fever'];
  const rows = [head.join(',')];
  D.forEach(d => d.scores.forEach((s, i) => rows.push([d.name, d.state, P.weeks[i], s, statusFor(s),
    d.deaths[i], d.abortions[i], d.human[i]].join(','))));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([rows.join('\n')], { type: 'text/csv' }));
  a.download = 'spillover_radar_scores.csv'; a.click();
}

function togglePlay() {
  const b = document.getElementById('playBtn');
  if (playing) { clearInterval(playing); playing = null; b.innerHTML = '&#9654; Play'; return; }
  b.innerHTML = '&#10074;&#10074; Pause'; wk = 0;
  playing = setInterval(() => {
    document.getElementById('week').value = wk; render();
    if (wk >= LAST) { clearInterval(playing); playing = null; b.innerHTML = '&#9654; Play'; return; }
    wk++;
  }, 900);
}

document.getElementById('week').addEventListener('input', e => { wk = +e.target.value; render(); });
const toggle = (id, layer) => document.getElementById(id).addEventListener('change', e => {
  if (e.target.checked) layer().addTo(map); else map.removeLayer(layer()); });
toggle('lMarkers', () => grp.markers); toggle('lBuf', () => grp.buf); toggle('lCor', () => grp.cor);
document.getElementById('lHeat').addEventListener('change', e => {
  if (!heat) return; if (e.target.checked) heat.addTo(map); else map.removeLayer(heat); });

lagBox(); render();
</script>
</body>
</html>"""

html_content = (HTML_TEMPLATE
                .replace("__DATA__", json.dumps(payload))
                .replace("__LASTWEEK__", str(WEEKS - 1)))
with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)
os.makedirs(os.path.join(BASE_DIR, "api"), exist_ok=True)
with open(os.path.join(BASE_DIR, "api", "districts.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# --------------------------------------------------------------------------
# 4. TERMINAL REPORT + LOCAL WEB SERVER
# --------------------------------------------------------------------------
def status_of(s):
    return "CRITICAL" if s >= 70 else "WATCH" if s >= 40 else "NORMAL"

print("\n[D.02] Data pipeline & [D.03] ML anomaly scoring finished successfully.")
print(f"{'District':<11}{'State':<16}{'Now':>6}{'Δ2wk':>7}  {'Status':<9}{'ML':<4}Top driver")
for d in sorted(districts_out, key=lambda x: -x["scores"][-1]):
    s = d["scores"][-1]; delta = s - d["scores"][-3]
    top = FACTOR_NAMES[int(np.argmax(d["shares"][-1]))]
    print(f"{d['name']:<11}{d['state']:<16}{s:>6}{delta:>+7.1f}  {status_of(s):<9}"
          f"{'YES' if d['ml_anomaly'] else '-':<4}{top}")
print(f"\nLag fusion: strongest human-fever correlation at lag {best_lag['lag']} wk (r={best_lag['r']}); "
      f"demo series was built with a {HUMAN_LAG_WEEKS}-wk lag.")
print("[D.01] Wrote index.html and api/districts.json")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):
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
