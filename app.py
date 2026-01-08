import streamlit as st
import json
import pandas as pd
import pydeck as pdk
from datetime import datetime

# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(page_title="The White Box", layout="wide")

# =====================================================
# ZONE COORDINATES (UI FALLBACK)
# =====================================================
ZONE_COORDS = {
    "Gandhipuram": (11.0168, 76.9558),
    "Peelamedu": (11.0232, 77.0020),
    "RS_Puram": (11.0108, 76.9442),
    "Saibaba_Colony": (11.0276, 76.9495),
    "Ukkadam": (10.9916, 76.9629),
    "Singanallur": (11.0000, 77.0280)
}

# =====================================================
# LOAD PLATFORM DATA
# =====================================================
@st.cache_data
def load_platform_data():
    with open("platform_insights.json", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data["zones"])
    apai = data.get("APAI", None)

    if "lat" not in df.columns:
        df["lat"] = df["zone"].map(lambda z: ZONE_COORDS[z][0])
        df["lon"] = df["zone"].map(lambda z: ZONE_COORDS[z][1])

    return df, apai

df, APAI = load_platform_data()

# =====================================================
# SESSION STATE
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================================
# HELPERS
# =====================================================
def zone_color_text(state):
    return "🟢 Green" if state == 2 else "🟡 Yellow" if state == 1 else "🔴 Red"

def zone_color_rgb(state):
    return (
        [0, 180, 0, 160] if state == 2 else
        [255, 200, 0, 160] if state == 1 else
        [200, 0, 0, 160]
    )

def explain_zone(row):
    text = []
    text.append(
        f"Task assignment here is "
        f"{'high' if row.assignment_class==2 else 'moderate' if row.assignment_class==1 else 'low'}."
    )
    text.append(
        f"Incentives appear "
        f"{'frequently' if row.incentive_class==2 else 'sometimes' if row.incentive_class==1 else 'rarely'}."
    )
    text.append(f"Average earnings are about ₹{row.avg_pay}.")
    if row.change_flag:
        text.append(
            f"A recent platform change reduced earnings by "
            f"{abs(row.pay_change_pct)}%."
        )
    if row.fairness_label == "Unfair":
        text.append("Workers here earn significantly less than other areas.")
    return " ".join(text)

# =====================================================
# 🌟 IMPROVED LOGIN PAGE
# =====================================================
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h2 style='text-align:center;'>🐧 The White Box</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center;'>Hi! I’m <b>Pingo</b> 🐧<br>"
            "I help explain how delivery apps work — simply.</p>",
            unsafe_allow_html=True
        )

        st.info(
            "🔍 This is a transparency tool.\n\n"
            "No real passwords.\n"
            "No data tracking.\n"
            "Just explanations."
        )

        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Enter The White Box")

        if submit:
            if username.strip() == "" or password.strip() == "":
                st.warning("Please enter both username and password.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_name = username
                st.success(f"Welcome, {username}!")
                st.rerun()

# =====================================================
# MAIN APPLICATION (UNCHANGED)
# =====================================================
else:
    st.sidebar.title("The White Box")
    st.sidebar.markdown(f"👋 Hi, **{st.session_state.user_name}**")

    page = st.sidebar.radio(
        "Navigate",
        [
            "How Delivery Apps Work",
            "Zone Map",
            "Zone Explanation",
            "Behind The White Box"
        ]
    )

    if page == "How Delivery Apps Work":
        st.title("🧠 How Delivery Apps Work (White Box View)")

        st.code("""
Customer Orders
(time, location)
        ↓
Platform Context
(demand, traffic, time)
        ↓
Hidden Assignment & Pricing Algorithm
(black box)
        ↓
Observed Outcomes
(orders, pay, incentives)
        ↓
THE WHITE BOX
(pattern analysis & explanations)
        ↓
Worker-Friendly Insights
(green / yellow / red zones)
        """)

        st.info(
            "The White Box does not access platform code. "
            "It explains patterns in outcomes."
        )

    elif page == "Zone Map":
        st.title("🗺️ Opportunity Map")

        map_df = df.copy()
        map_df["color"] = map_df["zone_state"].apply(zone_color_rgb)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_color="color",
            get_radius=700,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=12
        )

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"html": "<b>{zone}</b><br/>₹{avg_pay}"}
            )
        )

    elif page == "Zone Explanation":
        st.title("🔍 Zone Explanation")

        zone = st.selectbox("Select area", sorted(df["zone"].unique()))
        row = df[df.zone == zone].iloc[0]

        st.subheader(f"{zone} — {zone_color_text(row.zone_state)}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Assignment Level", row.assignment_class)
        c2.metric("Incentive Level", row.incentive_class)
        c3.metric("Avg Pay (₹)", row.avg_pay)

        st.write(explain_zone(row))

    elif page == "Behind The White Box":
        st.title("🧠 Behind The White Box")

        st.markdown("""
        • Algorithm Transparency  
        • Change Detection  
        • Fairness Assessment  
        • Worker-Centred Reporting  
        """)

        st.metric("Algorithm–Pay Influence Index (APAI)", APAI)
