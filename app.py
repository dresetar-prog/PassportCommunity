import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Passport Community Masterclass Leaderboard", 
    layout="centered"
)

st.title("Passport Community Masterclass Leaderboard")

# 2. Connect to the Personal Google Sheet (Users Tab)
SHEET_ID = "18CTdh0cuM8Ag4EGTqXflWzbFYCobNCoOq00wKcYeEIs"
USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Users"

# Cache the data for 60 seconds so it doesn't overload Google with requests
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(USERS_URL)
    # Combine First and Last Name for the chart display
    df["Display Name"] = df["First Name"].astype(str) + " " + df["Last Name"].astype(str)
    # Ensure Total Points is treated as a number and fill missing values with 0
    df["Total Points"] = pd.to_numeric(df["Total Points"], errors="coerce").fillna(0)
    return df

# Load the data from Google Sheets
try:
    df = load_data()
except Exception as e:
    st.error("Could not load data. Please ensure the Google Sheet is set to 'Anyone with the link can view'.")
    st.stop()

# 3. Simple Email Login System
st.write("Please enter your registered email to view your dashboard.")
email_input = st.text_input("Email Address:").strip().lower()

if email_input:
    # Make sure we compare lowercase to lowercase so capitalization doesn't matter
    df["Email_lower"] = df["Email"].astype(str).str.strip().str.lower()

    if email_input in df["Email_lower"].values:
        st.success("Welcome back!")
        
        # Get the logged-in user's display name based on email
        selected_user = df[df["Email_lower"] == email_input].iloc[0]["Display Name"]

        # Sort leaderboard by highest score
        df_sorted = df.sort_values(by="Total Points", ascending=False).reset_index(drop=True)

        # Highlight selected user vs cohort members
        df_sorted["Category"] = df_sorted["Display Name"].apply(
            lambda x: "You" if x == selected_user else "Cohort Member"
        )

        # Calculate Rank & Points for Selected User
        user_rank = df_sorted[df_sorted["Display Name"] == selected_user].index[0] + 1
        user_points = df_sorted[df_sorted["Display Name"] == selected_user].iloc[0]["Total Points"]

        # 4. Display Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Your Points", value=f"{int(user_points)} pts")
        with col2:
            st.metric(label="Your Rank", value=f"#{user_rank} of {len(df_sorted)}")

        st.markdown("---")

        # 5. Build Interactive Bar Chart
        fig = px.bar(
            df_sorted,
            x="Display Name",
            y="Total Points",
            color="Category",
            color_discrete_map={
                "You": "#FF4B4B",        # Distinct red color for the logged-in user
                "Cohort Member": "#1F77B4" # Standard blue for everyone else
            },
            title="Cohort Score Comparison",
            text="Total Points",
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Participant",
            yaxis_title="Total Points",
            legend_title="",
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Email not found. Please check your spelling or ensure you are registered.")
