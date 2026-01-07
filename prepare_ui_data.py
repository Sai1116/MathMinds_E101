import pandas as pd

# Load raw dataset
df = pd.read_csv("gig_dataset.csv")

# -------------------------
# Aggregate per pickup zone
# -------------------------
zone_summary = df.groupby("pickup_zone").agg(
    avg_fare=("total_fare", "mean"),
    min_fare=("total_fare", "min"),
    max_fare=("total_fare", "max"),
    incentive_rate=("incentive_bonus", lambda x: (x > 0).mean()),
    dominant_demand=("zone_demand_level", lambda x: x.value_counts().idxmax())
).reset_index()

# -------------------------
# Assignment availability (simple & explainable)
# -------------------------
def assignment_level(demand):
    if demand == "High":
        return "High"
    elif demand == "Medium":
        return "Medium"
    else:
        return "Low"

zone_summary["assignment_level"] = zone_summary["dominant_demand"].apply(assignment_level)

# -------------------------
# Incentive likelihood
# -------------------------
def incentive_label(p):
    if p > 0.4:
        return "High"
    elif p > 0.2:
        return "Medium"
    else:
        return "Low"

zone_summary["incentive_likelihood"] = zone_summary["incentive_rate"].apply(incentive_label)

# -------------------------
# Coordinates for map
# -------------------------
zone_coords = {
    "Gandhipuram": (11.017, 76.967),
    "Peelamedu": (11.029, 77.021),
    "RS_Puram": (11.010, 76.947),
    "Saibaba_Colony": (11.041, 76.951),
    "Ukkadam": (10.990, 76.962),
    "Singanallur": (11.000, 77.030)
}

zone_summary["lat"] = zone_summary["pickup_zone"].map(lambda z: zone_coords[z][0])
zone_summary["lng"] = zone_summary["pickup_zone"].map(lambda z: zone_coords[z][1])

# -------------------------
# Explanation text
# -------------------------
zone_summary["explanation"] = (
    "Demand is " + zone_summary["dominant_demand"] +
    ", resulting in " + zone_summary["assignment_level"] +
    " task availability. Incentives are " +
    zone_summary["incentive_likelihood"].str.lower() + "."
)

# -------------------------
# Save UI dataset
# -------------------------
zone_summary.rename(columns={"pickup_zone": "zone"}, inplace=True)
zone_summary.to_csv("zone_ui_data.csv", index=False)

print("zone_ui_data.csv created")
print(zone_summary)