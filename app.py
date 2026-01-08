import streamlit as st
import json
import pandas as pd
from datetime import datetime

# =========================================================
# BASIC CONFIG
# =========================================================
st.set_page_config(
    page_title="The White Box",
    layout="wide"
)

# =========================================================
# LOAD ML OUTPUT (FROM YOUR EXISTING BACKEND)
# =========================================================
@st.cache_data
def load_platform_data():
    with open("platform_output.json", "r") as f:
        return pd.DataFrame(json.load(f))

df = load_platform_data()

# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def zone_color(state):
    return "🟢 Green" if state == 2 else "🟡 Yellow" if state == 1 else "🔴 Red"

def simple_zone_reason(row):
    reasons = []
    if row.assignment_class == 0:
        reasons.append("fewer orders appear here")
    if row.incentive_class == 0:
        reasons.append("incentives are rare")
    if row.fairness_class == 0:
        reasons.append("earnings are usually lower")

    if not reasons:
        return "This area generally offers stable opportunities."

    return "This area feels slower because " + ", ".join(reasons) + "."

# =========================================================
# PAGE 1 — LOGIN
# =========================================================
if not st.session_state.logged_in:

    st.title("🔓 Welcome to The White Box")

    st.markdown("""
    **The White Box** helps explain how food-delivery platforms *seem* to work  
    — using patterns, not guesses.

    You don’t need technical knowledge.
    """)

    with st.form("login"):
        name = st.text_input("Your name (optional)")
        phone = st.text_input("Phone / Email (optional)")
        submit = st.form_submit_button("Enter")

    if submit:
        st.session_state.logged_in = True
        st.session_state.user_name = name if name else "Guest"
        st.rerun()

# =========================================================
# MAIN APP (AFTER LOGIN)
# =========================================================
else:

    # -----------------------------------------------------
    # SIDEBAR NAVIGATION
    # -----------------------------------------------------
    st.sidebar.title("The White Box")
    page = st.sidebar.radio(
        "Go to",
        [
            "How Swiggy Works",
            "Zone Map",
            "Zone Explanation",
            "Log Your Day"
        ]
    )

    # =====================================================
    # PAGE 2 — HOW SWIGGY WORKS (STORY FIRST)
    # =====================================================
    if page == "How Swiggy Works":

        st.title("🧠 How Swiggy Works (Simply Explained)")

        st.markdown("""
        ### Step 1: People order food
        Orders come in at different times and places.

        ### Step 2: Delivery partners are spread unevenly
        Some areas have many riders. Some don’t.

        ### Step 3: The platform quietly matches everything
        Time, distance, traffic, demand — all combined.

        ### Step 4: You only see the result
        Orders appear or don’t. Pay changes. Incentives come and go.

        ---
        ### ❓ The problem
        You never see *why* these things happen.

        ### ✅ The White Box
        This tool looks at **patterns over time**  
        and explains what *seems* to be happening.
        """)

    # =====================================================
    # PAGE 3 — ZONE MAP (VISUAL UNDERSTANDING)
    # =====================================================
    elif page == "Zone Map":

        st.title("🗺️ Area Overview")

        st.markdown("""
        Each area is shown as:
        - 🟢 **Green** → usually good flow
        - 🟡 **Yellow** → mixed or unstable
        - 🔴 **Red** → fewer orders or lower pay
        """)

        display_df = df.copy()
        display_df["Status"] = display_df["zone_state"].apply(zone_color)

        st.dataframe(
            display_df[["zone", "Status"]],
            use_container_width=True
        )

        st.info(
            "These colors are based on past patterns — not live predictions."
        )

    # =====================================================
    # PAGE 4 — ZONE EXPLANATION (WHY THIS HAPPENS)
    # =====================================================
    elif page == "Zone Explanation":

        st.title("🔍 Why Does This Area Feel This Way?")

        zone = st.selectbox(
            "Choose an area",
            sorted(df["zone"].unique())
        )

        row = df[df.zone == zone].iloc[0]

        st.subheader(f"Area {zone} — {zone_color(row.zone_state)}")

        st.markdown("### What we observe:")
        st.write(simple_zone_reason(row))

        st.markdown("""
        **Important**
        - This is not Swiggy’s code.
        - This is what the data *suggests* over time.
        - Patterns can change.
        """)

    # =====================================================
    # PAGE 5 — LOG YOUR DAY (FEEDBACK LOOP)
    # =====================================================
    elif page == "Log Your Day":

        st.title("📒 Log Your Day")

        st.markdown("""
        Help improve explanations by sharing what happened today.
        This does **not** affect orders.
        """)

        with st.form("log_form"):
            zone = st.selectbox("Area worked", sorted(df["zone"].unique()))
            hours = st.selectbox("Time period", ["Morning", "Afternoon", "Evening", "Night"])
            orders = st.selectbox("Orders received", ["0", "1–3", "4–7", "8+"])
            earnings = st.selectbox("Approx earnings", ["Low", "Medium", "High"])
            feel = st.selectbox("How did today feel?", ["Bad", "Normal", "Good"])

            submit = st.form_submit_button("Add Log")

        if submit:
            st.session_state.user_logs.append({
                "time": str(datetime.now()),
                "zone": zone,
                "hours": hours,
                "orders": orders,
                "earnings": earnings,
                "feel": feel
            })
            st.success("Thanks. Your experience has been recorded.")

        if st.session_state.user_logs:
            st.markdown("### Your past logs")
            st.json(st.session_state.user_logs)