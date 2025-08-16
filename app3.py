import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------
# Palette (가독성 높은 추천 팔레트) — 전역 배경색 지정 안 함
# -------------------------------------------------
PRIMARY = "#3366CC"  # 매출(주 색: 블루)
SECONDARY = "#DC3912"  # 증감률/강조(레드 오렌지)
ACCENT1 = "#FF9900"  # 보조선/누적(오렌지)
ACCENT2 = "#109618"  # 증가/이동평균(그린)
NEUTRAL = "#AAAAAA"  # 연결선/보조

st.set_page_config(page_title="월별 매출 대시보드", layout="wide")
st.title("📊 월별 매출 대시보드 — 분석 강화")

uploaded_file = st.file_uploader("CSV 업로드 (열: 월, 매출액, 전년동월, 증감률)", type=["csv"])

# -------------------------------------------------
# 데이터 로드 & 정규화
# -------------------------------------------------
def _to_num(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return np.nan

sample_data = pd.DataFrame({
    "월": ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06","2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
    "매출액": [12000000,13500000,11000000,18000000,21000000,16500000,17500000,19000000,20000000,22000000,25000000,28000000],
    "전년동월": [10500000,11200000,12800000,15200000,18500000,15000000,16000000,16800000,17200000,19000000,21000000,23500000],
    "증감률": [14.3,20.5,-14.1,18.4,13.5,10.0,9.4,13.1,16.3,15.8,19.0,19.1]
})

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="cp949")
else:
    df = sample_data.copy()

# 열 정리
cols_map = {c: c.strip() for c in df.columns}
df = df.rename(columns=cols_map)
required = ["월", "매출액", "전년동월"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"누락된 열: {', '.join(missing)}")
    st.stop()

# 숫자화
df["매출액"] = df["매출액"].apply(_to_num)
df["전년동월"] = df["전년동월"].apply(_to_num)
if "증감률" in df.columns:
    df["증감률"] = df["증감률"].apply(_to_num)
else:
    df["증감률"] = np.nan

# 월 정렬 및 파생 지표
df["월"] = df["월"].astype(str).str.slice(0, 7)
df = df.sort_values("월").reset_index(drop=True)
df["YoY(%)"] = np.where(df["전년동월"].gt(0), (df["매출액"] / df["전년동월"] - 1) * 100, np.nan)
df["MoM(%)"] = df["매출액"].pct_change() * 100
df["Δ전년(원)"] = df["매출액"] - df["전년동월"]
df["3개월MA"] = df["매출액"].rolling(3).mean()

# 분기 필터
def _quarter(m):
    try:
        mth = int(str(m)[5:7])
    except Exception:
        return "-"
    return "Q1" if mth <= 3 else ("Q2" if mth <= 6 else ("Q3" if mth <= 9 else "Q4"))

df["분기"] = df["월"].apply(_quarter)
col_f1, col_f2, col_f3 = st.columns([1,1,2])
with col_f1:
    q_sel = st.selectbox("분기", options=["전체", "Q1", "Q2", "Q3", "Q4"], index=0)
with col_f2:
    gmin = st.number_input("YoY 최소(%)", value=None, step=0.1, format="%0.1f")
with col_f3:
    gmax = st.number_input("YoY 최대(%)", value=None, step=0.1, format="%0.1f")

fdf = df.copy()
if q_sel != "전체":
    fdf = fdf[fdf["분기"] == q_sel]
if gmin is not None:
    fdf = fdf[(fdf["YoY(%)"].notna()) & (fdf["YoY(%)"] >= float(gmin))]
if gmax is not None:
    fdf = fdf[(fdf["YoY(%)"].notna()) & (fdf["YoY(%)"] <= float(gmax))]
if fdf.empty:
    st.info("필터 결과가 없습니다. 필터를 조정해 주세요.")
    fdf = df.copy()

# -------------------------------------------------
# KPI
# -------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("총 매출", f"{fdf['매출액'].sum():,.0f} 원")
k2.metric("평균 YoY", f"{fdf['YoY(%)'].mean():.2f}%")
k3.metric("평균 MoM", f"{fdf['MoM(%)'].mean():.2f}%")
mx = fdf.loc[fdf["매출액"].idxmax()]
mn = fdf.loc[fdf["매출액"].idxmin()]
k4.metric("최대 매출", f"{mx['매출액']:,.0f} 원", mx['월'])
k5.metric("최소 매출", f"{mn['매출액']:,.0f} 원", mn['월'])

