# generate_naija_art_data.py
# Production-grade synthetic data generator for ART toxicity surveillance
# Incorporates engineering best practices: dependency chains, derived variables, clinical credibility

import pandas as pd
import numpy as np

np.random.seed(42)
n = 500  # Realistic cohort size for a Nigerian clinic

# ============================================
# BASE PATIENT DEMOGRAPHICS (Nigeria reality)
# ============================================
data = {
    'patient_id': [f'NGA_{i:04d}' for i in range(1, n+1)],
    'age': np.random.randint(25, 65, n),
    'sex': np.random.choice(['F', 'M'], n, p=[0.62, 0.38]),  # 62% women (Nigeria ART data)
    'weight_kg': np.random.normal(68, 12, n),
    'height_cm': np.random.normal(165, 8, n),
}

# ============================================
# ART REGIMENS (Nigeria 2025 WHO Guidelines)
# ============================================
regimens = ['TDF/3TC/DTG', 'ABC/3TC/DTG', 'TDF/3TC/EFV']
data['art_regimen'] = np.random.choice(regimens, n, p=[0.65, 0.25, 0.10])

df = pd.DataFrame(data)

# ============================================
# RENAL MARKERS 
# ============================================
base_creatinine = np.random.normal(0.9, 0.2, n)
base_creatinine = np.clip(base_creatinine, 0.5, 2.0)

mask_tdf_dtg = df['art_regimen'] == 'TDF/3TC/DTG'
mask_tdf_efv = df['art_regimen'] == 'TDF/3TC/EFV'

df['creatinine_mg_dl'] = base_creatinine
df.loc[mask_tdf_dtg, 'creatinine_mg_dl'] += np.random.normal(0.25, 0.15, mask_tdf_dtg.sum())
df.loc[mask_tdf_efv, 'creatinine_mg_dl'] += np.random.normal(0.20, 0.12, mask_tdf_efv.sum())
df['creatinine_mg_dl'] = np.clip(df['creatinine_mg_dl'], 0.5, 5.0)

# CKD-EPI simplified formula (age + sex + creatinine)
# eGFR = 141 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.209 × 0.993^Age × sex_factor
kappa = np.where(df['sex'] == 'F', 0.7, 0.9)  # κ = 0.7 for females, 0.9 for males
alpha = np.where(df['sex'] == 'F', -0.329, -0.411)  # α = -0.329 for females, -0.411 for males
scr_kappa_ratio = df['creatinine_mg_dl'] / kappa

egfr_base = 141 * np.minimum(scr_kappa_ratio, 1)**alpha * np.maximum(scr_kappa_ratio, 1)**(-1.209)
egfr_base *= 0.993 ** df['age']  # Age adjustment
egfr_base *= np.where(df['sex'] == 'F', 1.018, 1.0)  # Female adjustment

df['egfr_ml_min'] = np.clip(egfr_base, 15, 150)

# Proteinuria
df['urine_protein_mg_dl'] = np.random.normal(15, 10, n)
df.loc[mask_tdf_dtg, 'urine_protein_mg_dl'] += np.random.normal(25, 15, mask_tdf_dtg.sum())
df['urine_protein_mg_dl'] = np.clip(df['urine_protein_mg_dl'], 5, 200)

# ============================================
# CARDIOMETABOLIC MARKERS (DTG effects)
# ============================================
df['current_weight_kg'] = df['weight_kg'].copy()
df.loc[mask_tdf_dtg, 'current_weight_kg'] += np.random.normal(4.5, 2.0, mask_tdf_dtg.sum())
mask_abc_dtg = df['art_regimen'] == 'ABC/3TC/DTG'
df.loc[mask_abc_dtg, 'current_weight_kg'] += np.random.normal(4.0, 1.8, mask_abc_dtg.sum())
df['current_weight_kg'] = np.clip(df['current_weight_kg'], 45, 120)

# STORE BMI EXPLICITLY 
df['bmi'] = df['current_weight_kg'] / ((df['height_cm'] / 100) ** 2)

# Blood Pressure
df['systolic_bp'] = np.random.normal(125, 18, n)
df.loc[mask_tdf_dtg, 'systolic_bp'] += np.random.normal(8, 5, mask_tdf_dtg.sum())
df['diastolic_bp'] = df['systolic_bp'] * 0.62 + np.random.normal(0, 5, n)

