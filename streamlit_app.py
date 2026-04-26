import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# -------------------------
# DB Connection
# -------------------------
conn = psycopg2.connect(
    host="localhost",
    database="airflow_db",
    user="airflow",
    password="airflow"
)

# -------------------------
# Load Data
# -------------------------
df = pd.read_sql(
    "SELECT * FROM raw.weather_data ORDER BY created_at",
    conn
)

# Ensure sorting
df = df.sort_values("created_at")

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")

start_date = st.sidebar.date_input("Start Date", df["created_at"].min())
end_date = st.sidebar.date_input("End Date", df["created_at"].max())

df = df[
    (df["created_at"] >= pd.to_datetime(start_date)) &
    (df["created_at"] <= pd.to_datetime(end_date))
]

# -------------------------
# Title
# -------------------------
st.title("🌤 Weather Dashboard")

# -------------------------
# KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Avg Temp",
    f"{df['temperature'].mean():.1f} °C"
)

col2.metric(
    "Max Temp",
    f"{df['temperature'].max():.1f} °C"
)

col3.metric(
    "Min Temp",
    f"{df['temperature'].min():.1f} °C"
)

col4.metric(
    "Avg Humidity",
    f"{df['humidity'].mean():.1f}%"
)

# -------------------------
# Charts Row
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡 Temperature Over Time")
    fig_temp = px.line(df, x="created_at", y="temperature")
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.subheader("💧 Humidity Over Time")
    fig_hum = px.area(df, x="created_at", y="humidity")
    st.plotly_chart(fig_hum, use_container_width=True)

# -------------------------
# Scatter (Relationship)
# -------------------------
st.subheader("🔗 Temperature vs Humidity")
fig_scatter = px.scatter(df, x="temperature", y="humidity")
st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------------
# Rolling Average (Trend)
# -------------------------
st.subheader("📈 Temperature Trend (Rolling Average)")

df["rolling_temp"] = df["temperature"].rolling(window=5).mean()

fig_roll = px.line(df, x="created_at", y=["temperature", "rolling_temp"])
st.plotly_chart(fig_roll, use_container_width=True)

# -------------------------
# Insights Section
# -------------------------
st.subheader("🧠 Insights")

st.write(f"""
- 🔥 Highest temperature: **{df['temperature'].max():.1f} °C**
- ❄️ Lowest temperature: **{df['temperature'].min():.1f} °C**
- 💧 Highest humidity: **{df['humidity'].max():.1f}%**
- 🌵 Lowest humidity: **{df['humidity'].min():.1f}%**
""")

# -------------------------
# Raw Data (Collapsed)
# -------------------------
with st.expander("📊 Show Raw Data"):
    st.dataframe(df)

st.subheader("📋 Raw Data")
st.dataframe(df)    