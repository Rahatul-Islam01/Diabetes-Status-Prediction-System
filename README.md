# Diabetes Status Prediction System

A complete, end-to-end machine learning system that estimates whether a person **currently has diabetes** based on selected health-related features, using real **NHANES 2021–2023** data.

> ⚠️ **Important distinction:** This is a **cross-sectional diabetes status classification** project. It estimates current diabetes status, it is **NOT** a future diabetes prediction system and **NOT** a medical diagnosis tool.

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Main Features](#main-features)
3. [Technology Stack](#technology-stack)
4. [Dataset Source](#dataset-source)
5. [Target Variable Definition](#target-variable-definition)
6. [Preprocessing Methodology](#preprocessing-methodology)
7. [Machine Learning Methodology](#machine-learning-methodology)
8. [Model Evaluation Results](#model-evaluation-results)
9. [SHAP Explainability](#shap-explainability)
10. [API Documentation](#api-documentation)
11. [Installation Instructions](#installation-instructions)
12. [Running the Application](#running-the-application)
13. [Limitations and Disclaimer](#limitations-and-disclaimer)

## 1. Project Overview

The system estimates current diabetes status from cross-sectional health data. It combines:
- Real NHANES 2021–2023 data downloaded from the official CDC source
- Six trained and compared ML models
- XGBoost selected as the final model (best validation ROC-AUC)
- Threshold tuned on validation data for a screening-oriented recall/sensitivity trade-off
- SHAP explainability for global and individual predictions
- A Flask REST API backend
- A modern React (Vite + Tailwind CSS) frontend dashboard
- LocalStorage-based prediction history (no external database)

## 2. Main Features

- **Home / Dashboard**: Project overview, prediction count, recent history, model performance summary
- **Diabetes Assessment**: Validated form with only model-real features, units, descriptions, loading state
- **Prediction Result**: Predicted status, model-estimated score, decision threshold, SHAP explanation, medical disclaimer
- **Prediction History**: LocalStorage history with date/time, inputs, predicted status, score, delete/clear
- **Model Insights**: Real backend evaluation metrics, model comparison, ROC/PR curves, confusion matrix, SHAP importance
- **About & Disclaimer**: Project objective, dataset source, methodology, limitations, medical disclaimer
- Light/dark mode, fully responsive design

## 3. Technology Stack

### Frontend
- React JS, Vite, Tailwind CSS, React Router DOM, Recharts, Lucide React, Axios

### Backend
- Python, Flask, Flask-CORS

### Machine Learning
- Pandas, NumPy, Scikit-learn, XGBoost, SHAP, Matplotlib

### Storage
- LocalStorage (prediction history and user preferences). No external database.

## 4. Dataset Source

**Official source:** CDC NHANES Continuous NHANES, August 2021–August 2023 cycle  
https://wwwn.cdc.gov/Nchs/Nhanes/ContinuousNhanes/default.aspx?Cycle=2021-2023

Data files used (official `.xpt` from CDC):
| File | Description |
|------|-------------|
| DEMO_L | Demographics |
| BMX_L | Body measures |
| BPXO_L | Blood pressure |
| GHB_L | Glycohemoglobin / HbA1c |
| GLU_L | Fasting glucose |
| DIQ_L | Diabetes questionnaire |
| PAQ_L | Physical activity |
| SMQ_L | Smoking |
| ALQ_L | Alcohol use |
| SLQ_L | Sleep |

All files were downloaded directly from `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/<NAME>.xpt`.

Variable names, types, units, and missing-value codes were verified against the official codebooks before processing.

### Dataset download script
`backend/data/download_nhanes.py` downloads all files from the official CDC source.

## 5. Target Variable Definition

Current diabetes status (`diabetes`):
- **1 (positive)** if: `DIQ010 == 1`, OR `LBXGH (HbA1c) >= 6.5%`, OR `LBXGLU (fasting glucose) >= 126 mg/dL`
- **0 (negative)** otherwise (including prediabetes/borderline `DIQ010 == 3` unless labs indicate diabetes)

Unknown/refused/missing cases with no lab evidence are excluded from the analytic sample.

**Data leakage prevention:** HbA1c and fasting glucose are used ONLY to construct the target and are EXCLUDED from predictors. Preprocessing is fit only on training data. No oversampling before train/test split.

Final analytic sample: **8,065 adults (age ≥ 18)**, class distribution: 6,791 negative / 1,274 positive (~15.8% prevalence).

## 6. Preprocessing Methodology

A reproducible scikit-learn `Pipeline` + `ColumnTransformer`:
- Missing codes → NaN; duplicate detection on `SEQN`; invalid values → missing
- Numeric: median imputation + `StandardScaler`
- Categorical: most-frequent imputation + `OneHotEncoder(handle_unknown='ignore')`
- Fit only on training data; applied to validation/test via fitted transformer

### Numeric features
`age`, `poverty_ratio`, `household_size`, `bmi`, `waist_cm`, `height_cm`, `weight_kg`, `systolic_bp`, `diastolic_bp`, `pulse`, `sedentary_min_day`, `moderate_min_session`, `vigorous_min_session`, `sleep_hours`, `alcohol_ever`

### Categorical features
`sex`, `race_ethnicity`, `education`, `marital_status`, `smoking_status`

### Splits (stratified, random_state=42)
- Train: 5,645 (70%) · Validation: 1,210 (15%) · Test: 1,210 (15%, held out)

Cleaned dataset: `dataset/processed/diabetes_cleaned.csv`  
Data quality report: `reports/data_quality.json`

## 7. Machine Learning Methodology

Models compared (stratified CV, RandomizedSearchCV, random_state=42):
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. **XGBoost** ← selected
5. Support Vector Machine
6. Gradient Boosting

Selection criterion: validation **ROC-AUC** (screening objective prioritizes recall/sensitivity). Final threshold (0.18) chosen on validation data to maximize F1 while keeping recall ≥ 0.75.

The final model was evaluated once on the untouched test set.

## 8. Model Evaluation Results (held-out test set)

| Metric | Value |
|--------|-------|
| Model | XGBoost |
| Accuracy | 0.740 |
| Precision | 0.348 |
| Recall / Sensitivity | 0.743 |
| Specificity | 0.739 |
| F1-score | 0.474 |
| ROC-AUC | 0.815 |
| PR-AUC | 0.449 |
| Brier score | 0.107 |
| Threshold | 0.18 |
| Confusion Matrix (TN/FP/FN/TP) | 753 / 266 / 49 / 142 |

For a screening application, recall is prioritized (0.743) to reduce false negatives, accepting a moderate false-positive rate.

Reports:
- `reports/model_evaluation.json` — full metrics + model comparison
- `reports/figures/roc_curve.png`, `pr_curve.png`, `confusion_matrix.png`, `model_comparison.png`, `learning_curve.png`, `calibration.png`
- `reports/learning_curve.json`, `reports/calibration.json`, `reports/subgroup_performance.json`

All metrics come from actual experiments on the held-out test set. No fabrication.

## 9. SHAP Explainability

Integrated with the selected XGBoost model using `shap.TreeExplainer`.
- Global feature importance (mean absolute SHAP)
- Individual prediction explanations (top positive / negative contributing features)
- SHAP values are shown as contribution to the model score, **not** medical causation

Top global drivers: age, waist_cm, pulse, systolic_bp, diastolic_bp.
SHAP importance saved to `backend/saved_models/shap_global_importance.json`.

## 10. API Documentation

Base URL: `http://127.0.0.1:5000/api` (dev) — configure via `VITE_API_BASE_URL` in frontend.

### GET /api/health
Backend and model status.
```json
{ "status": "ok", "model_loaded": true, "preprocessor_loaded": true }
```

### GET /api/model-info
Model name, dataset info, actual test metrics, threshold, SHAP importance.

### GET /api/features
Required input fields, types, valid ranges, descriptions.

### POST /api/predict
Validated input → predicted class, model score, threshold, disclaimer.

### POST /api/explain
Validated input → SHAP-based explanation (base value, top features, top positive/negative).

All endpoints return JSON with proper error handling and HTTP status codes (400 for invalid input, 500 for server errors).

## 11. Installation Instructions

### Prerequisites
- Python 3.11 (py / python)
- Node.js + npm (v20+)
- Windows PowerShell

### Step 1: Create Python virtual environment
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2: Install backend dependencies
```powershell
pip install -r backend\requirements.txt
```

### Step 3: Download NHANES data (optional; already included in dataset/raw)
```powershell
python backend\data\download_nhanes.py
```

### Step 4: Build cleaned dataset + train model
```powershell
python backend\preprocessing\build_dataset.py
python backend\training\train_model.py
```

### Step 5: Install frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

## 12. Running the Application

### Terminal A — Backend
```powershell
.venv\Scripts\Activate.ps1
cd backend
python app.py
```
Backend runs on `http://127.0.0.1:5000`.

### Terminal B — Frontend
```powershell
cd frontend
npm run dev
```
Frontend runs on `http://localhost:5173`.

### Verify
- Backend health: `http://127.0.0.1:5000/api/health`
- Frontend: `http://localhost:5173`

### Production build (frontend)
```powershell
cd frontend
npm run build
# output in frontend/dist
```

## 13. Limitations and Disclaimer

- **Cross-sectional only:** estimates current status, does not predict future diabetes.
- **Not a medical diagnosis:** consult a qualified healthcare professional.
- **NHANES-specific:** results generalize best to the U.S. civilian noninstitutionalized adult population.
- **Missing data:** some features have missingness (e.g., waist_cm ~27%, sleep_hours ~27%); imputation used.
- **Demographic bias:** performance varies across age/sex/smoking subgroups (see `reports/subgroup_performance.json`).
- **Threshold-dependent:** predicted class changes with the decision threshold (0.18).
- **SHAP ≠ causation:** SHAP values indicate feature contribution to the model score, not medical causation.
- **No oversampling:** class imbalance retained (~15.8% prevalence); precision is moderate.


## Project Structure

```
diabetes_predictor/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── config.py           # Feature schema & metadata
│   ├── requirements.txt
│   ├── data/
│   │   └── download_nhanes.py
│   ├── preprocessing/
│   │   └── build_dataset.py
│   ├── training/
│   │   └── train_model.py
│   ├── explainability/
│   │   └── shap_explainer.py
│   ├── saved_models/       # model.pkl, preprocessor.pkl, metadata.json, shap_global_importance.json
│   └── utils/
│       └── validation.py
├── frontend/
│   ├── src/
│   │   ├── pages/          # Home, Assessment, Result, History, Insights, About
│   │   ├── layouts/
│   │   ├── services/       # api.js (axios)
│   │   ├── hooks/          # useTheme.jsx
│   │   └── utils/          # history.js (LocalStorage)
│   ├── package.json
│   └── vite.config.js
├── dataset/
│   ├── raw/                # NHANES .xpt files
│   └── processed/          # diabetes_cleaned.csv
├── reports/
│   ├── model_evaluation.json
│   ├── data_quality.json
│   ├── learning_curve.json
│   ├── calibration.json
│   ├── subgroup_performance.json
│   └── figures/
├── notebooks/
├── README.md
├── PROJECT_STATUS.md
├── .gitignore
└── backend\requirements.txt
```