# Fasting Glucose
df['fasting_glucose_mg_dl'] = np.random.normal(95, 15, n)
df.loc[mask_tdf_dtg, 'fasting_glucose_mg_dl'] += np.random.normal(12, 8, mask_tdf_dtg.sum())

# QT Interval ( CONCEPTUAL FIX: Link to metabolic syndrome, not direct DTG effect)
df['qt_interval_ms'] = np.random.normal(400, 25, n)
df['heart_rate_bpm'] = np.random.normal(78, 10, n)

# CORRECTED: QTc prolongation linked to BMI/metabolic syndrome (not direct DTG)
# High BMI → insulin resistance → sympathetic overdrive → QTc prolongation
bmi_effect = np.where(df['bmi'] > 30, np.random.normal(12, 8, n), 0)  # BMI >30 adds QTc prolongation
df['qtc_ms'] = (df['qt_interval_ms'] / np.sqrt(60 / df['heart_rate_bpm'])) + bmi_effect

# ============================================
# CLINICAL FLAGS (WHO thresholds)
# ============================================
df['cd4_count'] = np.random.normal(320, 120, n)
df['last_visit_months_ago'] = np.random.choice([3, 6, 9, 12], n, p=[0.4, 0.35, 0.15, 0.10])

# ============================================
# INTRODUCING NIGERIAN CLINIC REALITY (MESSY DATA)
# ============================================

#  MECHANISM-BASED MISSINGNESS (not random)
# Rural clinics: more missing labs
rural_probability = 0.4  # 40% of cohort from rural settings
is_rural = np.random.rand(n) < rural_probability

# Urban clinics: better equipment, fewer missing values
missing_bp_idx = np.where(is_rural & (np.random.rand(n) < 0.5))[0]  # 50% of rural miss BP
df.loc[missing_bp_idx, 'systolic_bp'] = np.nan
df.loc[missing_bp_idx, 'diastolic_bp'] = np.nan

missing_creat_idx = np.where(is_rural & (np.random.rand(n) < 0.45))[0]  # 45% of rural miss creatinine
df.loc[missing_creat_idx, 'creatinine_mg_dl'] = np.nan
df.loc[missing_creat_idx, 'egfr_ml_min'] = np.nan

missing_qtc_idx = np.where(is_rural & (np.random.rand(n) < 0.6))[0]  # 60% of rural miss ECG
df.loc[missing_qtc_idx, 'qtc_ms'] = np.nan

# High-risk patients more likely to have labs done (healthcare bias)
high_risk_mask = (df['bmi'] > 30) | (df['systolic_bp'] > 140) | (df['creatinine_mg_dl'] > 1.3)

# 1. Identify high-risk patients with missing creatinine
missing_cr_high_risk = high_risk_mask & df['creatinine_mg_dl'].isna()

# 2. Impute Creatinine FIRST (simulate a lab result since they are high risk)
# We assume if they are high risk, their creatinine is likely elevated (e.g., 1.4 +/- 0.2)
if missing_cr_high_risk.sum() > 0:
    df.loc[missing_cr_high_risk, 'creatinine_mg_dl'] = np.random.normal(1.4, 0.2, missing_cr_high_risk.sum())
    
    # 3. NOW recalculate eGFR for those specific rows (because we now have creatinine values)
    # We need to re-run the CKD-EPI logic for these specific rows
    kappa_fix = np.where(df.loc[missing_cr_high_risk, 'sex'] == 'F', 0.7, 0.9)
    alpha_fix = np.where(df.loc[missing_cr_high_risk, 'sex'] == 'F', -0.329, -0.411)
    scr_kappa_fix = df.loc[missing_cr_high_risk, 'creatinine_mg_dl'] / kappa_fix

    egfr_fix = 141 * np.minimum(scr_kappa_fix, 1)**alpha_fix * np.maximum(scr_kappa_fix, 1)**(-1.209)
    egfr_fix *= 0.993 ** df.loc[missing_cr_high_risk, 'age']
    egfr_fix *= np.where(df.loc[missing_cr_high_risk, 'sex'] == 'F', 1.018, 1.0)

    df.loc[missing_cr_high_risk, 'egfr_ml_min'] = np.clip(egfr_fix, 15, 150)

