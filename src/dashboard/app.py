import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.state import get_user_state
from src.recommender.final_ranker import FinalRanker
from src.recommender.baseline import BaselineRecommender
from src.data_ingestion import load_raw_data

# Page Config
st.set_page_config(page_title="Anti-Addiction RecSys", layout="wide")

# Initialize System
@st.cache_resource
def init_system():
    # FinalRanker initializes its own data and baseline internally
    ranker = FinalRanker()
    return ranker, ranker.data

ranker, data = init_system()

# Sidebar: User Simulation
st.sidebar.header("User Simulation")
user_id = st.sidebar.selectbox("Select User", ["u_1", "u_2", "u_3", "u_4", "u_5"])

# Context Factors
time_of_day = st.sidebar.select_slider("Time of Day", options=["morning", "afternoon", "evening", "night"])
emotion_label = st.sidebar.selectbox("Simulate Emotion", ["neutral", "happy", "sad", "bored", "anxious"])

# Session State for History/Fatigue
if "watch_history" not in st.session_state:
    st.session_state.watch_history = [] 

# Main Header
st.title("🎬 Emotion-Aware Entertainment System")
st.markdown("### Anti-Addiction & Wellbeing Stats")

from src.feature_schema import ContextFeatures

# 1. Calculate & Display State
# We mock the emotion input with the sidebar selection
raw_emotion = {"label": emotion_label, "valence": 0.0, "arousal": 0.0}

context = ContextFeatures(
    time_of_day=time_of_day,
    device_type="desktop", # Schema uses 'device_type', not 'device'
    location="home"
)

# Fetch state
state = get_user_state(user_id, context, raw_emotion)

# OVERRIDE FATIGUE for Demo:
simulated_fatigue = st.sidebar.slider("Simulate Session Duration (minutes)", 0, 180, 30)

if simulated_fatigue > 120:
    state["fatigue"] = {"score": 1.0, "intervention": "hard_break"}
elif simulated_fatigue > 90:
    state["fatigue"] = {"score": 0.8, "intervention": "soft_break"}
else:
    # Update score strictly for visual if not overridden by logic
    state["fatigue"]["score"] = max(state["fatigue"]["score"], simulated_fatigue / 180.0)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Detected Emotion", state["emotion"]["label"].title())
with col2:
    fatigue_score = state["fatigue"].get("score", 0.0)
    st.metric("Fatigue Score", f"{fatigue_score:.2f}")
    st.progress(min(fatigue_score, 1.0))
with col3:
    intervention = state["fatigue"].get("intervention", "None")
    if intervention == "hard_break":
        st.error("⚠️ HARD BREAK TRIGGERED")
    elif intervention == "soft_break":
        st.warning("⚠️ Soft Break / Diversify")
    else:
        st.success("✅ Healthy State")

# 2. Get Recommendations
st.markdown("### Recommended for You")

# IMPORTANT: FinalRanker init in app expects just mocks, but current code in src has `__init__(self)` with hardcoded baseline.
# Wait, previous `FinalRanker` code I wrote in Step 332:
# class FinalRanker:
#     def __init__(self):
#         ...
#         self.baseline = BaselineRecommender(self.data["items"])
# So passing `baseline` to `init_system`'s `FinalRanker(baseline)` might fail if `__init__` doesn't take args.
# In Step 332, `__init__` takes NO arguments.
# So I must fix the `init_system` function below to valid code.

# Correcting the instantiation logic in this file content:
recommendations = ranker.rank(user_id, state)

# Display Grid
for item in recommendations:
    with st.container():
        c1, c2 = st.columns([1, 4])
        with c1:
            st.image("https://placehold.co/150x200?text=Movie", use_container_width=True)
        with c2:
            st.subheader(item.get("title"))
            st.caption(f"Category: {item.get('category')} | Score: {item.get('score', 0):.2f}")
            
            # Explanation Badge
            st.info(f"💡 {item.get('explanation')}")
            
            if item.get("type") == "intervention":
                st.button("Take a Break 🧘", key=f"break_{item['item_id']}")
            else:
                if st.button("Watch Now ▶️", key=f"watch_{item['item_id']}"):
                    st.toast(f"Started watching {item['title']}!")
        st.divider()

# Privacy/Debug Info
with st.expander("Debug: Internal User State"):
    st.json(state)
