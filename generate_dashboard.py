import pandas as pd
import json
from datetime import datetime

INPUT_FILE = r"C:\Users\RERE\Downloads\NLP ASSIGNMENT\Hasil_Analisis_PerfectCrown.xlsx"
OUTPUT_FILE = r"C:\Users\RERE\Downloads\NLP ASSIGNMENT\PerfectCrown_Dashboard.html"

df = pd.read_excel(INPUT_FILE)
df["Published Date"] = pd.to_datetime(df["Published Date"], errors="coerce")

total_berita = len(df)
sentimen_counts = df["Sentimen"].value_counts().to_dict()
positive = sentimen_counts.get("positive", 0)
negative = sentimen_counts.get("negative", 0)
neutral = sentimen_counts.get("neutral", 0)
total_entitas = df["Tokoh"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip().nunique() + \
                df["Lembaga"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip().nunique() + \
                df["Tempat"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip().nunique()

pos_pct = round(positive / total_berita * 100, 1) if total_berita else 0
neg_pct = round(negative / total_berita * 100, 1) if total_berita else 0
neu_pct = round(neutral / total_berita * 100, 1) if total_berita else 0

topik_sentimen = df.groupby(["Topik", "Sentimen"]).size().unstack(fill_value=0)
topik_sentimen_data = {}
for topik in topik_sentimen.index:
    row = topik_sentimen.loc[topik]
    topik_sentimen_data[topik] = {
        "positive": int(row.get("positive", 0)),
        "negative": int(row.get("negative", 0)),
        "neutral": int(row.get("neutral", 0)),
    }

topik_counts = df["Topik"].value_counts().to_dict()

tokoh_all = df["Tokoh"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip()
tokoh_counts = tokoh_all.value_counts().head(10).to_dict()

lembaga_all = df["Lembaga"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip()
lembaga_counts = lembaga_all.value_counts().head(10).to_dict()

tempat_all = df["Tempat"].dropna().replace("-", "").replace("", pd.NA).dropna().str.split(",").explode().str.strip()
tempat_counts = tempat_all.value_counts().head(10).to_dict()

publisher_counts = df["Publisher"].value_counts().head(8).to_dict()
author_counts = df["Author"].value_counts().head(8).to_dict()

date_range = ""
if df["Published Date"].notna().any():
    min_date = df["Published Date"].min().strftime("%d %b %Y")
    max_date = df["Published Date"].max().strftime("%d %b %Y")
    date_range = f"{min_date} - {max_date}"

articles_json = df.fillna("").to_dict(orient="records")
for a in articles_json:
    if isinstance(a.get("Published Date"), pd.Timestamp):
        a["Published Date"] = a["Published Date"].strftime("%d %b %Y")

data_json = json.dumps({
    "total_berita": total_berita,
    "positive": positive,
    "negative": negative,
    "neutral": neutral,
    "total_entitas": total_entitas,
    "pos_pct": pos_pct,
    "neg_pct": neg_pct,
    "neu_pct": neu_pct,
    "topik_sentimen": topik_sentimen_data,
    "topik_counts": topik_counts,
    "tokoh_counts": tokoh_counts,
    "lembaga_counts": lembaga_counts,
    "tempat_counts": tempat_counts,
    "publisher_counts": publisher_counts,
    "author_counts": author_counts,
    "date_range": date_range,
    "articles": articles_json,
})

html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Perfect Crown — Sentiment Dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  :root {{
    --gold: #C9A84C;
    --gold-light: #E8D48B;
    --gold-dark: #A07C1C;
    --bg: #0A0A0A;
    --bg-card: #111111;
    --bg-card-hover: #1A1A1A;
    --border: rgba(201,168,76,0.15);
    --border-hover: rgba(201,168,76,0.35);
    --text: #F5F5F5;
    --text-muted: #888888;
    --positive: #C9A84C;
    --negative: #8B3A3A;
    --neutral: #555555;
    --radius: 12px;
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
  }}

  * {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    min-height: 100vh;
  }}

  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 20px; }}

  /* HEADER */
  header {{
    text-align: center;
    padding: 48px 20px 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 40px;
  }}
  header .crown-icon {{ font-size: 48px; margin-bottom: 8px; display: block; }}
  header h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(28px, 5vw, 42px);
    font-weight: 700;
    letter-spacing: 2px;
    background: linear-gradient(135deg, var(--gold-light), var(--gold), var(--gold-dark));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  header p {{
    color: var(--text-muted);
    font-size: 14px;
    margin-top: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
  }}
  header .date-range {{
    color: var(--gold);
    font-size: 13px;
    margin-top: 12px;
    font-weight: 500;
  }}

  /* KPI CARDS */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
  }}
  .kpi-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }}
  .kpi-card:hover {{ border-color: var(--border-hover); transform: translateY(-2px); box-shadow: var(--shadow); }}
  .kpi-card:hover::before {{ opacity: 1; }}
  .kpi-card .kpi-value {{
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: var(--gold);
  }}
  .kpi-card .kpi-label {{
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 8px;
  }}

  /* SECTION */
  .section {{
    margin-bottom: 40px;
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInUp 0.6s ease forwards;
  }}
  .section:nth-child(2) {{ animation-delay: 0.1s; }}
  .section:nth-child(3) {{ animation-delay: 0.2s; }}
  .section:nth-child(4) {{ animation-delay: 0.3s; }}
  .section:nth-child(5) {{ animation-delay: 0.4s; }}

  @keyframes fadeInUp {{
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-left: 16px;
    border-left: 3px solid var(--gold);
    color: var(--text);
  }}

  /* INSIGHT BOX */
  .insight-box {{
    background: linear-gradient(135deg, rgba(201,168,76,0.08), rgba(201,168,76,0.02));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    position: relative;
  }}
  .insight-box::before {{
    content: '\\2726';
    position: absolute;
    top: -12px; left: 20px;
    background: var(--bg);
    padding: 0 8px;
    color: var(--gold);
    font-size: 20px;
  }}
  .insight-box h3 {{
    font-family: 'Playfair Display', serif;
    color: var(--gold);
    font-size: 16px;
    margin-bottom: 12px;
  }}
  .insight-box p {{
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.8;
  }}
  .insight-box strong {{ color: var(--gold-light); }}

  /* SENTIMENT PILLS */
  .pills-container {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .pill {{
    flex: 1;
    min-width: 200px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    transition: all 0.3s ease;
  }}
  .pill:hover {{ border-color: var(--border-hover); }}
  .pill-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .pill-label {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
  }}
  .pill-value {{
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
  }}
  .pill-bar {{
    height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 3px;
    overflow: hidden;
  }}
  .pill-bar-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 1.2s ease;
    width: 0;
  }}
  .pill.positive .pill-label {{ color: var(--positive); }}
  .pill.positive .pill-value {{ color: var(--positive); }}
  .pill.positive .pill-bar-fill {{ background: var(--positive); }}
  .pill.negative .pill-label {{ color: var(--negative); }}
  .pill.negative .pill-value {{ color: var(--negative); }}
  .pill.negative .pill-bar-fill {{ background: var(--negative); }}
  .pill.neutral .pill-label {{ color: var(--neutral); }}
  .pill.neutral .pill-value {{ color: var(--neutral); }}
  .pill.neutral .pill-bar-fill {{ background: var(--neutral); }}

  /* CHARTS GRID */
  .charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 20px;
  }}
  .chart-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    transition: all 0.3s ease;
  }}
  .chart-card:hover {{ border-color: var(--border-hover); }}
  .chart-card h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    margin-bottom: 20px;
    color: var(--gold);
  }}

  /* DONUT */
  .donut-wrapper {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 32px;
    flex-wrap: wrap;
  }}
  .donut-svg {{ width: 180px; height: 180px; }}
  .donut-legend {{ display: flex; flex-direction: column; gap: 12px; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 13px; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}

  /* STACKED BAR */
  .stacked-bar {{ display: flex; flex-direction: column; gap: 16px; }}
  .stacked-row {{ display: flex; align-items: center; gap: 12px; }}
  .stacked-label {{ width: 140px; font-size: 12px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .stacked-track {{ flex: 1; height: 28px; background: rgba(255,255,255,0.03); border-radius: 6px; overflow: hidden; display: flex; }}
  .stacked-seg {{
    height: 100%;
    transition: width 1s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    min-width: 0;
  }}
  .stacked-seg.pos {{ background: var(--positive); }}
  .stacked-seg.neg {{ background: var(--negative); }}
  .stacked-seg.neu {{ background: var(--neutral); }}

  /* HORIZONTAL BAR */
  .hbar {{ display: flex; flex-direction: column; gap: 12px; }}
  .hbar-row {{ display: flex; align-items: center; gap: 12px; }}
  .hbar-label {{ width: 140px; font-size: 12px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .hbar-track {{ flex: 1; height: 24px; background: rgba(255,255,255,0.03); border-radius: 4px; overflow: hidden; }}
  .hbar-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--gold-dark), var(--gold));
    border-radius: 4px;
    transition: width 1s ease;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 11px;
    font-weight: 600;
    color: #000;
  }}

  /* TOPICS LIST */
  .topics-list {{ display: flex; flex-direction: column; gap: 16px; }}
  .topic-item {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: rgba(255,255,255,0.02);
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.3s ease;
  }}
  .topic-item:hover {{ border-color: var(--border); background: rgba(201,168,76,0.04); }}
  .topic-rank {{
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--gold);
    width: 36px;
    text-align: center;
  }}
  .topic-info {{ flex: 1; }}
  .topic-name {{ font-size: 14px; font-weight: 500; margin-bottom: 6px; }}
  .topic-progress {{ height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden; }}
  .topic-progress-fill {{ height: 100%; background: var(--gold); border-radius: 2px; transition: width 1s ease; width: 0; }}
  .topic-count {{ font-size: 13px; color: var(--gold); font-weight: 600; }}

  /* PUBLISHERS / AUTHORS */
  .entity-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
  }}
  .entity-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }}
  .entity-card h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    margin-bottom: 16px;
    color: var(--gold);
  }}
  .entity-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .entity-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }}
  .entity-row:last-child {{ border-bottom: none; }}
  .avatar {{
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--gold-dark), var(--gold));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    color: #000;
    flex-shrink: 0;
  }}
  .entity-name {{ font-size: 13px; flex: 1; }}
  .entity-count {{ font-size: 12px; color: var(--gold); font-weight: 600; }}

  /* NER TAG CLOUD */
  .ner-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }}
  .ner-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }}
  .ner-card h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    margin-bottom: 16px;
    color: var(--gold);
  }}
  .tag-cloud {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .tag {{
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid var(--border);
    background: rgba(201,168,76,0.06);
    color: var(--text-muted);
    transition: all 0.3s ease;
  }}
  .tag:hover {{ border-color: var(--gold); color: var(--gold); background: rgba(201,168,76,0.12); }}
  .tag .tag-count {{ color: var(--gold); font-weight: 700; margin-left: 4px; }}

  /* TABLE */
  .table-wrapper {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }}
  .table-controls {{
    display: flex;
    gap: 12px;
    padding: 20px;
    flex-wrap: wrap;
    align-items: center;
    border-bottom: 1px solid var(--border);
  }}
  .search-input {{
    flex: 1;
    min-width: 200px;
    padding: 10px 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 13px;
    outline: none;
    transition: border-color 0.3s ease;
  }}
  .search-input:focus {{ border-color: var(--gold); }}
  .search-input::placeholder {{ color: var(--text-muted); }}
  .filter-btn {{
    padding: 8px 16px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-muted);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .filter-btn:hover, .filter-btn.active {{ border-color: var(--gold); color: var(--gold); background: rgba(201,168,76,0.08); }}
  .table-scroll {{ overflow-x: auto; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  th {{
    padding: 14px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--gold);
    background: rgba(201,168,76,0.06);
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}
  td {{
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    color: var(--text-muted);
    vertical-align: top;
  }}
  tr:hover td {{ background: rgba(201,168,76,0.03); }}
  .sentiment-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: capitalize;
  }}
  .sentiment-badge.positive {{ background: rgba(201,168,76,0.15); color: var(--positive); }}
  .sentiment-badge.negative {{ background: rgba(139,58,58,0.2); color: #C46B6B; }}
  .sentiment-badge.neutral {{ background: rgba(85,85,85,0.2); color: #999; }}
  .table-footer {{
    padding: 14px 20px;
    font-size: 12px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    text-align: right;
  }}

  /* FOOTER */
  footer {{
    text-align: center;
    padding: 32px 20px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
    color: var(--text-muted);
    font-size: 12px;
    letter-spacing: 1px;
  }}
  footer span {{ color: var(--gold); }}

  /* RESPONSIVE */
  @media (max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .charts-grid {{ grid-template-columns: 1fr; }}
    .stacked-label, .hbar-label {{ width: 100px; font-size: 11px; }}
    .donut-wrapper {{ flex-direction: column; }}
    header {{ padding: 32px 16px 24px; }}
  }}
  @media (max-width: 480px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <span class="crown-icon">&#9813;</span>
  <h1>PERFECT CROWN</h1>
  <p>Sentiment Analysis Dashboard</p>
  <div class="date-range" id="dateRange"></div>
</header>

<div class="container">

  <!-- KPI CARDS -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-value" id="kpiTotal">0</div>
      <div class="kpi-label">Total Berita</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" id="kpiPositive">0</div>
      <div class="kpi-label">Positive</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" id="kpiNegative">0</div>
      <div class="kpi-label">Negative</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" id="kpiNeutral">0</div>
      <div class="kpi-label">Neutral</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" id="kpiEntities">0</div>
      <div class="kpi-label">Total Entitas</div>
    </div>
  </div>

  <!-- KEY INSIGHT -->
  <div class="section">
    <div class="insight-box">
      <h3>Key Insights</h3>
      <p id="insightText"></p>
    </div>
  </div>

  <!-- SENTIMENT PILLS -->
  <div class="section" style="margin-top:40px;">
    <h2 class="section-title">Sentiment Distribution</h2>
    <div class="pills-container">
      <div class="pill positive">
        <div class="pill-header">
          <span class="pill-label">Positive</span>
          <span class="pill-value" id="pillPosPct">0%</span>
        </div>
        <div class="pill-bar"><div class="pill-bar-fill" id="pillPosBar"></div></div>
      </div>
      <div class="pill negative">
        <div class="pill-header">
          <span class="pill-label">Negative</span>
          <span class="pill-value" id="pillNegPct">0%</span>
        </div>
        <div class="pill-bar"><div class="pill-bar-fill" id="pillNegBar"></div></div>
      </div>
      <div class="pill neutral">
        <div class="pill-header">
          <span class="pill-label">Neutral</span>
          <span class="pill-value" id="pillNeuPct">0%</span>
        </div>
        <div class="pill-bar"><div class="pill-bar-fill" id="pillNeuBar"></div></div>
      </div>
    </div>
  </div>

  <!-- CHARTS -->
  <div class="section" style="margin-top:40px;">
    <h2 class="section-title">Visual Analytics</h2>
    <div class="charts-grid">

      <!-- DONUT -->
      <div class="chart-card">
        <h3>Sentiment Overview</h3>
        <div class="donut-wrapper">
          <svg class="donut-svg" viewBox="0 0 42 42" id="donutChart"></svg>
          <div class="donut-legend" id="donutLegend"></div>
        </div>
      </div>

      <!-- STACKED BAR -->
      <div class="chart-card">
        <h3>Sentiment per Topik</h3>
        <div class="stacked-bar" id="stackedBar"></div>
      </div>

      <!-- HORIZONTAL BAR -->
      <div class="chart-card">
        <h3>Artikel per Topik</h3>
        <div class="hbar" id="hbarChart"></div>
      </div>

      <!-- TOP TOPICS -->
      <div class="chart-card">
        <h3>Top Topics Ranking</h3>
        <div class="topics-list" id="topicsList"></div>
      </div>

    </div>
  </div>

  <!-- PUBLISHERS & AUTHORS -->
  <div class="section" style="margin-top:40px;">
    <h2 class="section-title">Publishers & Authors</h2>
    <div class="entity-grid">
      <div class="entity-card">
        <h3>Top Publishers</h3>
        <div class="entity-list" id="publisherList"></div>
      </div>
      <div class="entity-card">
        <h3>Top Authors</h3>
        <div class="entity-list" id="authorList"></div>
      </div>
    </div>
  </div>

  <!-- NER -->
  <div class="section" style="margin-top:40px;">
    <h2 class="section-title">Named Entity Recognition</h2>
    <div class="ner-grid">
      <div class="ner-card">
        <h3>Tokoh</h3>
        <div class="tag-cloud" id="tokohCloud"></div>
      </div>
      <div class="ner-card">
        <h3>Lembaga</h3>
        <div class="tag-cloud" id="lembagaCloud"></div>
      </div>
      <div class="ner-card">
        <h3>Tempat</h3>
        <div class="tag-cloud" id="tempatCloud"></div>
      </div>
    </div>
  </div>

  <!-- TABLE -->
  <div class="section" style="margin-top:40px;">
    <h2 class="section-title">Article Database</h2>
    <div class="table-wrapper">
      <div class="table-controls">
        <input type="text" class="search-input" id="searchInput" placeholder="Search judul, author, publisher...">
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="positive">Positive</button>
        <button class="filter-btn" data-filter="negative">Negative</button>
        <button class="filter-btn" data-filter="neutral">Neutral</button>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>No</th>
              <th>Judul Artikel</th>
              <th>Publisher</th>
              <th>Author</th>
              <th>Published</th>
              <th>Topik</th>
              <th>Sentimen</th>
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
      <div class="table-footer" id="tableFooter"></div>
    </div>
  </div>

</div>

<footer>
  <span>&#9813;</span> Perfect Crown Sentiment Dashboard &mdash; Generated <span id="genDate"></span>
</footer>

<script>
const DATA = {data_json};

function animateValue(el, end, duration=1200) {{
  let start = 0;
  const step = end / (duration / 16);
  const timer = setInterval(() => {{
    start += step;
    if (start >= end) {{ start = end; clearInterval(timer); }}
    el.textContent = Math.round(start);
  }}, 16);
}}

function init() {{
  // Date range
  document.getElementById('dateRange').textContent = DATA.date_range ? '\\uD83D\\uDCC5 ' + DATA.date_range : '';

  // KPI
  animateValue(document.getElementById('kpiTotal'), DATA.total_berita);
  animateValue(document.getElementById('kpiPositive'), DATA.positive);
  animateValue(document.getElementById('kpiNegative'), DATA.negative);
  animateValue(document.getElementById('kpiNeutral'), DATA.neutral);
  animateValue(document.getElementById('kpiEntities'), DATA.total_entitas);

  // Insight
  const dominantSentiment = DATA.positive >= DATA.negative && DATA.positive >= DATA.neutral ? 'Positive' :
                            DATA.negative >= DATA.positive && DATA.negative >= DATA.neutral ? 'Negative' : 'Neutral';
  const topTopic = Object.entries(DATA.topik_counts).sort((a,b) => b[1]-a[1])[0];
  const topTokoh = Object.entries(DATA.tokoh_counts).sort((a,b) => b[1]-a[1])[0];
  document.getElementById('insightText').innerHTML =
    `Dari <strong>${{DATA.total_berita}} artikel</strong> yang dianalisis, sentimen dominan adalah <strong>${{dominantSentiment}}</strong> ` +
    `(${{DATA.pos_pct}}%). Topik paling banyak dibahas adalah <strong>${{topTopic ? topTopic[0] : '-'}}</strong> ` +
    `dengan ${{topTopic ? topTopic[1] : 0}} artikel. Tokoh yang paling sering disebutkan adalah <strong>${{topTokoh ? topTokoh[0] : '-'}}</strong>. ` +
    `Total ditemukan <strong>${{DATA.total_entitas}} entitas unik</strong> (tokoh, lembaga, dan tempat).`;

  // Pills
  document.getElementById('pillPosPct').textContent = DATA.pos_pct + '%';
  document.getElementById('pillNegPct').textContent = DATA.neg_pct + '%';
  document.getElementById('pillNeuPct').textContent = DATA.neu_pct + '%';
  setTimeout(() => {{
    document.getElementById('pillPosBar').style.width = DATA.pos_pct + '%';
    document.getElementById('pillNegBar').style.width = DATA.neg_pct + '%';
    document.getElementById('pillNeuBar').style.width = DATA.neu_pct + '%';
  }}, 300);

  // Donut
  const total = DATA.positive + DATA.negative + DATA.neutral || 1;
  const posR = DATA.positive / total * 100;
  const negR = DATA.negative / total * 100;
  const neuR = DATA.neutral / total * 100;
  const posDash = posR;
  const negDash = negR;
  const neuDash = neuR;
  const posOffset = 0;
  const negOffset = -posR;
  const neuOffset = -(posR + negR);

  document.getElementById('donutChart').innerHTML = `
    <circle cx="21" cy="21" r="15.915" fill="none" stroke="var(--positive)" stroke-width="4"
      stroke-dasharray="${{posDash}} ${{100-posDash}}" stroke-dashoffset="${{posOffset}}"
      style="transition: all 1s ease;"/>
    <circle cx="21" cy="21" r="15.915" fill="none" stroke="var(--negative)" stroke-width="4"
      stroke-dasharray="${{negDash}} ${{100-negDash}}" stroke-dashoffset="${{negOffset}}"
      style="transition: all 1s ease;"/>
    <circle cx="21" cy="21" r="15.915" fill="none" stroke="var(--neutral)" stroke-width="4"
      stroke-dasharray="${{neuDash}} ${{100-neuDash}}" stroke-dashoffset="${{neuOffset}}"
      style="transition: all 1s ease;"/>
    <text x="21" y="20" text-anchor="middle" fill="var(--gold)" font-size="5" font-weight="700" font-family="Playfair Display">${{total}}</text>
    <text x="21" y="25" text-anchor="middle" fill="var(--text-muted)" font-size="2.5" font-family="Inter">articles</text>
  `;
  document.getElementById('donutLegend').innerHTML = `
    <div class="legend-item"><div class="legend-dot" style="background:var(--positive)"></div>Positive (${{DATA.positive}})</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--negative)"></div>Negative (${{DATA.negative}})</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--neutral)"></div>Neutral (${{DATA.neutral}})</div>
  `;

  // Stacked Bar
  const stackedEl = document.getElementById('stackedBar');
  for (const [topik, counts] of Object.entries(DATA.topik_sentimen)) {{
    const t = counts.positive + counts.negative + counts.neutral || 1;
    stackedEl.innerHTML += `
      <div class="stacked-row">
        <div class="stacked-label">${{topik}}</div>
        <div class="stacked-track">
          <div class="stacked-seg pos" style="width:${{counts.positive/t*100}}%">${{counts.positive > 0 ? counts.positive : ''}}</div>
          <div class="stacked-seg neg" style="width:${{counts.negative/t*100}}%">${{counts.negative > 0 ? counts.negative : ''}}</div>
          <div class="stacked-seg neu" style="width:${{counts.neutral/t*100}}%">${{counts.neutral > 0 ? counts.neutral : ''}}</div>
        </div>
      </div>
    `;
  }}

  // Horizontal Bar
  const hbarEl = document.getElementById('hbarChart');
  const maxCount = Math.max(...Object.values(DATA.topik_counts), 1);
  for (const [topik, count] of Object.entries(DATA.topik_counts).sort((a,b) => b[1]-a[1])) {{
    hbarEl.innerHTML += `
      <div class="hbar-row">
        <div class="hbar-label">${{topik}}</div>
        <div class="hbar-track">
          <div class="hbar-fill" style="width:${{count/maxCount*100}}%">${{count}}</div>
        </div>
      </div>
    `;
  }}

  // Topics List
  const topicsEl = document.getElementById('topicsList');
  const sortedTopics = Object.entries(DATA.topik_counts).sort((a,b) => b[1]-a[1]);
  sortedTopics.forEach(([topik, count], i) => {{
    const pct = count / sortedTopics[0][1] * 100;
    topicsEl.innerHTML += `
      <div class="topic-item">
        <div class="topic-rank">${{i+1}}</div>
        <div class="topic-info">
          <div class="topic-name">${{topik}}</div>
          <div class="topic-progress"><div class="topic-progress-fill" data-width="${{pct}}"></div></div>
        </div>
        <div class="topic-count">${{count}}</div>
      </div>
    `;
  }});
  setTimeout(() => {{
    document.querySelectorAll('.topic-progress-fill').forEach(el => {{
      el.style.width = el.dataset.width + '%';
    }});
  }}, 500);

  // Publishers
  const pubEl = document.getElementById('publisherList');
  for (const [name, count] of Object.entries(DATA.publisher_counts)) {{
    const initials = name.substring(0, 2).toUpperCase();
    pubEl.innerHTML += `
      <div class="entity-row">
        <div class="avatar">${{initials}}</div>
        <div class="entity-name">${{name}}</div>
        <div class="entity-count">${{count}}</div>
      </div>
    `;
  }}

  // Authors
  const authEl = document.getElementById('authorList');
  for (const [name, count] of Object.entries(DATA.author_counts)) {{
    const initials = name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
    authEl.innerHTML += `
      <div class="entity-row">
        <div class="avatar">${{initials}}</div>
        <div class="entity-name">${{name}}</div>
        <div class="entity-count">${{count}}</div>
      </div>
    `;
  }}

  // NER Tags
  function renderTags(containerId, data) {{
    const el = document.getElementById(containerId);
    const sorted = Object.entries(data).sort((a,b) => b[1]-a[1]);
    if (sorted.length === 0) {{
      el.innerHTML = '<span style="color:var(--text-muted);font-size:12px;">No data</span>';
      return;
    }}
    sorted.forEach(([name, count]) => {{
      el.innerHTML += `<span class="tag">${{name}}<span class="tag-count">${{count}}</span></span>`;
    }});
  }}
  renderTags('tokohCloud', DATA.tokoh_counts);
  renderTags('lembagaCloud', DATA.lembaga_counts);
  renderTags('tempatCloud', DATA.tempat_counts);

  // Table
  const tbody = document.getElementById('tableBody');
  const footer = document.getElementById('tableFooter');
  let currentFilter = 'all';
  let searchQuery = '';

  function renderTable() {{
    let filtered = DATA.articles.filter(a => {{
      const matchFilter = currentFilter === 'all' || a.Sentimen === currentFilter;
      const q = searchQuery.toLowerCase();
      const matchSearch = !q ||
        (a['Judul Artikel'] && a['Judul Artikel'].toLowerCase().includes(q)) ||
        (a.Author && a.Author.toLowerCase().includes(q)) ||
        (a.Publisher && a.Publisher.toLowerCase().includes(q)) ||
        (a.Topik && a.Topik.toLowerCase().includes(q));
      return matchFilter && matchSearch;
    }});
    tbody.innerHTML = '';
    filtered.forEach(a => {{
      const badgeClass = a.Sentimen || 'neutral';
      tbody.innerHTML += `
        <tr>
          <td>${{a.No}}</td>
          <td><a href="${{a['Link Berita']}}" target="_blank" style="color:var(--gold-light);text-decoration:none;">${{a['Judul Artikel']}}</a></td>
          <td>${{a.Publisher}}</td>
          <td>${{a.Author}}</td>
          <td>${{a['Published Date']}}</td>
          <td>${{a.Topik}}</td>
          <td><span class="sentiment-badge ${{badgeClass}}">${{a.Sentimen}}</span></td>
        </tr>
      `;
    }});
    footer.textContent = `Showing ${{filtered.length}} of ${{DATA.articles.length}} articles`;
  }}

  document.getElementById('searchInput').addEventListener('input', e => {{
    searchQuery = e.target.value;
    renderTable();
  }});

  document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderTable();
    }});
  }});

  renderTable();

  // Gen date
  document.getElementById('genDate').textContent = new Date().toLocaleDateString('id-ID', {{ day:'numeric', month:'long', year:'numeric' }});
}}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard saved to: {OUTPUT_FILE}")
