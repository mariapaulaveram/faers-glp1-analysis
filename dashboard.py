"""
dashboard.py
FAERS Adverse Event Analysis — GLP-1 Agonists
Genera el dashboard HTML interactivo con ECharts.

Author: María Paula Vera Morandini
ICH-GCP E6(R3) | ANMAT 7516/25
"""

import pandas as pd
import json
from datetime import datetime

with open("faers_kpis.json") as f:
    kpis = json.load(f)

top_reactions = pd.read_csv("faers_top_reactions.csv")
by_drug       = pd.read_csv("faers_reactions_by_drug.csv")
sex_dist      = pd.read_csv("faers_sex_dist.csv")
outcome_dist  = pd.read_csv("faers_outcome_dist.csv")
yearly        = pd.read_csv("faers_yearly.csv")
age_dist      = pd.read_csv("faers_age_dist.csv")
serious_df    = pd.read_csv("faers_serious.csv")

drugs = sorted(by_drug["drug"].unique().tolist())
drug_colors = {
    "Semaglutide": "#0891B2",
    "Liraglutide": "#7C3AED",
    "Dulaglutide": "#047857",
    "Exenatide":   "#B45309",
}

# Heatmap: top 10 reacciones x droga
top10 = top_reactions["reaction"].head(10).tolist()
heatmap_data = []
for drug in drugs:
    drug_data = by_drug[by_drug["drug"] == drug].set_index("reaction")["count"]
    for i, rxn in enumerate(top10):
        heatmap_data.append([drugs.index(drug), i, int(drug_data.get(rxn, 0))])

top_reactions_json = top_reactions.to_json(orient="records")
by_drug_json       = by_drug.to_json(orient="records")
sex_dist_json      = sex_dist.to_json(orient="records")
outcome_dist_json  = outcome_dist.to_json(orient="records")
yearly_json        = yearly.to_json(orient="records")
age_dist_json      = age_dist.to_json(orient="records")
serious_json       = serious_df.fillna("—").to_json(orient="records")
drugs_json         = json.dumps(drugs)
drug_colors_json   = json.dumps(drug_colors)
heatmap_json       = json.dumps(heatmap_data)
top10_json         = json.dumps(top10)

generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FAERS GLP-1 Adverse Event Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#FFFFFF; --surface:#FAFAFA; --surface2:#F3F4F6;
    --border:#E5E7EB; --border2:#D1D5DB;
    --text:#111827; --text2:#6B7280; --text3:#9CA3AF;
    --cyan:#0891B2; --cyan-lt:#ECFEFF; --cyan-dk:#164E63;
    --red:#BE123C; --red-lt:#FFF1F2; --red-dk:#7F1D1D;
    --amber:#B45309; --amber-lt:#FFFBEB; --amber-dk:#78350F;
    --green:#047857; --green-lt:#ECFDF5; --green-dk:#064E3B;
    --purple:#7C3AED; --purple-lt:#F5F3FF;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); }}

  .topbar {{
    background:var(--cyan-dk); padding:0 2rem;
    display:flex; align-items:center; gap:1rem;
    height:52px; position:sticky; top:0; z-index:100;
  }}
  .topbar-icon {{ width:28px; height:28px; background:rgba(255,255,255,0.15); border-radius:6px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
  .topbar-title {{ font-size:14px; font-weight:600; color:white; letter-spacing:0.01em; }}
  .topbar-right {{ margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:10px; color:rgba(255,255,255,0.45); }}
  .pill {{ font-family:'JetBrains Mono',monospace; font-size:10px; padding:2px 8px; border-radius:3px; background:rgba(255,255,255,0.12); color:rgba(255,255,255,0.85); letter-spacing:0.05em; }}
  .pill-red {{ background:rgba(190,18,60,0.35); color:#FCA5A5; }}

  .page {{ max-width:1300px; margin:0 auto; padding:2rem 1.5rem 4rem; }}

  .disclaimer {{ border-left:3px solid var(--amber); background:var(--amber-lt); padding:10px 14px; font-size:12px; color:var(--amber-dk); margin-bottom:1.5rem; line-height:1.6; }}

  .filter-bar {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom:1.5rem; padding:12px 0; border-bottom:1px solid var(--border); }}
  .filter-bar label {{ font-size:11px; font-weight:600; color:var(--text3); text-transform:uppercase; letter-spacing:0.08em; }}
  .filter-bar select {{ font-family:'Inter',sans-serif; font-size:13px; color:var(--text); background:var(--surface2); border:1px solid var(--border2); border-radius:6px; padding:6px 24px 6px 10px; appearance:none; cursor:pointer; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E"); background-repeat:no-repeat; background-position:right 7px center; }}
  .filter-bar select:focus {{ outline:none; border-color:var(--cyan); }}
  .filter-sep {{ width:1px; height:20px; background:var(--border); }}
  .filter-reset {{ font-size:12px; color:var(--text3); background:none; border:none; cursor:pointer; padding:4px 8px; border-radius:4px; font-family:'Inter',sans-serif; }}
  .filter-reset:hover {{ color:var(--cyan); }}
  #recCount {{ margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--cyan-dk); background:var(--cyan-lt); border-left:3px solid var(--cyan); padding:3px 10px; }}

  .kpi-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:1px; margin-bottom:2rem; background:var(--border); border:1px solid var(--border); }}
  @media(max-width:900px){{ .kpi-grid {{ grid-template-columns:repeat(3,1fr); }} }}
  .kpi-card {{ background:var(--bg); padding:1.25rem 1.25rem 1rem; border-left:3px solid transparent; transition:background 0.15s; }}
  .kpi-card:hover {{ background:var(--surface); }}
  .kpi-card.c-cyan {{ border-left-color:var(--cyan); }}
  .kpi-card.c-red {{ border-left-color:var(--red); }}
  .kpi-card.c-amber {{ border-left-color:var(--amber); }}
  .kpi-card.c-purple {{ border-left-color:var(--purple); }}
  .kpi-card.c-green {{ border-left-color:var(--green); }}
  .kpi-label {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:var(--text3); margin-bottom:10px; }}
  .kpi-value {{ font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:700; line-height:1; margin-bottom:4px; }}
  .kpi-card.c-cyan .kpi-value {{ color:var(--cyan); }}
  .kpi-card.c-red .kpi-value {{ color:var(--red); }}
  .kpi-card.c-amber .kpi-value {{ color:var(--amber); }}
  .kpi-card.c-purple .kpi-value {{ color:var(--purple); }}
  .kpi-card.c-green .kpi-value {{ color:var(--green); }}
  .kpi-sub {{ font-size:11px; color:var(--text3); }}

  .section-header {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:var(--cyan-dk); margin:2rem 0 1rem; padding-bottom:8px; border-bottom:2px solid var(--cyan); display:inline-block; }}

  .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:1px; margin-bottom:1px; background:var(--border); }}
  .grid-3 {{ display:grid; grid-template-columns:2fr 1fr; gap:1px; margin-bottom:1px; background:var(--border); }}
  .grid-full {{ margin-bottom:1px; }}
  @media(max-width:760px){{ .grid-2,.grid-3 {{ grid-template-columns:1fr; }} }}

  .card {{ background:var(--bg); padding:1.5rem; border:1px solid var(--border); }}
  .card-title {{ font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:var(--text2); margin-bottom:16px; display:flex; align-items:center; gap:8px; }}
  .card-title .bar {{ width:3px; height:14px; border-radius:2px; flex-shrink:0; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:12px; margin-bottom:12px; }}
  .legend-item {{ display:flex; align-items:center; gap:5px; font-size:11px; color:var(--text2); }}
  .legend-dot {{ width:8px; height:8px; border-radius:1px; flex-shrink:0; }}
  .inline-select {{ font-family:'Inter',sans-serif; font-size:12px; color:var(--text); background:var(--surface2); border:1px solid var(--border2); border-radius:4px; padding:4px 20px 4px 8px; appearance:none; cursor:pointer; margin-bottom:12px; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E"); background-repeat:no-repeat; background-position:right 6px center; }}

  .table-wrap {{ overflow-x:auto; }}
  table.dt {{ width:100%; border-collapse:collapse; font-size:12px; }}
  table.dt thead th {{ font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text3); padding:8px 14px; text-align:left; border-bottom:2px solid var(--border); background:var(--surface); white-space:nowrap; }}
  table.dt tbody td {{ padding:9px 14px; border-bottom:1px solid var(--border); color:var(--text); white-space:nowrap; }}
  table.dt tbody tr:last-child td {{ border-bottom:none; }}
  table.dt tbody tr:hover td {{ background:var(--cyan-lt); }}
  .mono {{ font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text2); }}
  .tag {{ display:inline-block; font-size:10px; font-weight:700; padding:2px 8px; letter-spacing:0.05em; border-left:2px solid; }}
  .tag-fatal {{ border-color:var(--red); background:var(--red-lt); color:var(--red-dk); }}
  .tag-notrecov {{ border-color:var(--amber); background:var(--amber-lt); color:var(--amber-dk); }}
  .dpill {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700; padding:2px 8px; color:white; }}

  .footer {{ text-align:center; padding:2rem 0 1rem; font-size:12px; color:var(--text3); border-top:2px solid var(--border); margin-top:3rem; }}
  .footer a {{ color:var(--cyan); text-decoration:none; }}
  .footer a:hover {{ text-decoration:underline; }}
  .empty {{ text-align:center; padding:2rem; color:var(--text3); font-size:12px; }}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-icon">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path d="M3 12h4l3-8 4 16 3-9 2 1h2" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
  <span class="topbar-title">FAERS Adverse Event Analysis — GLP-1 Agonists</span>
  <span class="pill pill-red">PHARMACOVIGILANCE</span>
  <span class="pill">openFDA · FAERS</span>
  <span class="pill">REAL DATA</span>
  <span class="topbar-right">Generated: {generated_at}</span>