# 6% duplicate patient IDs
duplicate_idx = np.random.choice(df.index, int(0.06*n), replace=False)
for idx in duplicate_idx:
    df.loc[len(df)] = df.loc[idx]

# Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ============================================
#  RISK FLAGS GENERATED AFTER MISSINGNESS ( critical insight!)
# ============================================

# RENAL RISK FLAGS (WHO Nigeria 2025)
df['renal_risk_flag'] = (
    (df['creatinine_mg_dl'] > 1.3) | 
    (df['egfr_ml_min'] < 60) | 
    (df['urine_protein_mg_dl'] > 30)
).astype(int)

# Missing renal markers = unknown risk (flag as -1 for uncertainty)
df.loc[df['creatinine_mg_dl'].isna() & df['egfr_ml_min'].isna(), 'renal_risk_flag'] = -1

# CARDIOMETABOLIC RISK FLAGS (DTG-linked via metabolic syndrome)
df['cardio_risk_flag'] = (
    (df['systolic_bp'] > 140) | 
    (df['diastolic_bp'] > 90) |
    ((df['fasting_glucose_mg_dl'] >= 100) & (df['fasting_glucose_mg_dl'] < 126)) |
    (df['bmi'] > 30)
).astype(int)

# Missing cardio markers = unknown risk
df.loc[df['systolic_bp'].isna() & df['bmi'].isna(), 'cardio_risk_flag'] = -1

# SEVERE QTc FLAG (Critical for high-BMI patients)
df['severe_qtc_flag'] = (
    ((df['sex'] == 'M') & (df['qtc_ms'] > 450)) |
    ((df['sex'] == 'F') & (df['qtc_ms'] > 470))
).astype(int)

df.loc[df['qtc_ms'].isna(), 'severe_qtc_flag'] = -1  # Unknown if QTc missing

df['critical_qtc_flag'] = (df['qtc_ms'] > 500).astype(int)
df.loc[df['qtc_ms'].isna(), 'critical_qtc_flag'] = -1

# ============================================
# SAVE TO CSV
# ============================================
df.to_csv('naija_art_clinic_messy.csv', index=False)

print("="*70)
print("✅ PRODUCTION-GRADE SYNTHETIC DATA GENERATED")
print("="*70)
print(f"Total patients: {len(df)} (including duplicates)")
print(f"\nART Regimens:")
print(f"  TDF/3TC/DTG (nephro + CV risk): {sum(df['art_regimen'] == 'TDF/3TC/DTG')}")
print(f"  ABC/3TC/DTG (CV risk only): {sum(df['art_regimen'] == 'ABC/3TC/DTG')}")
print(f"  TDF/3TC/EFV (nephro risk): {sum(df['art_regimen'] == 'TDF/3TC/EFV')}")
print(f"\n⚠️ Risk Flags (Generated AFTER Missingness):")
print(f"  Renal Risk: {sum(df['renal_risk_flag'] == 1)} | Unknown: {sum(df['renal_risk_flag'] == -1)}")
print(f"  Cardiometabolic Risk: {sum(df['cardio_risk_flag'] == 1)} | Unknown: {sum(df['cardio_risk_flag'] == -1)}")
print(f"  Severe QTc Risk: {sum(df['severe_qtc_flag'] == 1)} | Unknown: {sum(df['severe_qtc_flag'] == -1)}")
print(f"  Critical QTc (>500ms): {sum(df['critical_qtc_flag'] == 1)} | Unknown: {sum(df['critical_qtc_flag'] == -1)}")
print(f"\n⚠️ Data Quality Issues (Mechanism-Based Missingness):")
print(f"  Missing BP: {df['systolic_bp'].isnull().sum()} ({df['systolic_bp'].isnull().sum()/len(df):.0%})")
print(f"  Missing Creatinine: {df['creatinine_mg_dl'].isnull().sum()} ({df['creatinine_mg_dl'].isnull().sum()/len(df):.0%})")
print(f"  Missing QTc: {df['qtc_ms'].isnull().sum()} ({df['qtc_ms'].isnull().sum()/len(df):.0%})")
print(f"  Duplicate IDs: {df.duplicated(subset=['patient_id']).sum()}")
print(f"\n💾 Saved to: naija_art_clinic_messy.csv")
print("="*70)