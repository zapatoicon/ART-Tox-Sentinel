import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="ART-Tox Sentinel",
    page_icon="🏥",
    layout="wide"
)

# Load data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'naija_art_clinic_clean.csv'))

# ── Title & intro ──────────────────────────────────────────────────────────────
st.title("🏥 ART-Tox Sentinel")
st.markdown(
    "A prototype clinical decision-support dashboard simulating organ toxicity "
    "surveillance for HIV patients on first-line antiretroviral therapy (ART) in "
    "Nigerian clinic settings. Designed for use by clinic data officers and HIV "
    "program researchers evaluating regimen-level toxicity patterns."
)

# ── Synthetic data banner ──────────────────────────────────────────────────────
st.warning(
    "⚠️ **Simulation only.** All data in this dashboard is fully synthetic, "
    "generated to reflect Nigerian ART clinic parameters (WHO Nigeria 2025 guidelines, "
    "CKD-EPI renal equations). This tool is not validated for clinical use and should "
    "not inform real patient management decisions."
)

st.markdown("---")

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.header("Filters")
regimen_filter = st.sidebar.multiselect(
    "Select ART Regimen:",
    options=df['art_regimen'].unique(),
    default=df['art_regimen'].unique()
)
sex_filter = st.sidebar.multiselect(
    "Select Sex:",
    options=df['sex'].unique(),
    default=df['sex'].unique()
)

df_filtered = df[
    (df['art_regimen'].isin(regimen_filter)) &
    (df['sex'].isin(sex_filter))
]

if df_filtered.empty:
    st.error("No patients match the selected filters. Adjust the sidebar selections.")
    st.stop()

# ── Key metrics ────────────────────────────────────────────────────────────────
st.subheader("Cohort Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Patients in View", len(df_filtered))
with col2:
    renal_pct = (df_filtered['renal_risk_flag'] == 1).mean() * 100
    st.metric("Renal Risk", f"{renal_pct:.1f}%", help="Creatinine >1.3 mg/dL, eGFR <60 mL/min, or proteinuria >30 mg/dL")
with col3:
    cv_pct = (df_filtered['cardio_risk_flag'] == 1).mean() * 100
    st.metric("CV Risk", f"{cv_pct:.1f}%", help="SBP >140 mmHg, DBP >90 mmHg, fasting glucose 100–125 mg/dL, or BMI >30")
with col4:
    qtc_pct = (df_filtered['severe_qtc_flag'] == 1).mean() * 100
    st.metric("Severe QTc Risk", f"{qtc_pct:.1f}%", help="QTc >450 ms (male) or >470 ms (female)")

st.markdown("---")

# ── Risk distribution plots ────────────────────────────────────────────────────
st.subheader("Risk Distribution by ART Regimen")
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

sns.countplot(data=df_filtered, x='art_regimen', hue='renal_risk_flag', ax=ax[0],
              palette={0: '#4C9BE8', 1: '#E84C4C', -1: '#AAAAAA'})
ax[0].set_title('Renal Risk Flag by Regimen')
ax[0].set_xlabel('ART Regimen')
ax[0].set_ylabel('Patient Count')
handles, _ = ax[0].get_legend_handles_labels()
ax[0].legend(handles, ['No Risk (0)', 'At Risk (1)', 'Unknown (-1)'], title='Renal Risk')

sns.countplot(data=df_filtered, x='art_regimen', hue='cardio_risk_flag', ax=ax[1],
              palette={0: '#4C9BE8', 1: '#E84C4C', -1: '#AAAAAA'})
ax[1].set_title('CV Risk Flag by Regimen')
ax[1].set_xlabel('ART Regimen')
ax[1].set_ylabel('Patient Count')
handles, _ = ax[1].get_legend_handles_labels()
ax[1].legend(handles, ['No Risk (0)', 'At Risk (1)', 'Unknown (-1)'], title='CV Risk')

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# Filter-responsive clinical interpretation 
st.subheader("Clinical Interpretation")

active_regimens = df_filtered['art_regimen'].unique().tolist()

tdf_regimens = [r for r in active_regimens if 'TDF' in r]
dtg_regimens = [r for r in active_regimens if 'DTG' in r]

col1, col2 = st.columns(2)

with col1:
    if tdf_regimens:
        st.info(
            "**Renal Risk Pattern — TDF-containing regimens:**\n\n"
            f"Active in view: {', '.join(tdf_regimens)}\n\n"
            "TDF accumulates in proximal tubular cells via OAT1/OAT3 transporters, "
            "causing mitochondrial dysfunction and progressive eGFR decline. "
            "Monitor eGFR every 3 months. Switch to ABC if eGFR falls below 60 mL/min "
            "or significant proteinuria develops."
        )
    else:
        st.success(
            "**Renal Risk Pattern:**\n\n"
            "No TDF-containing regimens in current view. "
            "Renal toxicity risk from TDF is not applicable to the selected cohort."
        )

