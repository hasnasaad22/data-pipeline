import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

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

df['created_at'] = pd.to_datetime(df['created_at'])

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
# KPIs
# -------------------------
st.title("🌤 Weather Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Temp", f"{df['temperature'].mean():.1f} °C")
col2.metric("Max Temp", f"{df['temperature'].max():.1f} °C")
col3.metric("Min Temp", f"{df['temperature'].min():.1f} °C")
col4.metric("Avg Humidity", f"{df['humidity'].mean():.1f}%")

# -------------------------
# DAILY AGGREGATION (NEW 🔥)
# -------------------------
daily_df = df.copy()
daily_df["date"] = daily_df["created_at"].dt.date

daily_df = daily_df.groupby("date").agg({
    "temperature": "mean",
    "humidity": "mean"
}).reset_index()

# -------------------------
# Charts
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Avg Temperature")
    fig1 = px.line(daily_df, x="date", y="temperature", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("💧 Daily Avg Humidity")
    fig2 = px.bar(daily_df, x="date", y="humidity")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Heatmap (NEW 🔥🔥)
# -------------------------
st.subheader("🔥 Temperature Heatmap (Hour vs Day)")

heatmap_df = df.copy()
heatmap_df["hour"] = heatmap_df["created_at"].dt.hour
heatmap_df["date"] = heatmap_df["created_at"].dt.date

pivot = heatmap_df.pivot_table(
    index="hour",
    columns="date",
    values="temperature"
)

fig_heat = px.imshow(pivot, aspect="auto")
st.plotly_chart(fig_heat, use_container_width=True)

# -------------------------
# Scatter
# -------------------------
st.subheader("🔗 Temp vs Humidity")

fig3 = px.scatter(df, x="temperature", y="humidity", color="temperature")
st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# Raw Data
# -------------------------
with st.expander("📊 Show Raw Data"):
    st.dataframe(df)