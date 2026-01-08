import streamlit as st
import json
import pandas as pd
import pydeck as pdk
from datetime import datetime

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
# SAFE JSON LOADER
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
        f"Tasks are assigned at a "
        f"{'high' if row.assignment_class==2 else 'medium' if row.assignment_class==1 else 'low'} rate."
    )
    text.append(
        f"Incentives appear "
        f"{'frequently' if row.incentive_class==2 else 'occasionally' if row.incentive_class==1 else 'rarely'}."
    )
    text.append(f"Average earnings here are ₹{row.avg_pay}.")
    if row.change_flag:
        text.append(
            f"A recent platform behaviour change reduced earnings by "
            f"{abs(row.pay_change_pct)}%."
        )
    if row.fairness_label == "Unfair":
        text.append("Workers here earn significantly less than other areas.")
    return " ".join(text)

# =====================================================
# LOGIN
# =====================================================
if not st.session_state.logged_in:
    st.title("🔓 Welcome to The White Box")

    with st.form("login"):
        name = st.text_input("Your name (optional)")
        submit = st.form_submit_button("Enter")

    if submit:
        st.session_state.logged_in = True
        st.rerun()

# =====================================================
# MAIN APP
# =====================================================
else:
    st.sidebar.title("The White Box")
    page = st.sidebar.radio(
        "Navigate",
        [
            "How Swiggy Works",
            "Zone Map",
            "Zone Explanation",
            "Behind The White Box"
        ]
    )

    # -------------------------------
    if page == "How Swiggy Works":
        st.title("🧠 How Swiggy Works (White Box View)")
        st.markdown("""
        Platforms combine **time, location, demand, traffic and history**.
        Workers only see outcomes — not the logic.

        **The White Box converts outcomes into explanations.**
        """)

    # -------------------------------
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

        st.info("🟢 Good • 🟡 Mixed • 🔴 Risky")

    # -------------------------------
    elif page == "Zone Explanation":
        st.title("🔍 Zone Explanation")

        zone = st.selectbox("Select area", sorted(df["zone"].unique()))
        row = df[df.zone == zone].iloc[0]

        st.subheader(f"{zone} — {zone_color_text(row.zone_state)}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Assignment Level", row.assignment_class)
        c2.metric("Incentive Level", row.incentive_class)
        c3.metric("Avg Pay (₹)", row.avg_pay)

        st.markdown("### What is happening here?")
        st.write(explain_zone(row))

        st.markdown("### Fairness Assessment")
        st.write(f"Fairness: **{row.fairness_label}**")
        st.write(f"Pay gap vs best area: ₹{row.pay_gap_vs_best}")

        if row.change_flag:
            st.warning(
                f"Platform change detected "
                f"({row.pay_change_pct}% impact on earnings)"
            )

    # -------------------------------
    elif page == "Behind The White Box":
        st.title("🧠 Behind The White Box")

        st.markdown("""
        **Algorithm Transparency**
        - Explains how assignment, incentives and pay emerge from patterns

        **Change Detection**
        - Flags undocumented platform behaviour shifts

        **Fairness Assessment**
        - Compares earnings across areas

        **Worker-Centred Reporting**
        - Simple visuals and explanations, not commands
        """)

        st.metric("Algorithm–Pay Influence Index (APAI)", APAI)
