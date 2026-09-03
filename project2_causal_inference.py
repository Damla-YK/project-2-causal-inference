# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 15:23:35 2026

@author: Yagmda
"""

import numpy as np
import pandas as pd


#Step 1 — Set up the simulation

np.random.seed(42)

n_candidates = 3000

years = range(2013, 2023)

sessions = ["March", "June", "September", "December"]

n_exams = 18

online_effect = 1.5

#Step 2 — Create our candidates

candidate_ids = np.arange(1, n_candidates + 1)

candidates = pd.DataFrame({
    "candidate_id": candidate_ids,
    "ability": np.random.normal(0, 1, n_candidates)
})

#test
print(candidates.head())
print(candidates["ability"].describe())

#Step 3 — Create centres
# Create centres with staggered rollout
# 20 centres eventually adopt online
# 10 centres remain paper-only
# The 10 never-adopting centres become our comparison group for DiD.

n_centres = 30
centre_ids = np.arange(1, n_centres + 1)

adoption_years = np.array(
    [2016] * 4 +
    [2017] * 4 +
    [2018] * 4 +
    [2019] * 4 +
    [2020] * 4 +
    [np.nan] * 10,
    dtype=float
)

np.random.shuffle(adoption_years)

centres = pd.DataFrame({
    "centre_id": centre_ids,
    "online_adoption_year": adoption_years
})

centres["ever_adopts"] = centres["online_adoption_year"].notna().astype(int)

print(centres)
print("\nAdoption year counts:")
print(centres["online_adoption_year"].value_counts(dropna=False).sort_index())
#test
print(centres.head())
print(centres["online_adoption_year"].value_counts().sort_index())

#Step 4 — Create the exams
exam_names = [f"Exam_{i:02d}" for i in range(1, n_exams + 1)]

exam_levels = (
    ["Foundation"] * 6
    + ["Intermediate"] * 6
    + ["Advanced"] * 6
)

# Relative difficulty within each exam level:
# negative = easier, positive = harder
exam_difficulty = np.concatenate([
    np.random.normal(0, 0.4, 6),  # Foundation
    np.random.normal(0, 0.4, 6),  # Intermediate
    np.random.normal(0, 0.4, 6)   # Advanced
])

exams = pd.DataFrame({
    "exam_id": exam_names,
    "exam_level": exam_levels,
    "exam_difficulty": exam_difficulty
})

print(exams)

#Step 5 — Create our exam sessions
exam_sessions = pd.DataFrame([
    {
        "year": year,
        "session": session
    }
    for year in years
    for session in sessions
])

print(exam_sessions.head(10))
print(exam_sessions.tail())
print(len(exam_sessions))

#Step 6 — Assign candidates to centres
candidates["centre_id"] = np.random.choice(
    centre_ids,
    size=n_candidates
)

candidates = candidates.merge(
    centres,
    on="centre_id",
    how="left"
)

print(candidates.head())

#test
print(candidates["centre_id"].nunique())

print(candidates["online_adoption_year"].value_counts().sort_index())

#Step 7 — Give candidates their background characteristics
countries = ["UK", "Ireland", "UAE", "Singapore", "South Africa"]

candidates["country"] = np.random.choice(
    countries,
    size=n_candidates,
    p=[0.40, 0.10, 0.15, 0.15, 0.20]
)

candidates["degree_level"] = np.random.choice(
    ["None", "Undergraduate", "Postgraduate"],
    size=n_candidates,
    p=[0.20, 0.60, 0.20]
)

candidates["training_type"] = np.random.choice(
    ["Self-study", "Training provider"],
    size=n_candidates,
    p=[0.45, 0.55]
)

candidates["experience_years"] = np.round(
    np.random.exponential(scale=3, size=n_candidates),
    1
)

print(candidates.head())

#Step 8 — Create study behaviour
candidates["study_hours_per_week"] = np.clip(
    10 + 4 * candidates["ability"] + np.random.normal(0, 4, n_candidates),
    2,
    30
)

candidates["attendance_rate"] = np.clip(
    80 + 5 * candidates["ability"] + np.random.normal(0, 8, n_candidates),
    50,
    100
)

print(
    candidates[
        [
            "candidate_id",
            "ability",
            "study_hours_per_week",
            "attendance_rate"
        ]
    ].head(10)
)

#Step 9 — Create exam attempts
candidates["number_of_attempts"] = np.random.randint(
    1,
    9,
    size=n_candidates
)

print(
    candidates["number_of_attempts"].describe()
)

#Step 10 — Create exam attempts
attempt_records = []

for _, candidate in candidates.iterrows():
    chosen_sessions = np.random.choice(
        len(exam_sessions),
        size=candidate["number_of_attempts"],
        replace=False
    )

    for session_idx in chosen_sessions:
        session = exam_sessions.iloc[session_idx]

        exam = exams.sample(1).iloc[0]

        attempt_records.append({
            "candidate_id": candidate["candidate_id"],
            "centre_id": candidate["centre_id"],
            "year": session["year"],
            "session": session["session"],
            "exam_id": exam["exam_id"],
            "exam_level": exam["exam_level"],
            "exam_difficulty": exam["exam_difficulty"]
        })

attempts = pd.DataFrame(attempt_records)

print(attempts.head(10))
print(attempts.shape)

#Step 11 — Determine online eligibility
attempts = attempts.merge(
    centres,
    on="centre_id",
    how="left"
)

attempts["online_available"] = (
    (attempts["ever_adopts"] == 1) &
    (attempts["year"] >= attempts["online_adoption_year"])
)
print(
    attempts[
        [
            "candidate_id",
            "centre_id",
            "year",
            "online_adoption_year",
            "online_available"
        ]
    ].head(10)
)

#Step 12 — Create self-selection
attempts = attempts.merge(
    candidates[
        [
            "candidate_id",
            "ability",
            "degree_level",
            "training_type",
            "experience_years",
            "study_hours_per_week",
            "attendance_rate"
        ]
    ],
    on="candidate_id",
    how="left"
)

selection_score = (
    -1.0
    + 1.2 * attempts["ability"]
    + 0.04 * attempts["study_hours_per_week"]
    + 0.02 * attempts["attendance_rate"]
)

online_probability = 1 / (1 + np.exp(-selection_score))

random_draw = np.random.random(len(attempts))

attempts["delivery_mode"] = np.where(
    attempts["online_available"] &
    (random_draw < online_probability),
    "Online",
    "Paper"
)

attempts = attempts.drop(
    columns=["online_available"]
)

#check
print(
    attempts["delivery_mode"].value_counts(normalize=True)
)

print(
    attempts.groupby("delivery_mode")["ability"].mean()
)

#Step 13 — Generate previous performance

#check
print(attempts["delivery_mode"].value_counts())
print(
    attempts.groupby("delivery_mode")["ability"].agg(
        ["mean", "std", "count"]
    )
)

level_effect = {
    "Foundation": 5,
    "Intermediate": 0,
    "Advanced": -5
}

attempts["base_mark"] = (
    55
    + 10 * attempts["ability"]
    + attempts["exam_level"].map(level_effect)
    - 5 * attempts["exam_difficulty"]
    + 0.5 * attempts["experience_years"]
    + 0.4 * attempts["study_hours_per_week"]
    + 0.08 * (attempts["attendance_rate"] - 80)
)

attempts["marks"] = (
    attempts["base_mark"]
    + np.where(
        attempts["delivery_mode"] == "Online",
        online_effect,
        0
    )
    + np.random.normal(0, 7, len(attempts))
)

attempts["marks"] = attempts["marks"].clip(0, 100)
attempts["pass_fail"] = np.where(
    attempts["marks"] >= 50,
    "Pass",
    "Fail"
)

session_order = {
    "March": 1,
    "June": 2,
    "September": 3,
    "December": 4
}

attempts["session_order"] = attempts["session"].map(session_order)
attempts = attempts.sort_values(
    ["candidate_id", "year", "session_order"]
    ).reset_index(drop=True)

attempts = attempts.drop(columns="session_order")

#check
print(
    attempts.groupby("delivery_mode")["marks"].agg(
        ["mean", "std", "count"]
    )
)
print(
    attempts.groupby("delivery_mode")["pass_fail"].value_counts(
        normalize=True
    )
)


# Step 14 — Create baseline performance before online rollout

# For each candidate, calculate their average mark
# before their centre introduced online exams.

attempts["baseline_average_mark"] = np.nan

for candidate_id, group in attempts.groupby("candidate_id"):
    
    adoption_year = group["online_adoption_year"].iloc[0]
    
    if pd.notna(adoption_year):
        baseline = group.loc[
            group["year"] < adoption_year,
            "marks"
        ].mean()
    else:
        # Never-adopting candidates use the pre-2016 period
        baseline = group.loc[
            group["year"] < 2016,
            "marks"
        ].mean()
    
    attempts.loc[
        attempts["candidate_id"] == candidate_id,
        "baseline_average_mark"
    ] = baseline

print(
    attempts[
        [
            "candidate_id",
            "year",
            "online_adoption_year",
            "marks",
            "baseline_average_mark"
        ]
    ].head(15)
)
#Step 15 — Historical pass rate
attempts["historical_pass_rate"] = (
    attempts.groupby("candidate_id")["pass_fail"]
    .transform(
        lambda x: (
            x.shift()
            .eq("Pass")
            .where(x.shift().notna())
            .expanding()
            .mean()
        )
    )
)#Don't use the current exam result to calculate the candidate's history.

#check
print(
    attempts[
        [
            "candidate_id",
            "year",
            "session",
            "marks",
            "pass_fail",
            "baseline_average_mark",
            "historical_pass_rate"
        ]
    ].head(15)
)

#Step 16 — Check our historical variables

print(
    attempts[
        ["baseline_average_mark", "historical_pass_rate"]
    ].isna().sum()
)

print(
    attempts["baseline_average_mark"].notna().sum()
)

print(
    attempts["historical_pass_rate"].notna().sum()
)

print(
    attempts[
        ["baseline_average_mark", "historical_pass_rate"]
    ].describe()
)

#Step 17 — Let's investigate our selection bias
print(
    attempts.groupby("delivery_mode")[
        "baseline_average_mark"
    ].agg(["mean", "std", "count"])
)
print(
    attempts.groupby("delivery_mode")[
        "historical_pass_rate"
    ].mean()
)

#Step 18 — The DiD setup

# DiD treatment variables

attempts["treated"] = attempts["ever_adopts"]

attempts["post"] = (
    (attempts["ever_adopts"] == 1) &
    (attempts["year"] >= attempts["online_adoption_year"])
).astype(int)

#check
print("\nOnline uptake after rollout:")
print(
    attempts.loc[attempts["post"] == 1, "delivery_mode"]
    .value_counts(normalize=True)
)


#check
print(
    attempts.groupby(
        ["year", "post"]
    ).size()
)
print(
    attempts.groupby("post")["marks"].mean()
)

print("\nDiD variable check:")
print(
    attempts.groupby(["treated", "post"])
    .size()
    .reset_index(name="n_attempts")
)

#Don't interpret the second result as a treatment effect yet! staggered adoption

#DiD 
# calculate the four means
did_means = (
    attempts
    .groupby(["treated", "post"])["marks"]
    .mean()
)

print("\nDiD group means:")
print(did_means)
#We cannot yet calculate the basic 2×2 DiD from these three numbers, because our comparison centres need both a pre and post period.

#1 - regression-based DiD
# Difference-in-Differences regression

import statsmodels.formula.api as smf

did_model = smf.ols(
    "marks ~ treated + post + treated:post",
    data=attempts
).fit()

print(did_model.summary())
#Did marks change more after online rollout in adopting centres than they did otherwise?

# Two-way fixed-effects DiD
# Centre effects control for permanent differences between centres
# Year effects control for changes affecting everyone over time

did_fe_model = smf.ols(
    "marks ~ post + C(centre_id) + C(year)",
    data=attempts
).fit()

print("\nTwo-way fixed-effects DiD:")
print(did_fe_model.summary())

#plot average marks by year
import matplotlib.pyplot as plt

year_trends = (
    attempts
    .groupby(["year", "treated"])["marks"]
    .mean()
    .reset_index()
)

for group, data in year_trends.groupby("treated"):
    label = "Eventually adopts" if group == 1 else "Never adopts"
    plt.plot(data["year"], data["marks"], marker="o", label=label)

plt.xlabel("Year")
plt.ylabel("Average marks")
plt.title("Average Marks Over Time by Treatment Group")
plt.legend()
plt.show() #not parallel
#A DiD estimate isn't automatically causal just because we ran a regression. We need to examine whether its assumptions are plausible.
#DiD relies on the parallel trends assumption

# Check pre-treatment trends (2013-2015)

pre_trends = (
    attempts[attempts["year"] <= 2015]
    .groupby(["year", "treated"])["marks"]
    .mean()
    .reset_index()
)

print("\nPre-treatment trends:")
print(pre_trends)

# Formal pre-trend check

pre_period = attempts[attempts["year"] <= 2015].copy()

pretrend_model = smf.ols(
    "marks ~ year + treated + year:treated",
    data=pre_period
).fit(
    cov_type="cluster",
    cov_kwds={"groups": pre_period["centre_id"]}
)

print("\nFormal pre-trend check:")
print(pretrend_model.summary())

#Regression adjustment
# Step 1, run an adjusted regression
# DiD with baseline performance adjustment

did_adjusted = smf.ols(
   "marks ~ post + baseline_average_mark + C(centre_id) + C(year)",
    data=attempts.dropna(subset=["baseline_average_mark"])
).fit(
    cov_type="cluster",
    cov_kwds={"groups": attempts.dropna(
        subset=["baseline_average_mark"]
    )["centre_id"]}
)

print("\nAdjusted DiD:")
print(did_adjusted.summary())

print("\nAverage baseline performance by delivery mode:")
print(
    attempts.groupby("delivery_mode")["baseline_average_mark"].mean()
)

# DiD with additional candidate characteristics

did_full = smf.ols(
    """
    marks ~ post
    + baseline_average_mark
    + study_hours_per_week
    + attendance_rate
    + experience_years
    + C(degree_level)
    + C(training_type)
    + C(centre_id)
    + C(year)
    """,
    data=attempts.dropna(subset=["baseline_average_mark"])
).fit(
    cov_type="cluster",
    cov_kwds={"groups": attempts.dropna(
        subset=["baseline_average_mark"]
    )["centre_id"]}
)

print("\nFull adjusted DiD:")
print(did_full.summary())

# I used categorical fixed effects for centre and year to control for time-invariant differences between 
# centres and common year-specific shocks."

# Compare our DiD estimates

print("\nDiD estimate comparison:")
print("Two-way FE DiD:              ", round(did_fe_model.params["post"], 3))
print("Adjusted for prior marks:    ", round(did_adjusted.params["post"], 3))
print("Full adjusted model:         ", round(did_full.params["post"], 3))
print("True simulated effect:       ", online_effect)

# Final model comparison table

results = pd.DataFrame({
    "Model": [
        "Unadjusted online vs paper",
        "Two-way FE DiD",
        "DiD + baseline performance",
        "Full adjusted DiD"
    ],
    "Estimated_effect": [
        attempts.loc[
            attempts["delivery_mode"] == "Online", "marks"
        ].mean()
        -
        attempts.loc[
            attempts["delivery_mode"] == "Paper", "marks"
        ].mean(),

        did_fe_model.params["post"],
        did_adjusted.params["post"],
        did_full.params["post"]
    ]
})

results["Estimated_effect"] = results["Estimated_effect"].round(3)

print("\nFinal results:")
print(results)

#visual
import matplotlib.pyplot as plt

plt.figure(figsize=(9, 5))

plt.bar(
    results["Model"],
    results["Estimated_effect"]
)

plt.axhline(
    online_effect,
    linestyle="--",
    label="True simulated effect"
)

plt.ylabel("Estimated effect on marks")
plt.title("Online Exam Effect Across Model Specifications")
plt.xticks(rotation=20, ha="right")
plt.legend()
plt.tight_layout()
plt.show()

# Final results table

#1
results["Estimated_effect"] = results["Estimated_effect"].round(2)

print("\nFINAL RESULTS")
print(results.to_string(index=False))

#2 save
# Save final simulated dataset

attempts.to_csv(
    "project2_exam_attempts.csv",
    index=False
)

print("\nDataset saved as project2_exam_attempts.csv")

#graph
pre_trends = (
    attempts[attempts["year"] <= 2015]
    .groupby(["year", "treated"])["marks"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8, 5))

for group, data in pre_trends.groupby("treated"):
    label = "Eventually adopts" if group == 1 else "Never adopts"
    plt.plot(
        data["year"],
        data["marks"],
        marker="o",
        label=label
    )

plt.xticks([2013, 2014, 2015])
plt.xlabel("Year")
plt.ylabel("Average mark")
plt.title("Pre-Treatment Trends: Eventually Adopting vs Never Adopting Centres")
plt.legend()
plt.tight_layout()
plt.show()