</header>

<main class="page">
  <div class="disclaimer">
    <strong>⚠ Disclaimer:</strong> This analysis uses publicly available data from the FDA Adverse Event Reporting System (FAERS) via openFDA. Reports are submitted voluntarily and may contain duplicates or incomplete information. For educational and portfolio purposes only. Not medical or regulatory advice.
  </div>

  <div class="filter-bar">
    <label>Drug</label>
    <select id="selDrug">
      <option value="all">All GLP-1 Agonists</option>
      <option value="Semaglutide">Semaglutide (Ozempic)</option>
      <option value="Liraglutide">Liraglutide (Victoza)</option>
      <option value="Dulaglutide">Dulaglutide (Trulicity)</option>
      <option value="Exenatide">Exenatide (Byetta)</option>
    </select>
    <div class="filter-sep"></div>
    <label>Outcome</label>
    <select id="selOutcome">
      <option value="all">All outcomes</option>
      <option value="Fatal">Fatal</option>
      <option value="Not recovered">Not recovered</option>
      <option value="Recovered">Recovered</option>
      <option value="Recovering">Recovering</option>
      <option value="Unknown">Unknown</option>
    </select>
    <div class="filter-sep"></div>
    <label>Sex</label>
    <select id="selSex">
      <option value="all">All</option>
      <option value="Female">Female</option>
      <option value="Male">Male</option>
    </select>
    <button class="filter-reset" id="btnReset">↺ Reset</button>
    <span id="recCount">— records</span>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card c-cyan"><div class="kpi-label">Total Reports</div><div class="kpi-value">{kpis["total_reports"]:,}</div><div class="kpi-sub">adverse event reports</div></div>
    <div class="kpi-card c-red"><div class="kpi-label">Serious Events</div><div class="kpi-value">{kpis["serious_pct"]}%</div><div class="kpi-sub">of total reports</div></div>
    <div class="kpi-card c-amber"><div class="kpi-label">Fatal Outcomes</div><div class="kpi-value">{kpis["fatal_pct"]}%</div><div class="kpi-sub">of total reports</div></div>
    <div class="kpi-card c-purple"><div class="kpi-label">Unique Reactions</div><div class="kpi-value">{kpis["total_reactions"]:,}</div><div class="kpi-sub">MedDRA terms</div></div>
    <div class="kpi-card c-green"><div class="kpi-label">Drugs Analyzed</div><div class="kpi-value">{kpis["drugs"]}</div><div class="kpi-sub">GLP-1 agonists</div></div>
  </div>

  <div class="section-header">Adverse Reactions Overview</div>
  <div class="grid-3">
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--red)"></span>Top 15 Adverse Reactions (MedDRA)</div>
      <div id="chartReactions" style="height:320px"></div>
    </div>
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--purple)"></span>Outcome Distribution</div>
      <div id="chartOutcome" style="height:320px"></div>
    </div>
  </div>

  <div class="section-header">Heatmap — Reaction × Drug</div>
  <div class="grid-full">
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--cyan)"></span>Top 10 Reactions × Drug — Frequency Heatmap</div>
      <div id="chartHeatmap" style="height:280px"></div>
    </div>
  </div>

  <div class="section-header">Drug Comparison</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--cyan)"></span>Reports by Year</div>
      <div id="chartYearly" style="height:240px"></div>
    </div>
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--green)"></span>Sex Distribution by Drug</div>
      <div id="chartSex" style="height:240px"></div>
    </div>
  </div>

  <div class="section-header">Age &amp; Reaction Profile</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--amber)"></span>Reports by Age Group</div>
      <div id="chartAge" style="height:230px"></div>
    </div>
    <div class="card">
      <div class="card-title"><span class="bar" style="background:var(--purple)"></span>Top Reactions by Drug</div>
      <select class="inline-select" id="selDrugReactions">
        <option value="Semaglutide">Semaglutide</option>
        <option value="Liraglutide">Liraglutide</option>
        <option value="Dulaglutide">Dulaglutide</option>
        <option value="Exenatide">Exenatide</option>
      </select>
      <div id="chartDrugReactions" style="height:195px"></div>
    </div>
  </div>

  <div class="section-header">Serious &amp; Fatal Reports</div>
  <div class="card">
    <div class="card-title"><span class="bar" style="background:var(--red)"></span>Fatal or Not Recovered — Sample</div>
    <div class="table-wrap">
      <table class="dt">
        <thead><tr><th>Drug</th><th>Reaction (MedDRA)</th><th>Outcome</th><th>Sex</th><th>Age</th><th>Country</th><th>Year</th></tr></thead>
        <tbody id="seriousTable"></tbody>
      </table>
    </div>
  </div>
