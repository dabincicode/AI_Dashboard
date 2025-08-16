import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정과 다크 테마 CSS 적용
st.set_page_config(page_title="월별 매출 대시보드", layout="wide")

st.markdown(
    """
    <style>
    body { background-color: #0f172a; color: #e5e7eb; }
    .stMetric { background-color: #111827; border-radius: 10px; padding: 10px; }
    h1, h2, h3, h4, h5 { color: #38bdf8; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 월별 매출 대시보드")

uploaded_file = st.file_uploader("CSV 업로드 (열: 월, 매출액, 전년동월, 증감률)", type=["csv"])

# 샘플 데이터
sample_data = pd.DataFrame({
    "월": ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06","2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
    "매출액": [12000000,13500000,11000000,18000000,21000000,16500000,17500000,19000000,20000000,22000000,25000000,28000000],
    "전년동월": [10500000,11200000,12800000,15200000,18500000,15000000,16000000,16800000,17200000,19000000,21000000,23500000],
    "증감률": [14.3,20.5,-14.1,18.4,13.5,10.0,9.4,13.1,16.3,15.8,19.0,19.1]
})

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = sample_data.copy()

# KPI 계산
total_sales = df["매출액"].sum()
avg_growth = df["증감률"].mean()
max_row = df.loc[df["매출액"].idxmax()]
min_row = df.loc[df["매출액"].idxmin()]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("총 매출", f"{total_sales:,.0f} 원")
kpi2.metric("평균 증감률", f"{avg_growth:.2f}%")
kpi3.metric("최대 매출", f"{max_row['매출액']:,.0f} 원", max_row['월'])
kpi4.metric("최소 매출", f"{min_row['매출액']:,.0f} 원", min_row['월'])

# 월별 매출 추이 (전년 대비)
fig1 = px.line(df, x="월", y=["매출액", "전년동월"], markers=True, title="월별 매출 추이 (전년 동월 대비)")
fig1.update_layout(legend_title_text="구분", plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", font_color="#e5e7eb")

# 증감률 막대
fig2 = px.bar(df, x="월", y="증감률", title="증감률(%)", color="증감률", color_continuous_scale="RdBu")
fig2.update_layout(plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", font_color="#e5e7eb")

# 누적 매출 추이
df_cum = df.copy()
df_cum["누적매출"] = df_cum["매출액"].cumsum()
fig3 = px.area(df_cum, x="월", y="누적매출", title="누적 매출 추이")
fig3.update_layout(plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", font_color="#e5e7eb")

# 전년 대비 그룹 막대
fig4 = px.bar(df, x="월", y=["매출액", "전년동월"], barmode="group", title="전년 동월 대비 비교")
fig4.update_layout(plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", font_color="#e5e7eb")

st.plotly_chart(fig1, use_container_width=True)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)
