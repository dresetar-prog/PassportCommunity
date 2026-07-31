import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Cohort Leaderboard", page_icon="🏆", layout="centered"
)

st.title("🏆 Cohort Point Tracker")
st.write(
    "Select your name below to view your standing and compare your points with your cohort."
)

# 2. Cohort Data (Replace or connect to a Google Sheet / CSV as needed)
data = {
    "User": [
        "Alex",
        "Jordan",
        "Taylor",
        "Morgan",
        "Sam",
        "Chris",
        "Dakota",
        "Riley",
        "Jesse",
        "Casey",
    ],
    "Points": [120, 95, 150, 80, 110, 135, 90, 105, 140, 75],
}

df = pd.DataFrame(data)

# 3. User Selection
selected_user = st.selectbox("Select Your Name:", df["User"].sort_values())

# Highlight selected user vs others
df["Category"] = df["User"].apply(
    lambda x: "You" if x == selected_user else "Cohort Member"
)

# Sort leaderboard by highest score
df_sorted = df.sort_values(by="Points", ascending=False).reset_index(
    drop=True
)

# Calculate Rank & Points for Selected User
user_row = df_sorted[df_sorted["User"] == selected_user].iloc[0]
user_points = user_row["Points"]
user_rank = df_sorted[df_sorted["User"] == selected_user].index[0] + 1

# 4. Display Quick Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Your Points", value=f"{user_points} pts")
with col2:
    st.metric(label="Your Rank", value=f"#{user_rank} of {len(df)}")

st.markdown("---")

# 5. Build Interactive Bar Chart
fig = px.bar(
    df_sorted,
    x="User",
    y="Points",
    color="Category",
    color_discrete_map={
        "You": "#FF4B4B",  # Distinct red color for the selected user
        "Cohort Member": "#1F77B4",  # Standard blue for everyone else
    },
    title="Cohort Score Comparison",
    text="Points",
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_title="Participant",
    yaxis_title="Total Points",
    legend_title="",
    showlegend=True,
)

st.plotly_chart(fig, use_container_width=True)