</main>

<footer class="footer">
  <strong>María Paula Vera Morandini</strong> &nbsp;·&nbsp; Biochemist | Study Coordinator &amp; QA | Clinical Data Management<br>
  ICH-GCP E6(R3) Certified &nbsp;·&nbsp; ANMAT 7516/25 &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/maria-paula-vera-morandini-43b284399" target="_blank">LinkedIn</a> &nbsp;·&nbsp; Buenos Aires, Argentina<br><br>
  Data source: FDA Adverse Event Reporting System (FAERS) via openFDA public API · GLP-1 Agonists Pharmacovigilance Analysis
</footer>

<script>
const TOP_REACTIONS = {top_reactions_json};
const BY_DRUG       = {by_drug_json};
const SEX_DIST      = {sex_dist_json};
const OUTCOME_DIST  = {outcome_dist_json};
const YEARLY        = {yearly_json};
const AGE_DIST      = {age_dist_json};
const SERIOUS       = {serious_json};
const DRUGS         = {drugs_json};
const DRUG_COLORS   = {drug_colors_json};
const HEATMAP       = {heatmap_json};
const TOP10         = {top10_json};

const OUTCOME_COLORS = {{
  "Recovered":"#047857","Recovering":"#0891B2",
  "Not recovered":"#B45309","Fatal":"#BE123C","Unknown":"#9CA3AF",
}};

