import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config — must be first
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Allstate Claims Severity",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
.stApp {
    background-color: #080c14;
    color: #c9d1d9;
}
section[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #1e2433;
}
section[data-testid="stSidebar"] * {
    color: #8b949e !important;
}
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}
.kpi {
    background: #0d1117;
    border: 1px solid #1e2433;
    border-radius: 6px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi.blue::before   { background: #388bfd; }
.kpi.green::before  { background: #3fb950; }
.kpi.amber::before  { background: #d29922; }
.kpi.red::before    { background: #f85149; }
.kpi.purple::before { background: #8957e5; }
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: #484f58;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: #e6edf3;
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: #484f58;
    margin-top: 6px;
    font-family: 'IBM Plex Sans', sans-serif;
}
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: #484f58;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border-bottom: 1px solid #1e2433;
    padding-bottom: 10px;
    margin: 28px 0 18px 0;
}
.page-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px;
    font-weight: 600;
    color: #e6edf3;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}
.page-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    color: #484f58;
    margin-bottom: 24px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stCheckbox"] svg {
    color: #f85149 !important;
    fill: #f85149 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading 125,546 claims...")
def load_data():
    url = "https://raw.githubusercontent.com/hernon33/allstate-claims-dashboard/main/test_predictions_full.csv"
    df = pd.read_csv(url)
    df["high_severity_flag"] = df["high_severity_flag"].astype(bool)
    df["severity_tier"] = pd.Categorical(
        df["severity_tier"],
        categories=["Low", "Moderate", "High", "Extreme"],
        ordered=True,
    )
    return df

df = load_data()

TIER_COLORS = {
    "Low":      "#3fb950",
    "Moderate": "#388bfd",
    "High":     "#d29922",
    "Extreme":  "#f85149",
}
HIGH_SEV_THRESHOLD = 6401.74

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="font-family: IBM Plex Mono, monospace; font-size: 16px; '
        'font-weight: 600; color: #e6edf3; margin-bottom: 2px;">🛡️ Allstate</div>'
        '<div style="font-family: IBM Plex Sans, sans-serif; font-size: 11px; '
        'color: #484f58; margin-bottom: 24px;">Claims Severity Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Severity Tier**")
    selected_tier = st.selectbox("Tier", ["All", "Low", "Moderate", "High", "Extreme"], label_visibility="collapsed")

    st.markdown("<br>**High Severity Flag**", unsafe_allow_html=True)
    flag_filter = st.radio("Flag", ["All Claims", "Flagged Only", "Not Flagged"], label_visibility="collapsed")

    st.markdown("<br>**Loss Range ($)**", unsafe_allow_html=True)
    loss_range = st.slider(
        "Loss",
        min_value=0.0,
        max_value=float(df["predicted_loss"].max()),
        value=(0.0, float(df["predicted_loss"].max())),
        label_visibility="collapsed",
    )

    st.markdown("<br>**Search Claim ID**", unsafe_allow_html=True)
    search_id = st.text_input("ID", placeholder="e.g. 4, 9, 12...", label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        '<div style="font-size: 10px; color: #484f58; font-family: IBM Plex Mono, monospace; line-height: 1.8;">'
        'DATA 6545 · Spring 2026<br>Connor Hernon<br><br>'
        '<a href="https://github.com/hernon33/allstate-severity-api" style="color: #388bfd; text-decoration: none;">API Repo ↗</a><br>'
        '<a href="https://allstate-severity-api.onrender.com/health" style="color: #388bfd; text-decoration: none;">Live API ↗</a><br>'
        '<a href="https://github.com/hernon33/allstate-claims-dashboard" style="color: #388bfd; text-decoration: none;">Dashboard Repo ↗</a>'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------
filtered = df.copy()
if selected_tier != "All":
    filtered = filtered[filtered["severity_tier"] == selected_tier]
if flag_filter == "Flagged Only":
    filtered = filtered[filtered["high_severity_flag"]]
elif flag_filter == "Not Flagged":
    filtered = filtered[~filtered["high_severity_flag"]]
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
st.markdown(
    '<div class="page-title">Insurance Claims Severity Explorer</div>'
    '<div class="page-sub">LightGBM dual-model predictions · 125,546 test claims · '
    'Allstate Claims Severity Dataset · MAE $1,135 · AUC-ROC 0.9315</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi blue">
    <div class="kpi-label">Total Claims</div>
    <div class="kpi-value">{len(df):,}</div>
    <div class="kpi-sub">full test set</div>
  </div>
  <div class="kpi green">
    <div class="kpi-label">Avg Predicted Loss</div>
    <div class="kpi-value">${df['predicted_loss'].mean():,.0f}</div>
    <div class="kpi-sub">per claim</div>
  </div>
  <div class="kpi amber">
    <div class="kpi-label">High Severity</div>
    <div class="kpi-value">{df['high_severity_flag'].mean()*100:.1f}%</div>
    <div class="kpi-sub">of all claims flagged</div>
  </div>
  <div class="kpi red">
    <div class="kpi-label">Extreme Claims</div>
    <div class="kpi-value">{(df['severity_tier']=='Extreme').sum():,}</div>
    <div class="kpi-sub">> $6,401 predicted</div>
  </div>
  <div class="kpi purple">
    <div class="kpi-label">Showing</div>
    <div class="kpi-value">{len(filtered):,}</div>
    <div class="kpi-sub">after filters</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Distribution Analysis</div>', unsafe_allow_html=True)

CHART_LAYOUT = dict(
    plot_bgcolor="#0d1117",
    paper_bgcolor="#080c14",
    font=dict(family="IBM Plex Mono", color="#8b949e", size=11),
    title_font=dict(size=13, color="#c9d1d9"),
    margin=dict(t=44, b=20, l=10, r=10),
    xaxis=dict(gridcolor="#1e2433", linecolor="#1e2433", zeroline=False),
    yaxis=dict(gridcolor="#1e2433", linecolor="#1e2433", zeroline=False),
    showlegend=False,
)

col1, col2 = st.columns(2)

with col1:
    tier_counts = df["severity_tier"].value_counts().reindex(["Low", "Moderate", "High", "Extreme"])
    fig1 = go.Figure(go.Bar(
        x=tier_counts.index.tolist(),
        y=tier_counts.values,
        marker_color=[TIER_COLORS[t] for t in tier_counts.index],
        marker_line_width=0,
    ))
    fig1.update_layout(title="Claims by Severity Tier", **CHART_LAYOUT)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    bins   = [0, 500, 1000, 2000, 3000, 5000, 6402, 10000, df["predicted_loss"].max() + 1]
    labels = ["<$500","$500–1K","$1K–2K","$2K–3K","$3K–5K","$5K–6.4K","$6.4K–10K",">$10K"]
    counts = pd.cut(df["predicted_loss"], bins=bins, labels=labels).value_counts().reindex(labels)
    fig2 = go.Figure(go.Bar(
        x=labels, y=counts.values,
        marker_color="#388bfd",
        marker_line_width=0,
    ))
    fig2.update_layout(title="Predicted Loss Distribution", **CHART_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

fig3 = go.Figure(go.Histogram(
    x=df["high_severity_probability"],
    nbinsx=60,
    marker_color="#d29922",
    marker_line_width=0,
))
fig3.update_layout(
    title="High-Severity Probability Distribution  ·  AUC-ROC 0.9315  ·  Youden's J threshold = 0.0746",
    height=220,
    **{**CHART_LAYOUT, "margin": dict(t=44, b=20, l=10, r=10)},
)
fig3.update_xaxes(title_text="Classifier Probability")
fig3.update_yaxes(title_text="Claims")
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------------------------------
# Claims table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Claims Explorer</div>', unsafe_allow_html=True)

PAGE_SIZE = 25
total_pages = max(1, int(np.ceil(len(filtered) / PAGE_SIZE)))

pcol1, pcol2 = st.columns([1, 5])
with pcol1:
    page = st.number_input(
        "Page", min_value=1, max_value=total_pages,
        value=1, step=1, label_visibility="collapsed",
    )
with pcol2:
    st.markdown(
        f'<div style="font-family: IBM Plex Mono, monospace; font-size: 11px; '
        f'color: #484f58; padding-top: 10px;">'
        f'Page {int(page)} of {total_pages} · {len(filtered):,} claims matching filters</div>',
        unsafe_allow_html=True,
    )

start   = (int(page) - 1) * PAGE_SIZE
page_df = filtered.iloc[start: start + PAGE_SIZE].copy()
page_df["severity_tier"] = page_df["severity_tier"].astype(str)

st.dataframe(
    page_df[["id", "predicted_loss", "high_severity_probability", "high_severity_flag", "severity_tier"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "id": st.column_config.NumberColumn("Claim ID", format="%d"),
        "predicted_loss": st.column_config.NumberColumn(
            "Predicted Loss",
            format="$%,.2f",
            help="Predicted dollar loss from LightGBM regressor",
        ),
        "high_severity_probability": st.column_config.ProgressColumn(
    "High Severity Probability",
    format="%.1f%%",
    min_value=0.0,
    max_value=1.0,
    help="Classifier probability of falling in top 10% of losses",
        ),
        "high_severity_flag": st.column_config.CheckboxColumn(
            "Flagged",
            help="True if predicted loss >= $6,401.74",
        ),
        "severity_tier": st.column_config.TextColumn(
            "Severity Tier",
        ),
    },
    height=650,
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div style="font-family: IBM Plex Mono, monospace; font-size: 10px; '
    'color: #1e2433; text-align: center; margin-top: 40px; padding-bottom: 20px;">'
    'DATA 6545 · Spring 2026 · Connor Hernon · '
    'LightGBM Regressor + Classifier · 188,318 training claims · '
    'github.com/hernon33/allstate-severity-api'
    '</div>',
    unsafe_allow_html=True,
)
