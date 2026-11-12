# PROJECT STATUS

## Status: COMPLETE (functional end-to-end)

## Completed Features

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| 1 | NHANES 2021–2023 data download from official CDC source | Done | 10 `.xpt` files downloaded & verified against codebooks |
| 2 | Cleaned analytic dataset (adults ≥18, target built) | Done | 8,065 rows, 22 columns, saved to `dataset/processed/diabetes_cleaned.csv` |
| 3 | Data quality report | Done | `reports/data_quality.json` |
| 4 | Target definition (leakage-safe) | Done | DIQ010=1 OR HbA1c≥6.5 OR glucose≥126; labs excluded from predictors |
| 5 | Preprocessing pipeline (Pipeline + ColumnTransformer) | Done | Fit on train only; median impute + scale numeric, most-frequent + one-hot categorical |
| 6 | 6 ML models compared (LR, DT, RF, XGB, SVM, GB) | Done | RandomizedSearchCV, stratified 3-fold CV |
| 7 | Final model: XGBoost | Done | Best validation ROC-AUC 0.820 |
| 8 | Threshold tuning on validation (recall ≥0.75) | Done | Threshold = 0.18 |
| 9 | Held-out test evaluation (never used for selection) | Done | ROC-AUC 0.815, Recall 0.743, Precision 0.348 |
| 10 | Model artifacts saved | Done | `backend/saved_models/` (model.pkl, preprocessor.pkl, pipeline.pkl, metadata.json, feature_names.json, shap_global_importance.json, background_sample.csv) |
| 11 | SHAP explainability (TreeExplainer) | Done | Global importance + individual explanations |
| 12 | Flask REST API (health, model-info, features, predict, explain) | Done | All 5 endpoints tested, JSON, CORS, input validation, error handling |
| 13 | Invalid input handling | Done | 400 responses with details for missing/range/category errors |
| 14 | React frontend (Vite + Tailwind + Router + Recharts + Lucide + Axios) | Done | Builds successfully |
| 15 | All 6 pages (Home, Assessment, Result, History, Insights, About) | Done | Connected to real backend via vite proxy |
| 16 | LocalStorage prediction history | Done | Add, view, delete individual, clear all, empty state |
| 17 | Light/dark mode | Done | Persisted in LocalStorage |
| 18 | Responsive design | Done | Desktop/tablet/mobile |
| 19 | README.md | Done | Comprehensive documentation |
| 20 | requirements.txt + .gitignore | Done | Backend + frontend dependency files |

## Test Results

### Backend API (all tested against running server)
- `GET /api/health` → 200, `{status: ok, model_loaded: true, preprocessor_loaded: true}` ✅
- `GET /api/model-info` → 200, real XGBoost metrics + SHAP importance (33 features) ✅
- `GET /api/features` → 200, 20 features with types/ranges/descriptions ✅
- `POST /api/predict` → 200, returns predicted_class, model_score, threshold, disclaimer ✅
- `POST /api/explain` → 200, returns base_value, top_features, top_positive, top_negative ✅
- Invalid input (missing field / out of range / bad category) → 400 with details ✅

### Integration (React → Flask → React)
- Frontend dev server on `localhost:5173`, proxy `/api` → `http://127.0.0.1:5000` ✅
- `/api/health` reachable through frontend proxy ✅
- Prediction + explanation flow end-to-end verified ✅

### Frontend build
- `npm run build` succeeds ✅

### Model consistency
- Saved preprocessor + model produce consistent predictions (verified via check scripts) ✅

## Known Limitations

- Cross-sectional status classification only; not a medical diagnosis or future-risk predictor.
- NHANES-specific; generalizes best to U.S. civilian noninstitutionalized adults.
- Missing data imputed (waist_cm ~27%, sleep_hours ~27%, blood pressure ~26-28%).
- Class imbalance retained (~15.8% prevalence); precision moderate (0.348).
- Threshold-dependent predicted class (threshold 0.18).
- SHAP = model contribution, not medical causation.
- Performance varies across subgroups (see `reports/subgroup_performance.json`).

## Remaining Tasks

- [ ] Optional: Evaluate generalization on CDC BRFSS 2023 (feature/target compatibility must be verified first).
- [ ] Optional: Add probability calibration (Platt/Isotonic) and document.
- [ ] Optional: Unit test suite (pytest) for backend validation/prediction.
- [ ] Optional: Deploy instructions for production (Gunicorn + static frontend serving).

## Test Commands (Windows PowerShell)

```powershell
# Backend health
Invoke-WebRequest http://127.0.0.1:5000/api/health -UseBasicParsing | Select-Object -ExpandProperty Content

# Model info
Invoke-WebRequest http://127.0.0.1:5000/api/model-info -UseBasicParsing | Select-Object -ExpandProperty Content

# Predict
$body = @{age=55; sex='male'; race_ethnicity=3; education=4; marital_status=1; poverty_ratio=2.5; household_size=2; bmi=32.0; waist_cm=105.0; height_cm=175.0; weight_kg=98.0; systolic_bp=135.0; diastolic_bp=85.0; pulse=78.0; sedentary_min_day=480.0; moderate_min_session=30.0; vigorous_min_session=0.0; sleep_hours=7.0; smoking_status='former'; alcohol_ever=1} | ConvertTo-Json
Invoke-WebRequest http://127.0.0.1:5000/api/predict -Method POST -Body $body -ContentType 'application/json' | Select-Object -ExpandProperty Content

# Frontend
Invoke-WebRequest http://localhost:5173 -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```