const FONT = 'Inter';
const TEXT2 = '#6B7280';
const TEXT3 = '#9CA3AF';
const GRID  = '#F3F4F6';

// ECharts instances
const ec = {{}};
function initCharts() {{
  ['chartReactions','chartOutcome','chartHeatmap','chartYearly',
   'chartSex','chartAge','chartDrugReactions'].forEach(id => {{
    ec[id] = echarts.init(document.getElementById(id));
  }});
  window.addEventListener('resize', () => Object.values(ec).forEach(c => c.resize()));
}}

function render() {{
  const drug    = document.getElementById('selDrug').value;
  const outcome = document.getElementById('selOutcome').value;
  const sex     = document.getElementById('selSex').value;
  const drugsToShow = drug === 'all' ? DRUGS : [drug];

  let serious = SERIOUS.filter(r =>
    (drug==='all'||r.drug===drug) &&
    (outcome==='all'||r.outcome===outcome) &&
    (sex==='all'||r.sex===sex)
  );
  document.getElementById('recCount').textContent = serious.length + ' records';

  // ── Chart 1: Top reactions — horizontal bar ──────────────────────────────
  const rxData = drug==='all' ? TOP_REACTIONS : BY_DRUG.filter(r=>r.drug===drug).slice(0,15);
  ec.chartReactions.setOption({{
    tooltip:{{ trigger:'axis', axisPointer:{{type:'shadow'}}, textStyle:{{fontFamily:FONT,fontSize:12}} }},
    grid:{{ left:150, right:40, top:10, bottom:20 }},
    xAxis:{{ type:'value', splitLine:{{lineStyle:{{color:GRID}}}}, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT3}} }},
    yAxis:{{ type:'category', data:rxData.map(r=>r.reaction).reverse(),
      axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT2}},
      axisLine:{{show:false}}, axisTick:{{show:false}} }},
    series:[{{ type:'bar', data:rxData.map(r=>r.count).reverse(),
      itemStyle:{{color:'#BE123C',borderRadius:[0,3,3,0]}},
      barMaxWidth:16,
      label:{{show:true,position:'right',fontFamily:FONT,fontSize:10,color:TEXT2}}
    }}]
  }}, true);

  // ── Chart 2: Outcome — pie with emphasis ─────────────────────────────────
  const outcomeMap = {{}};
  OUTCOME_DIST.filter(r=>drug==='all'||r.drug===drug)
    .forEach(r=>{{ outcomeMap[r.outcome]=(outcomeMap[r.outcome]||0)+r.count; }});
  const pieData = Object.entries(outcomeMap).map(([name,value])=>{{
    return {{ name, value, itemStyle:{{color:OUTCOME_COLORS[name]||'#9CA3AF'}} }};
  }});
  ec.chartOutcome.setOption({{
    tooltip:{{ trigger:'item', formatter:'{{b}}: {{c}} ({{d}}%)', textStyle:{{fontFamily:FONT,fontSize:12}} }},
    legend:{{ bottom:0, textStyle:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, itemWidth:10, itemHeight:10 }},
    series:[{{ type:'pie', radius:['45%','72%'], center:['50%','45%'],
      data:pieData,
      label:{{show:false}},
      emphasis:{{ itemStyle:{{shadowBlur:10,shadowColor:'rgba(0,0,0,0.15)'}}, label:{{show:true,fontFamily:FONT,fontSize:12,formatter:'{{b}}\\n{{d}}%'}} }}
    }}]
  }}, true);

  // ── Chart 3: Heatmap ─────────────────────────────────────────────────────
  const heatFiltered = drug==='all' ? HEATMAP :
    HEATMAP.filter(d=>d[0]===DRUGS.indexOf(drug));
  const drugsForHeat = drug==='all' ? DRUGS : [drug];
  const maxVal = Math.max(...heatFiltered.map(d=>d[2]));
  ec.chartHeatmap.setOption({{
    tooltip:{{ formatter:p=>`${{drugsForHeat[p.data[0]]}} · ${{TOP10[p.data[1]]}}<br/>Reports: <strong>${{p.data[2]}}</strong>`, textStyle:{{fontFamily:FONT,fontSize:12}} }},
    grid:{{ left:160, right:80, top:20, bottom:60 }},
    xAxis:{{ type:'category', data:drugsForHeat, axisLabel:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, splitArea:{{show:true}} }},
    yAxis:{{ type:'category', data:TOP10, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT2}}, splitArea:{{show:true}} }},
    visualMap:{{ min:0, max:maxVal||1, calculable:true, orient:'horizontal',
      left:'right', bottom:0, textStyle:{{fontFamily:FONT,fontSize:10,color:TEXT2}},
      inRange:{{color:['#ECFEFF','#0891B2']}} }},
    series:[{{ type:'heatmap',
      data: drug==='all' ? HEATMAP : HEATMAP.filter(d=>d[0]===DRUGS.indexOf(drug)).map(d=>[0,d[1],d[2]]),
      label:{{show:true,fontFamily:FONT,fontSize:10,color:'#374151'}},
      emphasis:{{itemStyle:{{shadowBlur:6,shadowColor:'rgba(0,0,0,0.2)'}}}}
    }}]
  }}, true);

  // ── Chart 4: Yearly — smooth lines ───────────────────────────────────────
  const years = [...new Set(YEARLY.map(r=>r.year))].sort();
  ec.chartYearly.setOption({{
    tooltip:{{ trigger:'axis', textStyle:{{fontFamily:FONT,fontSize:12}} }},
    legend:{{ bottom:0, textStyle:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, itemWidth:12, itemHeight:3 }},
    grid:{{ left:40, right:20, top:10, bottom:50 }},
    xAxis:{{ type:'category', data:years.map(String), axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT2}}, axisLine:{{lineStyle:{{color:GRID}}}}, axisTick:{{show:false}} }},
    yAxis:{{ type:'value', splitLine:{{lineStyle:{{color:GRID}}}}, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT3}} }},
    series: drugsToShow.map(d=>{{
      const color = DRUG_COLORS[d];
      return {{
        name:d, type:'line', smooth:true,
        data:years.map(y=>{{ const r=YEARLY.find(r=>r.drug===d&&r.year===y); return r?r.count:0; }}),
        lineStyle:{{color,width:2}},
        itemStyle:{{color}},
        areaStyle:{{color,opacity:0.06}},
        symbol:'circle', symbolSize:6,
      }};
    }})
  }}, true);

  // ── Chart 5: Sex — grouped bar ───────────────────────────────────────────
  ec.chartSex.setOption({{
    tooltip:{{ trigger:'axis', axisPointer:{{type:'shadow'}}, textStyle:{{fontFamily:FONT,fontSize:12}} }},
    legend:{{ bottom:0, textStyle:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, itemWidth:10, itemHeight:10 }},
    grid:{{ left:40, right:20, top:10, bottom:50 }},
    xAxis:{{ type:'category', data:drugsToShow, axisLabel:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, axisTick:{{show:false}}, axisLine:{{lineStyle:{{color:GRID}}}} }},
    yAxis:{{ type:'value', splitLine:{{lineStyle:{{color:GRID}}}}, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT3}} }},
    series:[
      {{ name:'Female', type:'bar', stack:'s', barMaxWidth:32,
        data:drugsToShow.map(d=>{{ const r=SEX_DIST.find(r=>r.drug===d&&r.sex==='Female'); return r?r.count:0; }}),
        itemStyle:{{color:'#7C3AED',borderRadius:[0,0,0,0]}} }},
      {{ name:'Male', type:'bar', stack:'s', barMaxWidth:32,
        data:drugsToShow.map(d=>{{ const r=SEX_DIST.find(r=>r.drug===d&&r.sex==='Male'); return r?r.count:0; }}),
        itemStyle:{{color:'#0891B2',borderRadius:[3,3,0,0]}} }},
    ]
  }}, true);

  // ── Chart 6: Age groups ───────────────────────────────────────────────────
  const ageGroups = ["18-30","31-45","46-60","61-75","76+"];
  ec.chartAge.setOption({{
    tooltip:{{ trigger:'axis', axisPointer:{{type:'shadow'}}, textStyle:{{fontFamily:FONT,fontSize:12}} }},
    legend:{{ bottom:0, textStyle:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, itemWidth:10, itemHeight:10 }},
    grid:{{ left:40, right:20, top:10, bottom:50 }},
    xAxis:{{ type:'category', data:ageGroups, axisLabel:{{fontFamily:FONT,fontSize:11,color:TEXT2}}, axisTick:{{show:false}}, axisLine:{{lineStyle:{{color:GRID}}}} }},
    yAxis:{{ type:'value', splitLine:{{lineStyle:{{color:GRID}}}}, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT3}} }},
    series: drugsToShow.map(d=>{{
      return {{
        name:d, type:'bar', stack:'s', barMaxWidth:40,
        data:ageGroups.map(ag=>{{ const r=AGE_DIST.find(r=>r.drug===d&&r.age_group===ag); return r?r.count:0; }}),
        itemStyle:{{color:DRUG_COLORS[d]}}
      }};
    }})
  }}, true);

  // Table
  const tbody = document.getElementById('seriousTable');
  tbody.innerHTML = serious.length===0
    ? `<tr><td colspan="7" class="empty">No records match the current filters.</td></tr>`
    : serious.slice(0,20).map(r=>`<tr>
        <td><span class="dpill" style="background:${{DRUG_COLORS[r.drug]||'#888'}}">${{r.drug}}</span></td>
        <td style="color:#111827">${{r.reaction}}</td>
        <td><span class="tag ${{r.outcome==='Fatal'?'tag-fatal':'tag-notrecov'}}">${{r.outcome}}</span></td>
        <td>${{r.sex}}</td>
        <td class="mono">${{r.age!=='—'?r.age+' y':'—'}}</td>
        <td>${{r.country}}</td>
        <td class="mono">${{r.year!=='—'?r.year:'—'}}</td>
      </tr>`).join('');
}}

