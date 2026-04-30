import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Allstate Claims Severity Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Background */
.stApp {
    background-color: #0f1117;
    color: #e8e8e8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #2a2f3e;
}

/* Metric cards */
.metric-card {
    background: #161b27;
    border: 1px solid #2a2f3e;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #e8e8e8;
    line-height: 1;
}
.metric-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 4px;
}

/* Severity badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
}
.badge-low      { background: #1a3a2a; color: #34d399; border: 1px solid #34d399; }
.badge-moderate { background: #1a2f4a; color: #60a5fa; border: 1px solid #60a5fa; }
.badge-high     { background: #3a2a1a; color: #f59e0b; border: 1px solid #f59e0b; }
.badge-extreme  { background: #3a1a1a; color: #f87171; border: 1px solid #f87171; }

/* Section headers */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border-bottom: 1px solid #2a2f3e;
    padding-bottom: 8px;
    margin-bottom: 16px;
    margin-top: 24px;
}

/* Table */
.claims-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}
.claims-table th {
    background: #1e2433;
    color: #6b7280;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid #2a2f3e;
    cursor: pointer;
}
.claims-table td {
    padding: 10px 14px;
    border-bottom: 1px solid #1e2433;
    color: #d1d5db;
}
.claims-table tr:hover td { background: #1a1f2e; }
.claims-table tr.row-extreme td { background: #1f1515; }
.claims-table tr.row-high td    { background: #1f1a10; }

/* Flag indicator */
.flag-yes { color: #f87171; font-weight: 600; }
.flag-no  { color: #4b5563; }

/* Page title */
.dashboard-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #e8e8e8;
    letter-spacing: -0.02em;
}
.dashboard-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: #6b7280;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/hernon33/allstate-claims-dashboard/main/test_predictions_full.csv"
    df = pd.read_csv(url)
    df["high_severity_flag"] = df["high_severity_flag"].astype(bool)
    return df

df = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="dashboard-title">🛡️ Allstate</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-sub">Claims Severity Dashboard</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**Filter by Severity Tier**")
    tier_options = ["All", "Low", "Moderate", "High", "Extreme"]
    selected_tier = st.selectbox("Severity Tier", tier_options, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**High Severity Flag**")
    flag_filter = st.radio(
        "Flag",
        ["All Claims", "Flagged Only", "Not Flagged"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Loss Range ($)**")
    min_loss = float(df["predicted_loss"].min())
    max_loss = float(df["predicted_loss"].max())
    loss_range = st.slider(
        "Loss Range",
        min_value=min_loss,
        max_value=max_loss,
        value=(min_loss, max_loss),
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Search by Claim ID**")
    search_id = st.text_input("Claim ID", placeholder="e.g. 4, 6, 9...", label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        '<div style="font-family: IBM Plex Mono, monospace; font-size: 10px; color: #4b5563;">'
        'DATA 6545 · Spring 2026<br>Connor Hernon<br><br>'
        '<a href="https://github.com/hernon33/allstate-severity-api" style="color: #60a5fa;">API Repo</a> · '
        '<a href="https://allstate-severity-api.onrender.com" style="color: #60a5fa;">Live API</a>'
        '</div>',
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df.copy()

if selected_tier != "All":
    filtered = filtered[filtered["severity_tier"] == selected_tier]

if flag_filter == "Flagged Only":
    filtered = filtered[filtered["high_severity_flag"] == True]
elif flag_filter == "Not Flagged":
    filtered = filtered[filtered["high_severity_flag"] == False]

filtered = filtered[
    (filtered["predicted_loss"] >= loss_range[0]) &
    (filtered["predicted_loss"] <= loss_range[1])
]

if search_id.strip():
    try:
        filtered = filtered[filtered["id"] == int(search_id.strip())]
    except ValueError:
        pass

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="dashboard-title">Insurance Claims Severity</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-sub">LightGBM predictions across 125,546 test claims — '
    'Allstate Claims Severity Dataset · DATA 6545 Spring 2026</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Claims</div>
        <div class="metric-value">{len(df):,}</div>
        <div class="metric-sub">test set</div>
    </div>""", unsafe_allow_html=True)

with c2:
    avg_loss = df["predicted_loss"].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Predicted Loss</div>
        <div class="metric-value">${avg_loss:,.0f}</div>
        <div class="metric-sub">per claim</div>
    </div>""", unsafe_allow_html=True)

with c3:
    pct_high = df["high_severity_flag"].mean() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">High Severity</div>
        <div class="metric-value">{pct_high:.1f}%</div>
        <div class="metric-sub">flagged claims</div>
    </div>""", unsafe_allow_html=True)

with c4:
    extreme_count = (df["severity_tier"] == "Extreme").sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Extreme Claims</div>
        <div class="metric-value">{extreme_count:,}</div>
        <div class="metric-sub">> $6,401 predicted</div>
    </div>""", unsafe_allow_html=True)

with c5:
    showing = len(filtered)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Showing</div>
        <div class="metric-value">{showing:,}</div>
        <div class="metric-sub">after filters</div>
    </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Distribution Analysis</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

TIER_COLORS = {
    "Low":      "#34d399",
    "Moderate": "#60a5fa",
    "High":     "#f59e0b",
    "Extreme":  "#f87171",
}

with chart_col1:
    tier_counts = df["severity_tier"].value_counts().reindex(
        ["Low", "Moderate", "High", "Extreme"]
    ).reset_index()
    tier_counts.columns = ["Tier", "Count"]

    fig1 = px.bar(
        tier_counts, x="Tier", y="Count",
        color="Tier",
        color_discrete_map=TIER_COLORS,
        title="Claims by Severity Tier",
    )
    fig1.update_layout(
        plot_bgcolor="#161b27",
        paper_bgcolor="#0f1117",
        font=dict(family="IBM Plex Mono", color="#9ca3af", size=11),
        title_font=dict(size=13, color="#e8e8e8"),
        showlegend=False,
        xaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        yaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    bins = [0, 500, 1000, 2000, 3000, 5000, 6401, 10000, df["predicted_loss"].max()]
    labels = ["<$500", "$500–1K", "$1K–2K", "$2K–3K", "$3K–5K", "$5K–6.4K", "$6.4K–10K", ">$10K"]
    df["loss_bucket"] = pd.cut(df["predicted_loss"], bins=bins, labels=labels)
    bucket_counts = df["loss_bucket"].value_counts().sort_index().reset_index()
    bucket_counts.columns = ["Range", "Count"]

    fig2 = px.bar(
        bucket_counts, x="Range", y="Count",
        title="Predicted Loss Distribution",
        color_discrete_sequence=["#60a5fa"],
    )
    fig2.update_layout(
        plot_bgcolor="#161b27",
        paper_bgcolor="#0f1117",
        font=dict(family="IBM Plex Mono", color="#9ca3af", size=11),
        title_font=dict(size=13, color="#e8e8e8"),
        showlegend=False,
        xaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        yaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Severity probability distribution
# ---------------------------------------------------------------------------
fig3 = px.histogram(
    df, x="high_severity_probability",
    nbins=50,
    title="High-Severity Probability Distribution (AUC-ROC: 0.9315)",
    color_discrete_sequence=["#f59e0b"],
)
fig3.update_layout(
    plot_bgcolor="#161b27",
    paper_bgcolor="#0f1117",
    font=dict(family="IBM Plex Mono", color="#9ca3af", size=11),
    title_font=dict(size=13, color="#e8e8e8"),
    showlegend=False,
    xaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e", title="Probability"),
    yaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e", title="Claims"),
    margin=dict(t=40, b=20, l=20, r=20),
    height=250,
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------------------------------
# Claims table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Claims Explorer</div>', unsafe_allow_html=True)

BADGE_MAP = {
    "Low":      "badge-low",
    "Moderate": "badge-moderate",
    "High":     "badge-high",
    "Extreme":  "badge-extreme",
}

# Pagination
PAGE_SIZE = 25
total_pages = max(1, int(np.ceil(len(filtered) / PAGE_SIZE)))

col_page, col_info = st.columns([2, 4])
with col_page:
    page = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, step=1,
        label_visibility="collapsed"
    )
with col_info:
    st.markdown(
        f'<div style="font-family: IBM Plex Mono, monospace; font-size: 11px; '
        f'color: #6b7280; padding-top: 8px;">'
        f'Page {page} of {total_pages} · {len(filtered):,} claims</div>',
        unsafe_allow_html=True
    )

start = (page - 1) * PAGE_SIZE
page_data = filtered.iloc[start: start + PAGE_SIZE]

rows_html = ""
for _, row in page_data.iterrows():
    tier      = row["severity_tier"]
    row_class = f"row-{tier.lower()}" if tier in ["Extreme", "High"] else ""
    badge     = f'<span class="badge {BADGE_MAP[tier]}">{tier}</span>'
    flag_html = '<span class="flag-yes">● YES</span>' if row["high_severity_flag"] else '<span class="flag-no">—</span>'

    rows_html += f"""
    <tr class="{row_class}">
        <td>{int(row['id'])}</td>
        <td>${row['predicted_loss']:,.2f}</td>
        <td>{row['high_severity_probability']:.4f}</td>
        <td>{flag_html}</td>
        <td>{badge}</td>
    </tr>"""

table_html = f"""
<table class="claims-table">
    <thead>
        <tr>
            <th>Claim ID</th>
            <th>Predicted Loss</th>
            <th>High-Sev Probability</th>
            <th>Flagged</th>
            <th>Severity Tier</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family: IBM Plex Mono, monospace; font-size: 10px; color: #374151; text-align: center;">'
    'DATA 6545 · Spring 2026 · Connor Hernon · '
    'LightGBM · MAE $1,135 · AUC-ROC 0.9315 · 188K training claims'
    '</div>',
    unsafe_allow_html=True
)
