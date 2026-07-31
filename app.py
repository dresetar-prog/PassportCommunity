import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Passport Community Masterclass Leaderboard", layout="centered"
)

st.title("Passport Community Masterclass Leaderboard")

# 2. Connections
SHEET_ID = "18CTdh0cuM8Ag4EGTqXflWzbFYCobNCoOq00wKcYeEIs"
USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Users"

# Your Live Google Apps Script Web App Webhook URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxwdMFBNdOnl-ftNBBuozKkF7D81wm9mg7oymWN8o6PyFBx2nans7VywLKq8MM80jj8NA/exec"


# Cache data for 10 seconds so newly registered users appear almost instantly
@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(USERS_URL)
    df["First Name"] = df["First Name"].fillna("").astype(str)
    df["Last Name"] = df["Last Name"].fillna("").astype(str)
    df["Display Name"] = (
        df["First Name"].str.strip() + " " + df["Last Name"].str.strip()
    )
    df["Total Points"] = pd.to_numeric(
        df["Total Points"], errors="coerce"
    ).fillna(0)
    return df


try:
    df = load_data()
except Exception as e:
    st.error(
        "Could not load data. Please ensure the Google Sheet is set to 'Anyone with the link can view'."
    )
    st.stop()

# 3. Navigation: Log In vs Register
mode = st.radio(
    "Choose an option:", ["Log In", "Register New User"], horizontal=True
)

st.markdown("---")

if mode == "Log In":
    st.subheader("Log In")
    email_input = st.text_input("Enter your registered Email Address:").strip().lower()

    if email_input:
        df["Email_lower"] = df["Email"].astype(str).str.strip().str.lower()

        if email_input in df["Email_lower"].values:
            user_data = df[df["Email_lower"] == email_input].iloc[0]
            first_name = user_data["First Name"]
            selected_user = user_data["Display Name"]

            # Personalized Welcome Message
            st.success(f"Welcome back, {first_name}!")

            # Sort leaderboard by highest score
            df_sorted = df.sort_values(
                by="Total Points", ascending=False
            ).reset_index(drop=True)

            # Highlight selected user vs cohort
            df_sorted["Category"] = df_sorted["Display Name"].apply(
                lambda x: "You" if x == selected_user else "Cohort Member"
            )

            # Calculate Rank & Points
            user_rank = (
                df_sorted[df_sorted["Display Name"] == selected_user].index[0]
                + 1
            )
            user_points = df_sorted[
                df_sorted["Display Name"] == selected_user
            ].iloc[0]["Total Points"]

            # Display Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Your Points", value=f"{int(user_points)} pts")
            with col2:
                st.metric(
                    label="Your Rank", value=f"#{user_rank} of {len(df_sorted)}"
                )

            st.markdown("---")

            # Interactive Bar Chart
            fig = px.bar(
                df_sorted,
                x="Display Name",
                y="Total Points",
                color="Category",
                color_discrete_map={
                    "You": "#FF4B4B",
                    "Cohort Member": "#1F77B4",
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
            st.error(
                "Email not found. If you haven't joined yet, please select 'Register New User' above!"
            )

elif mode == "Register New User":
    st.subheader("Register New Account")
    st.write(
        "Fill out your details below to join the Passport Community Masterclass Leaderboard!"
    )

    with st.form("registration_form"):
        reg_first_name = st.text_input("First Name *")
        reg_last_name = st.text_input("Last Name *")
        reg_email = st.text_input("Email Address *").strip().lower()
        reg_company = st.text_input("Company Name (Optional)")

        submit_button = st.form_submit_button("Register & Join Leaderboard")

    if submit_button:
        if not reg_first_name or not reg_last_name or not reg_email:
            st.warning("Please fill in all required fields marked with *.")
        else:
            df["Email_lower"] = df["Email"].astype(str).str.strip().str.lower()
            if reg_email in df["Email_lower"].values:
                st.info("You are already registered! Please switch to 'Log In' above.")
            else:
                # Send data to Google Sheet Webhook
                payload = {
                    "email": reg_email,
                    "firstName": reg_first_name,
                    "lastName": reg_last_name,
                    "company": reg_company,
                }
                
                try:
                    response = requests.post(WEBHOOK_URL, json=payload)
                    st.cache_data.clear()  # Refresh dataset
                    st.success(f"Welcome to the community, {reg_first_name}! You have been successfully registered.")
                    st.info("Switch to 'Log In' above and enter your email to view your personalized chart!")
                except Exception as e:
                    st.error("Registration failed. Please try again.")
