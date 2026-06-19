# ART-Tox Sentinel

**A proof-of-concept clinical decision-support dashboard that simulates ART toxicity risk monitoring for HIV patients in Nigerian clinic settings, using rule-based logic applied to synthetic laboratory data.**

🔗 **Live demo:** [art-tox-sentinel.streamlit.app](https://art-tox-sentinel.streamlit.app)

---

## 1. Problem Context

Tenofovir (TDF) and dolutegravir (DTG)-based regimens are widely used as first-line antiretroviral therapy (ART) in Nigeria, in line with WHO treatment guidelines. TDF is associated with nephrotoxicity risk through proximal renal tubular accumulation, while DTG has been linked to weight gain and downstream cardiometabolic effects in several published cohorts.

Routine monitoring of these toxicities, such as periodic eGFR, blood pressure, and metabolic panel tracking, varies across clinical settings, and many lower-resource facilities lack structured tools for flagging at-risk patients from routine lab data. This creates a gap between the clinical knowledge of what to monitor and the practical infrastructure to monitor it systematically.

ART-Tox Sentinel explores what a lightweight, rule-based monitoring layer could look like if built on top of routine lab indicators already collected in many ART programs.

---

## 2. System Overview

ART-Tox Sentinel is a Streamlit dashboard that ingests patient-level lab and demographic data and applies explainable, threshold-based rules to flag renal risk, cardiovascular risk, severe QTc prolongation risk, and combined (dual-organ) risk.

The dashboard follows a four-stage workflow:

**Input** → **Processing** → **Risk Output** → **Interpretation**

1. **Input:** Patient records (demographics, ART regimen, lab values)
2. **Processing:** Rule-based risk logic applied per patient using WHO-aligned thresholds
3. **Risk Output:** Patients flagged by risk category
4. **Interpretation:** Regimen-level summaries and monitoring recommendations

Users can filter by ART regimen and sex, view cohort-level risk metrics, inspect a high-risk patient surveillance list, and review regimen-specific monitoring guidance.

---

## 3. Method / System Design

### Synthetic Data Generation

The dataset (n = 500 simulated patients) was generated programmatically to reflect realistic Nigerian ART clinic demographics and lab value distributions, informed by:

- WHO Nigeria ART guidelines
- Nigerian HIV/AIDS Indicator and Impact Survey (NAIIS) demographic proportions
- Published Nigerian cohort literature on TDF-associated nephrotoxicity and DTG-associated weight gain

eGFR is calculated using the **CKD-EPI 2009 equation** (race-free formulation). The dataset includes mechanism-based missing data (not random) to simulate data quality gaps typical of rural clinic settings, such as missing BP, creatinine, or ECG readings.

### Risk Logic Engine

All risk flags are rule-based and fully explainable:

| Flag | Logic |
|---|---|
| Renal Risk | Creatinine > 1.3 mg/dL, OR eGFR < 60 mL/min, OR urine protein > 30 mg/dL |
| CV Risk | SBP > 140 mmHg, OR DBP > 90 mmHg, OR fasting glucose 100–125 mg/dL, OR BMI > 30 |
| Severe QTc Risk | QTc > 450 ms (male), QTc > 470 ms (female) |
| Combined Risk | Renal Risk AND CV Risk both active |
| Unknown (−1) | Relevant lab data missing |

No machine learning is used in the deployed dashboard. This is an intentional design choice for a v0.1 prototype: rule-based logic is fully auditable and explainable to a clinical reviewer, which matters more than predictive sophistication at this stage.

### Dashboard Visualization

Built with Streamlit, pandas, matplotlib, and seaborn. Risk distributions, eGFR/BMI boxplots against clinical thresholds, and a filterable high-risk patient table are rendered dynamically based on user-selected filters.

---

## 4. Output / Features

- **Cohort Overview** : patient count and risk prevalence metrics, filterable by regimen and sex
- **Risk Distribution Charts** : renal and CV risk flag counts grouped by ART regimen
- **Clinical Interpretation** : filter-responsive explanation of risk mechanisms for regimens currently in view
- **Clinical Marker Distributions** : eGFR and BMI boxplots with clinical threshold lines
- **Clinical Decision Support Table** : regimen-level risk proportions and median eGFR
- **Regimen-Specific Monitoring Recommendations** : plain-language guidance per regimen
- **High-Risk Patient Surveillance List** : individual patients flagged for combined renal + CV risk, sorted by eGFR
- **Risk Flag Logic Panel** : plain-English explanation of every flag's trigger conditions

---

## 5. Limitations

- All data is **fully synthetic**. No real patient data was used at any stage.
- Risk thresholds are rule-based, not derived from statistical modeling or machine learning.
- The tool has not been validated against any real clinical dataset or deployed in a clinical environment.
- Missing-data handling is limited to high-risk patient imputation only; it does not represent a full missing-data strategy.
- The model does not account for ART duration, adherence, comorbidities, or concurrent medications, all of which affect real-world toxicity risk.
- This is a **v0.1 proof-of-concept**, not a clinical or production system.

---

## Tech Stack

Python · Streamlit · pandas · NumPy · matplotlib · seaborn

## Running Locally

```bash
git clone https://github.com/zapatoicon/ART-Tox-Sentinel.git
cd ART-Tox-Sentinel
pip install -r requirements.txt
streamlit run app.py
```

## Author

Ajibola — Physiology (Cardiovascular & Respiratory) background, data annotation and health analytics.

---

*This tool is a research and portfolio prototype. It is not validated for clinical use and must not inform real patient management decisions.*