with col2:
    if dtg_regimens:
        st.warning(
            "**CV Risk Pattern — DTG-containing regimens:**\n\n"
            f"Active in view: {', '.join(dtg_regimens)}\n\n"
            "DTG is associated with weight gain and insulin resistance, contributing to "
            "dyslipidemia and elevated cardiometabolic risk. "
            "Lifestyle counseling at every visit is recommended. "
            "Consider fasting lipid panel every 6 months for patients on DTG-based regimens."
        )
    else:
        st.success(
            "**CV Risk Pattern:**\n\n"
            "No DTG-containing regimens in current view. "
            "DTG-associated cardiometabolic risk is not applicable to the selected cohort."
        )

st.markdown("---")

# Clinical marker distributions 
st.subheader("Clinical Marker Distributions")
col1, col2 = st.columns(2)

with col1:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df_filtered, x='art_regimen', y='egfr_ml_min', ax=ax2)
    ax2.set_title('eGFR Distribution by Regimen')
    ax2.set_ylabel('eGFR (mL/min)')
    ax2.set_xlabel('ART Regimen')
    ax2.axhline(60, color='red', linestyle='--', label='CKD threshold (60 mL/min)')
    ax2.legend()
    plt.xticks(rotation=15)
    st.pyplot(fig2)
    plt.close()

with col2:
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df_filtered, x='art_regimen', y='bmi', ax=ax3)
    ax3.set_title('BMI Distribution by Regimen')
    ax3.set_ylabel('BMI (kg/m²)')
    ax3.set_xlabel('ART Regimen')
    ax3.axhline(30, color='red', linestyle='--', label='Obesity threshold (BMI 30)')
    ax3.legend()
    plt.xticks(rotation=15)
    st.pyplot(fig3)
    plt.close()

st.markdown("---")

# Clinical Decision Support table 
st.subheader("Clinical Decision Support")
st.markdown(
    "The table below summarises risk flag rates and median eGFR per regimen "
    "for the current filtered cohort. Risk flag values represent the **proportion "
    "of patients flagged as at-risk** (0 = no patient at risk, 1 = all patients at risk). "
    "Negative values (−1) indicate missing lab data."
)

regimen_risks = df_filtered.groupby('art_regimen').agg(
    renal_risk_proportion=('renal_risk_flag', lambda x: (x == 1).mean()),
    cardio_risk_proportion=('cardio_risk_flag', lambda x: (x == 1).mean()),
    severe_qtc_proportion=('severe_qtc_flag', lambda x: (x == 1).mean()),
    median_egfr_ml_min=('egfr_ml_min', 'median')
).round(3)

regimen_risks.columns = [
    'Renal Risk (proportion)',
    'CV Risk (proportion)',
    'Severe QTc Risk (proportion)',
    'Median eGFR (mL/min)'
]

st.dataframe(regimen_risks, use_container_width=True)

# Regimen-specific recommendations 
st.markdown("### Regimen-Specific Monitoring Recommendations")

recs = {
    'TDF/3TC/EFV': (
        "**Renal monitoring priority.** Obtain baseline eGFR before initiation. "
        "Recheck every 3 months. Switch to ABC/3TC if eGFR falls below 60 mL/min "
        "or significant proteinuria is confirmed."
    ),
    'TDF/3TC/DTG': (
        "**Highest combined renal and CV risk in this cohort.** Monitor eGFR, weight, "
        "and fasting lipids every 3 months. Consider DTG-sparing regimen if metabolic "
        "complications (obesity, dyslipidemia, impaired fasting glucose) arise."
    ),
    'ABC/3TC/DTG': (
        "**Preferred for patients with pre-existing CKD or renal risk factors.** "
        "Lower renal toxicity profile versus TDF-based regimens. Screen for HLA-B*5701 "
        "before initiation if status is unknown. Monitor weight and cardiometabolic "
        "markers given DTG component."
    ),
}

for regimen, rec in recs.items():
    if regimen in regimen_risks.index:
        st.info(f"**{regimen}:** {rec}")

st.markdown("---")

# Raw data toggle 
if st.checkbox("Show Raw Data"):
    st.dataframe(df_filtered)
    st.caption(f"Displaying {len(df_filtered)} synthetic patient records.")

st.markdown("---")
st.caption(
    "ART-Tox Sentinel v0.1 | Prototype — Simulation Only | "
    "Synthetic data modeled on Nigerian ART clinic parameters. "
    "Not validated for clinical deployment."
)