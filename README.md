# ART-Tox-Sentinel
# ART-Tox-Sentinel: HIV ART Toxicity Surveillance Dashboard

## Purpose
Prototype clinical decision support tool for monitoring renal, cardiovascular, and QTc toxicity 
in Nigerian HIV clinics on ART regimens.

## Architecture
- Synthetic cohort (n=500) modeled on Nigerian ART clinic parameters
- Streamlit dashboard for interactive risk stratification
- Physiology-informed risk flags & clinical recommendations

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py