import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# Palette (사용자 지정)
# -------------------------------------------------
PRIMARY = "#D70454"    # 강조
SECONDARY = "#AA0055"  # 보조 강조
DARK = "#980046"       # 텍스트/라인(진한 포인트)
LIGHT = "#F4D1DF"      # 배경/하이라이트

# -------------------------------------------------
# Page config & CSS (palette applied)
# -------------------------------------------------
st.set_page_config(page_title="월별 매출 대시보드", layout="wide")

st.markdown(
    f"""
    <style>
      :root {{
        --primary: {PRIMARY};
        --secondary: {SECONDARY};
        --dark: {DARK};
        --light: {LIGHT};
      }}
      html, body, .block-container {{
        background: var(--light) !important;
        color: var(--dark) !important;
      }}
      h1, h2, h3, h4, h5, h6 {{ color: var(--dark) !important; }}
      /* KPI metric cards */
      div[data-testid="stMetric"] {{
        background: #ffffffdd;
        border: 2px solid var(--secondary);
        border-radius: 14px;
        padding: 12px 14px;
      }}
      div[data-testid="stMetric"] span {{ color: var(--dark) !important; }}
      /* Buttons */
      .stDownloadButton button {{
        background: var(--primary) !important; border: 0; color: white !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 월별 매출 대시보드")

uploaded_file = st.file_uploader("CSV 업로드 (열: 월, 매출액, 전년동월, 증감률)", type=["csv"])

# -------------------------------------------------
# Sample data (동일 열명)
# -------------------------------------------------
sample_data = pd.DataFrame({
    "월": ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06","2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
    "매출액": [12000000,13500000,11000000,18000000,21000000,16500000,17500000,19000000,20000000,22000000,25000000,28000000],
    "전년동월": [10500000,11200000,12800000,15200000,18500000,15000000,16000000,16800000,17200000,19000000,21000000,23500000],
    "증감률": [14.3,20.5,-14.1,18.4,13.5,10.0,9.4,13.1,16.3,15.8,19.0,19.1]
})

# -------------------------------------------------
# Load data
# -------------------------------------------------
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="cp949")
else:
    df = sample_data.copy()

# -------------------------------------------------
# KPIs
# -------------------------------------------------
try:
    total_sales = df["매출액"].sum()
    avg_growth = df["증감률"].mean()
    max_row = df.loc[df["매출액"].idxmax()]
    min_row = df.loc[df["매출액"].idxmin()]
except Exception as e:
    st.error(f"데이터 열을 확인해주세요: {e}")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("총 매출", f"{total_sales:,.0f} 원")
k2.metric("평균 증감률", f"{avg_growth:.2f}%")
k3.metric("최대 매출", f"{max_row['매출액']:,.0f} 원", max_row['월'])
k4.metric("최소 매출", f"{min_row['매출액']:,.0f} 원", min_row['월'])

# -------------------------------------------------
# Plotly common layout/colors
# -------------------------------------------------
BASE_LAYOUT = dict(
    margin=dict(t=30, r=10, b=40, l=50),
    paper_bgcolor=LIGHT,
    plot_bgcolor=LIGHT,
    font=dict(color=DARK),
    legend=dict(orientation="h"),
)

# -------------------------------------------------
# Charts
# -------------------------------------------------
# Line: sales vs last-year
fig1 = px.line(
    df, x="월", y=["매출액", "전년동월"], markers=True,
    title="월별 매출 추이 (전년 동월 대비)",
    color_discrete_sequence=[PRIMARY, DARK]
)
fig1.update_layout(**BASE_LAYOUT)

# Bar: growth rate (continuous color scale using palette)
custom_scale = [(0.0, DARK), (0.5, LIGHT), (1.0, PRIMARY)]
fig2 = px.bar(
    df, x="월", y="증감률", title="증감률(%)",
    color="증감률", color_continuous_scale=custom_scale
)
fig2.update_layout(**BASE_LAYOUT)

# Area: cumulative sales
df_cum = df.copy()
df_cum["누적매출"] = df_cum["매출액"].cumsum()
fig3 = go.Figure(
    go.Scatter(x=df_cum["월"], y=df_cum["누적매출"], mode="lines",
               fill="tozeroy", name="누적 매출",
               line=dict(color=SECONDARY))
)
fig3.update_layout(title_text="누적 매출 추이", **BASE_LAYOUT)

# Grouped bars: current vs last year
fig4 = go.Figure()
fig4.add_bar(x=df["월"], y=df["매출액"], name="매출액", marker_color=PRIMARY)
fig4.add_bar(x=df["월"], y=df["전년동월"], name="전년동월", marker_color=DARK)
fig4.update_layout(barmode="group", title_text="전년 동월 대비 비교", **BASE_LAYOUT)

# Render
st.plotly_chart(fig1, use_container_width=True)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)

st.caption("ⓘ 팁: CSV는 열 이름을 반드시 '월, 매출액, 전년동월, 증감률'로 맞춰 주세요.")
