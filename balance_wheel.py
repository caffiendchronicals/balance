import streamlit as st
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Balance Wheel", layout="centered")

st.title("Life Balance")
st.write("Adjust the sliders below to rate each area (0 = very low, 10 = very high).")
st.write("You can also add notes for each area.")

# File to store history
DATA_FILE = "data.json"

# Your custom categories
categories = ["Physical", "Emotional", "Professional", "Creativity", "Financial", "Adventures"]

# --- Fixed base colors per category ---
base_colors = {
    "Physical": "blue",
    "Emotional": "yellow",
    "Professional": "purple",
    "Creativity": "teal",
    "Financial": "grey",
    "Adventures": "orange"
}

# --- Load saved history ---
history = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = {}

# --- Choose a past snapshot to view ---
if history:
    selected_time = st.selectbox(
        "📜 View past entries",
        ["(Current Input)"] + list(history.keys())[::-1]  # newest first
    )
else:
    selected_time = "(Current Input)"

# --- Ratings and Notes ---
if selected_time != "(Current Input)":
    # Viewing past snapshot
    snapshot = history[selected_time]
    ratings = [snapshot[cat]["rating"] for cat in categories]
    notes = {cat: snapshot[cat]["note"] for cat in categories}
    st.info(f"Showing saved snapshot from {selected_time}")
else:
    # Current input (editable sliders and notes)
    latest_data = history[list(history.keys())[-1]] if history else {}
    ratings = []
    notes = {}
    for cat in categories:
        default_rating = latest_data.get(cat, {}).get("rating", 5)
        default_note = latest_data.get(cat, {}).get("note", "")
        rating = st.slider(cat, 0, 10, default_rating)
        note = st.text_area(f"Notes for {cat}", default_note, key=f"note_{cat}")
        ratings.append(rating)
        notes[cat] = note

# --- Pie chart with consistent colors and highlights ---
fig, ax = plt.subplots(figsize=(6, 6))

max_rating = max(ratings)
min_rating = min(ratings)

colors = []
for i, cat in enumerate(categories):
    if ratings[i] == max_rating:
        colors.append("green")  # highlight highest
    elif ratings[i] == min_rating:
        colors.append("red")    # highlight lowest
    else:
        colors.append(base_colors[cat])  # consistent category color

ax.pie(
    ratings,
    labels=categories,
    autopct="%1.1f%%",
    startangle=90,
    colors=colors
)

ax.set_title("Your Balance Wheel", fontsize=16)
st.pyplot(fig)

# --- Display notes ---
st.subheader("📝 Your Notes")
for cat, note in notes.items():
    if note.strip():
        st.markdown(f"**{cat}:** {note}")

# --- Save button (only for current input) ---
if selected_time == "(Current Input)":
    if st.button("💾 Save Progress"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history[timestamp] = {
            cat: {"rating": ratings[i], "note": notes[cat]}
            for i, cat in enumerate(categories)
        }
        with open(DATA_FILE, "w") as f:
            json.dump(history, f, indent=4)
        st.success(f"✅ Progress saved at {timestamp}")

# --- Mini History Dashboard ---
if history:
    st.subheader("📊 Past Snapshots Dashboard")
    for ts in sorted(history.keys(), reverse=True):  # newest first
        snapshot = history[ts]
        st.markdown(f"**Timestamp:** {ts}")
        # Build a DataFrame for display
        df = pd.DataFrame({
            "Category": categories,
            "Rating": [snapshot[cat]["rating"] for cat in categories],
            "Note": [snapshot[cat]["note"] for cat in categories]
        })
        st.table(df)

import io

# EXPORT (download) your history as JSON
if history:
    st.download_button(
        "📥 Export history (download JSON)",
        data=json.dumps(history, indent=4),
        file_name="balance_wheel_history.json",
        mime="application/json"
    )

# IMPORT (upload) a JSON backup to restore
uploaded = st.file_uploader("📤 Upload JSON backup to restore (will overwrite)", type=["json"])
if uploaded:
    try:
        new_hist = json.load(uploaded)
        with open(DATA_FILE, "w") as f:
            json.dump(new_hist, f, indent=4)
        st.success("Imported backup — app will refresh to show restored data.")
        st.session_state.refresh_flag = not st.session_state.get("refresh_flag", False)
    except Exception as e:
        st.error("Failed to import JSON: " + str(e))


# --- Manage Saves Section with Automatic Refresh ---
st.subheader("⚙️ Manage Saved Progress")

if "refresh_flag" not in st.session_state:
    st.session_state.refresh_flag = False

if history:
    st.write("### Saved Snapshots")
    
    for ts in sorted(history.keys(), reverse=True):
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(ts)
        with col2:
            if st.button(f"Delete", key=f"del_{ts}"):
                del history[ts]
                with open(DATA_FILE, "w") as f:
                    json.dump(history, f, indent=4)
                st.success(f"Deleted snapshot {ts}")
                st.session_state.refresh_flag = not st.session_state.refresh_flag

    if st.button("⚠️ Reset All Progress"):
        history.clear()
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.success("All progress has been reset!")
        st.session_state.refresh_flag = not st.session_state.refresh_flag

# Trigger automatic refresh via session state
if st.session_state.refresh_flag:
    st.session_state.refresh_flag = False  # reset flag
    st.experimental_rerun()