function renderDrugReactions() {{
  const d = document.getElementById('selDrugReactions').value;
  const data = BY_DRUG.filter(r=>r.drug===d).slice(0,10);
  ec.chartDrugReactions.setOption({{
    tooltip:{{ trigger:'axis', axisPointer:{{type:'shadow'}}, textStyle:{{fontFamily:FONT,fontSize:12}} }},
    grid:{{ left:140, right:40, top:5, bottom:15 }},
    xAxis:{{ type:'value', splitLine:{{lineStyle:{{color:GRID}}}}, axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT3}} }},
    yAxis:{{ type:'category', data:data.map(r=>r.reaction).reverse(),
      axisLabel:{{fontFamily:FONT,fontSize:10,color:TEXT2}},
      axisLine:{{show:false}}, axisTick:{{show:false}} }},
    series:[{{ type:'bar', data:data.map(r=>r.count).reverse(),
      itemStyle:{{color:DRUG_COLORS[d],borderRadius:[0,3,3,0]}},
      barMaxWidth:14,
      label:{{show:true,position:'right',fontFamily:FONT,fontSize:10,color:TEXT2}}
    }}]
  }}, true);
}}

['selDrug','selOutcome','selSex'].forEach(id=>
  document.getElementById(id).addEventListener('change', render)
);
document.getElementById('btnReset').addEventListener('click',()=>{{
  ['selDrug','selOutcome','selSex'].forEach(id=>document.getElementById(id).value='all');
  render();
}});
document.getElementById('selDrugReactions').addEventListener('change', renderDrugReactions);

initCharts();
render();
renderDrugReactions();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard generado: index.html")
print(f"   · ECharts — heatmap, pie con énfasis, líneas suaves, barras agrupadas")
