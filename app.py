import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="ART Toxicity Surveillance",
    page_icon="🏥",
    layout="wide"
)

# Load data using safe path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'naija_art_clinic_clean.csv'))

st.title("🏥 ART Toxicity Surveillance Dashboard")
st.markdown("**Nigerian HIV Patient Risk Analysis** — Synthetic Cohort (n=500)")
st.markdown("---")

# Sidebar filters
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

# Filter data
df_filtered = df[
    (df['art_regimen'].isin(regimen_filter)) &
    (df['sex'].isin(sex_filter))
]

# Key metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", len(df_filtered))
with col2:
    renal_pct = (df_filtered['renal_risk_flag'] == 1).mean() * 100
    st.metric("Renal Risk", f"{renal_pct:.1f}%")
with col3:
    cv_pct = (df_filtered['cardio_risk_flag'] == 1).mean() * 100
    st.metric("CV Risk", f"{cv_pct:.1f}%")
with col4:
    qtc_pct = (df_filtered['severe_qtc_flag'] == 1).mean() * 100
    st.metric("Severe QTc Risk", f"{qtc_pct:.1f}%")

st.markdown("---")

# Risk distribution
st.subheader("Risk Distribution by ART Regimen")
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.countplot(data=df_filtered, x='art_regimen',
              hue='renal_risk_flag', ax=ax[0])
ax[0].set_title('Renal Risk by Regimen')
ax[0].set_xlabel('ART Regimen')
sns.countplot(data=df_filtered, x='art_regimen',
              hue='cardio_risk_flag', ax=ax[1])
ax[1].set_title('CV Risk by Regimen')
ax[1].set_xlabel('ART Regimen')
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")
st.write("TEST: Clinical section is loading!")

# Clinical Interpretation
st.subheader("Clinical Interpretation")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "**Renal Risk Pattern:**\n\n"
        "- TDF-containing regimens show higher renal toxicity\n"
        "- Mechanism: TDF accumulates in proximal tubular cells via OAT1/OAT3 transporters\n"
        "  leading to mitochondrial dysfunction and reduced eGFR\n"
        "- Action: Monitor eGFR every 3 months; consider switch to ABC if eGFR <60 mL/min"
    )

with col2:
    st.warning(
        "**CV Risk Pattern:**\n\n"
        "- TDF/3TC/DTG shows highest cardiovascular risk\n"
        "- Mechanism: DTG associated with weight gain and insulin resistance leading to\n"
        "  dyslipidemia and accelerated atherosclerosis\n"
        "- Action: Lifestyle counseling at each visit; consider lipid panel every 6 months"
    )

st.markdown("---")

# Clinical markers
st.subheader("Clinical Marker Distributions")
col1, col2 = st.columns(2)
with col1:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df_filtered, x='art_regimen', y='egfr_ml_min', ax=ax2)
    ax2.set_title('eGFR by Regimen')
    ax2.axhline(60, color='red', linestyle='--', label='CKD threshold')
    ax2.legend()
    plt.xticks(rotation=15)
    st.pyplot(fig2)
    plt.close()

with col2:
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df_filtered, x='art_regimen', y='bmi', ax=ax3)
    ax3.set_title('BMI by Regimen')
    ax3.axhline(30, color='red', linestyle='--', label='Obesity threshold')
    ax3.legend()
    plt.xticks(rotation=15)
    st.pyplot(fig3)
    plt.close()

    st.markdown("---")

# Clinical Decision Support
st.subheader("Clinical Decision Support")

# Calculate risk for each regimen
regimen_risks = df_filtered.groupby('art_regimen').agg({
    'renal_risk_flag': 'mean',
    'cardio_risk_flag': 'mean',
    'severe_qtc_flag': 'mean',
    'egfr_ml_min': 'median'
}).round(3)

st.dataframe(regimen_risks, use_container_width=True)

# Add recommendations
st.markdown("### Regimen-Specific Recommendations:")

recs = {
    'TDF/3TC/EFV': "High renal risk. Consider baseline eGFR before initiation. Switch to ABC if eGFR <60 mL/min or if significant proteinuria develops.",
    'TDF/3TC/DTG': "Highest combined renal and CV risk. Monitor weight, lipids, and eGFR every 3 months. Consider DTG-sparing regimen if metabolic complications arise.",
    'ABC/3TC/DTG': "Lower renal risk profile. Preferred for patients with baseline CKD or renal risk factors. Monitor for hypersensitivity reaction if HLA-B*5701 status unknown."
}

for regimen, rec in recs.items():
    if regimen in regimen_risks.index:
        st.info(f"**{regimen}:** {rec}")

st.markdown("---")

# Raw data
if st.checkbox("Show Raw Data"):
    st.dataframe(df_filtered)
    st.markdown(f"Showing {len(df_filtered)} patients")

st.markdown("---")
st.markdown(
    "**Data note:** This dashboard uses synthetic data "
    "modeled on Nigerian ART clinic parameters. "
    "Not for clinical use."
)