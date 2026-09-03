# Project 2 — Causal Inference: Difference-in-Differences

## Overview

This project investigates whether the introduction of centre-based online exams was associated with improved candidate performance.

The project uses a synthetic observational dataset to demonstrate how a simple comparison can give a misleading impression when individuals self-select into different groups.

I use Difference-in-Differences (DiD), fixed effects and regression adjustment to investigate the effect of introducing online exam availability.

**Important:** The dataset is synthetic and was created specifically for this portfolio project. It does not represent real examination results or a real organisation.

---

## Research Question

> Did the introduction of online exam availability improve candidate performance?

A secondary question is:

> How much of the observed difference between online and paper candidates can be explained by selection and other differences between candidates and centres?

---

## Why Causal Inference?

A simple comparison showed that candidates taking online exams scored substantially higher than candidates taking paper exams.

However, this does not necessarily mean that online exams caused the higher marks.

The simulated data was designed so that stronger candidates were more likely to select online exams.

This creates **selection bias**.

Therefore, the analysis moves beyond a simple online-versus-paper comparison and uses a Difference-in-Differences approach.

---

## Data

The dataset contains simulated examination attempts across:

- 3,000 candidates
- 30 examination centres
- 2013–2022
- Multiple examination sessions
- Foundation, Intermediate and Advanced levels
- Online and paper delivery
- Candidate characteristics
- Previous performance
- Study hours
- Attendance
- Experience
- Centre-level online adoption

Twenty centres eventually adopted online exams, with adoption occurring between 2016 and 2020.

Ten centres never adopted online exams and provide the comparison group.

---

## Methodology

### 1. Unadjusted comparison

The first analysis compares average marks between online and paper candidates.

This produced an estimated difference of:

**+6.48 marks**

This is an observational association rather than a causal estimate.

The large difference may partly reflect the fact that stronger candidates were more likely to select online exams.

---

### 2. Difference-in-Differences

Centres introduced online exams at different times.

This allows the analysis to compare changes in performance at centres that introduced online exams with centres that never adopted them.

The basic two-way fixed-effects model controls for:

- Centre fixed effects
- Year fixed effects
- Online rollout

The estimated effect was:

**+0.75 marks**

---

### 3. DiD + Baseline Performance

The next model additionally controls for candidates' baseline performance before their centre introduced online exams.

This helps account for differences in previous candidate performance without using performance that may have occurred after treatment.

Estimated effect:

**+1.02 marks**

---

### 4. Full Adjusted DiD

The final model additionally controls for candidate characteristics including:

- Baseline performance
- Study hours
- Attendance
- Experience
- Degree level
- Training type
- Centre fixed effects
- Year fixed effects

Estimated effect:

**+1.06 marks**

---

## Results

| Model | Estimated Effect |
|---|---:|
| Unadjusted online vs paper | +6.48 |
| Two-way FE DiD | +0.75 |
| DiD + baseline performance | +1.02 |
| Full adjusted DiD | +1.06 |

The main finding is that the large **+6.48 mark observational difference** becomes substantially smaller after accounting for the structure of the observational data.

The adjusted DiD estimates are around **+1 mark**.

---

## Understanding the Difference

The simulation includes a deliberately specified **+1.5 mark effect for actually taking an online exam**.

However, the DiD treatment represents the **introduction of online availability at a centre**, rather than forcing every candidate to take an online exam.

After rollout, approximately **68% of attempts were online**, while approximately **32% remained paper**.

Therefore, the estimated effect of rollout can be smaller than the simulated +1.5 mark effect for an individual online exam.

The final adjusted rollout estimate of **+1.06 marks** is therefore consistent with the treatment not being received by every candidate.

---

## Parallel Trends

Difference-in-Differences relies on the assumption that treated and comparison groups would have followed similar trends in the absence of treatment.

I examined pre-treatment trends between adopting and never-adopting centres.

The formal pre-treatment trend test produced:

**p = 0.613**

This provides no statistically significant evidence of different pre-treatment trends.

However, a non-significant test does not prove that the parallel-trends assumption holds, so the pre-treatment graph is also considered when interpreting the results.

---

## Key Takeaway

The initial analysis suggested that online candidates performed **6.48 marks higher** than paper candidates.

However, this simple comparison did not account for selection into online exams.

After accounting for centre differences, changes over time, baseline performance and additional candidate characteristics, the estimated effect of online rollout was approximately **1 mark**.

This demonstrates why an observed difference between two groups should not automatically be interpreted as a causal effect.

---

## Limitations

### Synthetic data

The dataset is simulated and therefore does not establish a real-world effect.

### Selection into online exams

Candidates could choose between online and paper after online exams became available. This means the analysis is not estimating the effect of forcing candidates to take an online exam.

### Staggered adoption

Centres adopted online exams at different times, making the analysis more complex than a simple two-period Difference-in-Differences design.

### Parallel trends

The pre-treatment trends were examined visually and statistically, but the assumption cannot be proven from the available data.

### Treatment interpretation

The DiD estimate should be interpreted as the effect of **online rollout/availability**, rather than the pure effect of actually taking an online exam.

---

## Skills Demonstrated

- Causal inference
- Difference-in-Differences
- Observational data analysis
- Selection bias
- Fixed effects regression
- Regression adjustment
- Staggered treatment adoption
- Pre-treatment trend analysis
- Statistical interpretation
- Data visualisation
- Python

---

## Tools

- Python
- pandas
- NumPy
- statsmodels
- Matplotlib

---

## Project Structure

```text
project-2-causal-inference/
│
├── README.md
├── project2_causal_inference.py
├── project2_exam_attempts.csv
│
└── figures/
    ├── model_comparison.png
    └── pre_treatment_trends.png