# -------------------------------------------------
# 1) Combo: 매출(막대, 블루) + YoY%(라인, 레드) + 3개월MA(라인, 그린)
# -------------------------------------------------
combo = make_subplots(specs=[[{"secondary_y": True}]])
combo.add_trace(go.Bar(x=fdf["월"], y=fdf["매출액"], name="매출액", marker_color=PRIMARY), secondary_y=False)
combo.add_trace(go.Scatter(x=fdf["월"], y=fdf["YoY(%)"], name="YoY(%)", mode="lines+markers", line=dict(color=SECONDARY, width=2)), secondary_y=True)
combo.add_trace(go.Scatter(x=fdf["월"], y=fdf["3개월MA"], name="3개월 이동평균", mode="lines", line=dict(color=ACCENT2, width=3, dash="dot")), secondary_y=False)
combo.update_yaxes(title_text="금액(원)", secondary_y=False)
combo.update_yaxes(title_text="YoY(%)", secondary_y=True)
combo.update_layout(title_text="매출 vs YoY% (3개월 이동평균 포함)", legend_orientation="h", margin=dict(t=30, r=10, b=40, l=50))

# -------------------------------------------------
# 2) MoM Waterfall: 월별 증감 금액 브리지
# -------------------------------------------------
values = [fdf["매출액"].iloc[0]] + fdf["매출액"].diff().iloc[1:].tolist()
measures = ["absolute"] + ["relative"] * (len(fdf) - 1)
water = go.Figure(go.Waterfall(
    x=fdf["월"], measure=measures, y=values,
    increasing=dict(marker_color=ACCENT2),  # 증가 → 그린
    decreasing=dict(marker_color=SECONDARY), # 감소 → 레드 오렌지
    totals=dict(marker_color=PRIMARY),
    connector=dict(line=dict(color=NEUTRAL))
))
water.update_layout(title_text="월별 MoM 변화 브리지 (Waterfall)", margin=dict(t=30, r=10, b=40, l=50))

# -------------------------------------------------
# 3) 전년 대비 편차(Δ전년)
# -------------------------------------------------
colors = [ACCENT2 if v >= 0 else SECONDARY for v in fdf["Δ전년(원)"]]
delta_bar = go.Figure(go.Bar(x=fdf["월"], y=fdf["Δ전년(원)"], marker_color=colors, name="Δ전년"))
delta_bar.update_layout(title_text="전년 대비 차이 (Δ전년)", margin=dict(t=30, r=10, b=40, l=50))

# -------------------------------------------------
# 4) Pareto: 월 매출 상위 기여도 (누적%)
# -------------------------------------------------
pareto_df = fdf.sort_values("매출액", ascending=False).reset_index(drop=True)
pareto_df["누적비중(%)"] = pareto_df["매출액"].cumsum() / pareto_df["매출액"].sum() * 100
pareto = make_subplots(specs=[[{"secondary_y": True}]])
pareto.add_trace(go.Bar(x=pareto_df["월"], y=pareto_df["매출액"], name="매출액", marker_color=PRIMARY), secondary_y=False)
pareto.add_trace(go.Scatter(x=pareto_df["월"], y=pareto_df["누적비중(%)"], name="누적비중(%)", mode="lines+markers", line=dict(color=ACCENT1)), secondary_y=True)
pareto.update_yaxes(title_text="금액(원)", secondary_y=False)
pareto.update_yaxes(title_text="누적비중(%)", secondary_y=True, range=[0, 100])
pareto.update_layout(title_text="Pareto 분석: 상위 월의 매출 기여도", legend_orientation="h", margin=dict(t=30, r=10, b=40, l=50))

# -------------------------------------------------
# 렌더링
# -------------------------------------------------
st.subheader("① 매출·성장 동시 관찰")
st.plotly_chart(combo, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("② 월간 변화 구조 (Waterfall)")
    st.plotly_chart(water, use_container_width=True)
with c2:
    st.subheader("③ 전년 대비 편차")
    st.plotly_chart(delta_bar, use_container_width=True)

st.subheader("④ Pareto: 상위 월 기여도")
st.plotly_chart(pareto, use_container_width=True)

st.caption("ⓘ 배경색은 전역 지정하지 않았고, 팔레트는 블루/레드·오렌지/그린 기반으로 가독성을 높였습니다.")
