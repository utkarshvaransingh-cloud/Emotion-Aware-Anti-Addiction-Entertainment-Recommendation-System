# -*- coding: utf-8 -*-
"""
Script to run the corrected notebook cells for evaluation and analysis.
This fixes issues with parameter naming and context object handling.
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Add to path and change directory
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

print(f"Project root: {project_root}")

# Import standard libraries
import pandas as pd
import numpy as np

# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette('husl')

# Ensure outputs directory exists
os.makedirs(os.path.join(project_root, 'outputs'), exist_ok=True)

# Import project modules
from src.data_ingestion import load_raw_data
from src.anti_addiction import compute_fatigue_score, get_intervention
from src.state import get_user_state
from src.feature_schema import ContextFeatures
from src.recommender.final_ranker import FinalRanker

# Load data (returns a dictionary)
data = load_raw_data()
users = data['users']
items = data['items']
interactions = data['interactions']

# Initialize ranker
ranker = FinalRanker()

print("\n[OK] All libraries and modules loaded!")
print(f"[OK] Data loaded: {len(users)} users, {len(items)} movies, {len(interactions)} interactions")

# ============================================================
# SECTION 1: Anti-Addiction Fatigue Analysis
# ============================================================
print("\n" + "=" * 60)
print("[SECTION 1] Anti-Addiction Fatigue Analysis")
print("=" * 60)

test_sessions = [0, 30, 60, 90, 120, 150, 180]
fatigue_scores = []

for session_min in test_sessions:
    # Use correct parameter names from compute_fatigue_score
    score = compute_fatigue_score(
        session_duration_minutes=session_min,
        repetition_index=0.3,
        cumulative_daily_minutes=session_min,
        time_of_day_penalty=0.5
    )
    intervention = get_intervention(score)
    fatigue_scores.append(score)
    
    status = '[HIGH]' if intervention == 'hard_break' else '[MED]' if intervention == 'soft_break' else '[LOW]' if intervention == 'diversify' else '[OK]'
    print(f"{status} Session: {session_min:3d} min -> Fatigue: {score:.2f} -> {intervention or 'none'}")

# Visualize fatigue curve
plt.figure(figsize=(10, 6))
plt.plot(test_sessions, fatigue_scores, 'o-', linewidth=2, markersize=10, color='#2563eb', label='Fatigue Score')

plt.axhline(y=0.4, color='#fbbf24', linestyle='--', linewidth=2, label='Diversify (0.4)')
plt.axhline(y=0.6, color='#f97316', linestyle='--', linewidth=2, label='Soft Break (0.6)')
plt.axhline(y=0.84, color='#ef4444', linestyle='--', linewidth=2, label='Hard Break (0.84)')

plt.axhspan(0.84, 1.0, alpha=0.2, color='red')
plt.axhspan(0.6, 0.84, alpha=0.2, color='orange')
plt.axhspan(0.4, 0.6, alpha=0.2, color='yellow')

plt.xlabel('Session Duration (minutes)', fontsize=12)
plt.ylabel('Fatigue Score', fontsize=12)
plt.title('Fatigue Score vs Session Duration', fontsize=14, fontweight='bold')
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(project_root, 'outputs', 'fatigue_curve.png'), dpi=150)
plt.close()
print("\n[SAVED] Fatigue curve saved to outputs/fatigue_curve.png")

# ============================================================
# SECTION 2: Simulating 1000 Random User Sessions
# ============================================================
print("\n" + "=" * 60)
print("[SECTION 2] Simulating 1000 Random User Sessions...")
print("=" * 60)

# Use 'none' instead of None for dictionary key
interventions = {'none': 0, 'diversify': 0, 'soft_break': 0, 'hard_break': 0}

np.random.seed(42)
for _ in range(1000):
    session = np.random.randint(0, 200)
    repetition = np.random.uniform(0, 1)
    daily = np.random.randint(0, 300)
    night = np.random.uniform(0, 1)
    
    score = compute_fatigue_score(session, repetition, daily, night)
    intervention = get_intervention(score)
    # Convert None to 'none' for dictionary key
    key = intervention if intervention is not None else 'none'
    interventions[key] += 1

print("\nIntervention Distribution:")
for name, count in interventions.items():
    pct = count / 10
    bar = "#" * int(pct / 2)
    print(f"  {name:12s}: {bar:25s} {pct:.1f}%")

plt.figure(figsize=(10, 5))
colors = ['#10b981', '#fbbf24', '#f97316', '#ef4444']
bars = plt.bar(interventions.keys(), interventions.values(), color=colors, edgecolor='white', linewidth=2)
plt.title('Intervention Distribution (1000 Sessions)', fontsize=14, fontweight='bold')
plt.ylabel('Count')
plt.xlabel('Intervention Type')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 15, f'{height/10:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(project_root, 'outputs', 'intervention_distribution.png'), dpi=150)
plt.close()
print("\n[SAVED] Intervention distribution saved to outputs/intervention_distribution.png")

# ============================================================
# SECTION 3: Diversity Analysis Across Moods
# ============================================================
def calculate_diversity(recommendations):
    genres = [r['category'] for r in recommendations]
    unique_genres = len(set(genres))
    return unique_genres / len(genres) if genres else 0

print("\n" + "=" * 60)
print("[SECTION 3] Diversity Analysis Across Moods")
print("=" * 60)

# Create ContextFeatures object (not a dictionary)
context = ContextFeatures(
    time_of_day="evening", 
    device_type="browser", 
    location="home", 
    session_minutes=30
)

diversity_results = []

for mood in ["happy", "sad", "bored", "anxious", "neutral"]:
    state = get_user_state("u_1", context, {"label": mood})
    recs = ranker.rank("u_1", state)[:10]
    diversity = calculate_diversity(recs)
    diversity_results.append({"mood": mood, "diversity": diversity})
    bar = "#" * int(diversity * 20)
    print(f"{mood:8s}: {bar:20s} {diversity:.2f}")

print(f"\n[RESULT] Average Diversity: {np.mean([r['diversity'] for r in diversity_results]):.2f}")

# ============================================================
# SECTION 4: Full Recommendation Pipeline
# ============================================================
print("\n" + "=" * 60)
print("[SECTION 4] Full Recommendation Pipeline")
print("=" * 60)

for mood in ["happy", "sad", "bored"]:
    print(f"\n{'='*60}")
    print(f"MOOD: {mood.upper()}")
    print('='*60)
    
    state = get_user_state("u_1", context, {"label": mood})
    recommendations = ranker.rank("u_1", state, genre_filter=None)[:5]
    
    for i, rec in enumerate(recommendations, 1):
        title = rec['title'][:30] if len(rec['title']) > 30 else rec['title']
        print(f"  {i}. {title:30s} | {rec['category']:10s} | Score: {rec['score']:.2f}")

# ============================================================
# SECTION 5: System Summary
# ============================================================
print("\n" + "=" * 60)
print("[SECTION 5] SYSTEM SUMMARY")
print("=" * 60)
print(f"  Total Movies:        {len(items)}")
print(f"  Total Users:         {len(users)}")
print(f"  Genres Supported:    {len(items['category'].unique())}")
print(f"  Moods Supported:     5 (happy, sad, bored, anxious, neutral)")
print(f"  Intervention Types:  4 (none, diversify, soft_break, hard_break)")
print("=" * 60)

print("\n" + "="*60)
print("SCRIPT EXECUTION COMPLETE!")
print("="*60)
print("\nAll sections executed successfully.")
print("Thank you for reviewing this project!")
