import os, json, numpy as np, pandas as pd, joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, roc_curve, precision_recall_curve,
    brier_score_loss)
from sklearn.calibration import calibration_curve

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
PROC = os.path.join(ROOT, "dataset", "processed")
REPORTS = os.path.join(ROOT, "reports")
FIGS = os.path.join(REPORTS, "figures")
SAVED = os.path.join(ROOT, "backend", "saved_models")
os.makedirs(FIGS, exist_ok=True)
os.makedirs(SAVED, exist_ok=True)

df = pd.read_csv(os.path.join(PROC, "diabetes_cleaned.csv"))
y = df["diabetes"].astype(int)
X = df.drop(columns=["diabetes", "SEQN"])

numeric_features = ["age","poverty_ratio","household_size","bmi","waist_cm","height_cm","weight_kg",
    "systolic_bp","diastolic_bp","pulse","sedentary_min_day","moderate_min_session",
    "vigorous_min_session","sleep_hours","alcohol_ever"]
categorical_features = ["sex","race_ethnicity","education","marital_status","smoking_status"]

for c in numeric_features + categorical_features:
    if c not in X.columns:
        X[c] = np.nan

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42)
print("Train/val/test sizes:", len(X_train), len(X_val), len(X_test))

def make_preprocessor():
    num = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    cat = Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([("num", num, numeric_features), ("cat", cat, categorical_features)])

def metrics_dict(y_true, y_pred, y_proba):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": float(tn/(tn+fp)) if (tn+fp)>0 else 0.0,
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "brier": float(brier_score_loss(y_true, y_proba)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }

param_grids = {
    "LogisticRegression": {
        "model__C": [0.01, 0.1, 1, 10],
        "model__class_weight": [None, "balanced"],
        "model__max_iter": [1000],
    },
    "DecisionTree": {
        "model__max_depth": [3, 5, 8, 12, None],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 5],
        "model__class_weight": [None, "balanced"],
    },
    "RandomForest": {
        "model__n_estimators": [100, 200],
        "model__max_depth": [5, 10, None],
        "model__min_samples_leaf": [1, 2, 4],
        "model__class_weight": [None, "balanced"],
    },
    "XGBoost": {
        "model__n_estimators": [100, 200],
        "model__max_depth": [3, 5, 7],
        "model__learning_rate": [0.05, 0.1],
        "model__subsample": [0.8, 1.0],
        "model__colsample_bytree": [0.8, 1.0],
        "model__scale_pos_weight": [1, 3, 5],
    },
    "SVM": {
        "model__C": [0.1, 1, 10],
        "model__gamma": ["scale", "auto"],
        "model__kernel": ["rbf"],
        "model__class_weight": [None, "balanced"],
        "model__probability": [True],
    },
    "GradientBoosting": {
        "model__n_estimators": [100, 200],
        "model__max_depth": [3, 5],
        "model__learning_rate": [0.05, 0.1],
        "model__subsample": [0.8, 1.0],
    },
}

estimators = {
    "LogisticRegression": LogisticRegression(random_state=42),
    "DecisionTree": DecisionTreeClassifier(random_state=42),
    "RandomForest": RandomForestClassifier(random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(random_state=42, eval_metric="logloss", n_jobs=-1, use_label_encoder=False),
    "SVM": SVC(random_state=42, probability=True),
    "GradientBoosting": GradientBoostingClassifier(random_state=42),
}

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
results = {}
best_pipelines = {}

for name in estimators:
    print("\n=== Training", name, "===")
    pipe = Pipeline([("preprocessor", make_preprocessor()), ("model", estimators[name])])
    search = RandomizedSearchCV(
        pipe, param_grids[name], n_iter=8, scoring="roc_auc", cv=cv,
        random_state=42, n_jobs=-1, refit=True, error_score="raise"
    )
    search.fit(X_train, y_train)
    best_pipelines[name] = search.best_estimator_
    val_proba = search.best_estimator_.predict_proba(X_val)[:, 1]
    val_pred = (val_proba >= 0.5).astype(int)
    m = metrics_dict(y_val, val_pred, val_proba)
    m["best_params"] = search.best_params_
    m["cv_best_score"] = float(search.best_score_)
    results[name] = m
    print(name, "val ROC-AUC:", m["roc_auc"], "recall:", m["recall"])

best_name = max(results, key=lambda n: results[n]["roc_auc"])
print("\nBest model:", best_name)
best_pipe = best_pipelines[best_name]

val_proba = best_pipe.predict_proba(X_val)[:, 1]
best_thr = 0.5
best_f1 = -1
for thr in np.arange(0.1, 0.91, 0.01):
    pred = (val_proba >= thr).astype(int)
    f1 = f1_score(y_val, pred, zero_division=0)
    if f1 > best_f1:
        best_f1 = f1
        best_thr = float(thr)
print("Tuned threshold:", best_thr, "val F1:", best_f1)

recall_thr = None
for thr in sorted(np.arange(0.05, 0.91, 0.01), reverse=True):
    pred = (val_proba >= thr).astype(int)
    if recall_score(y_val, pred, zero_division=0) >= 0.85:
        recall_thr = float(thr)
        break
print("Recall-oriented threshold (recall>=0.85):", recall_thr)

test_proba = best_pipe.predict_proba(X_test)[:, 1]
test_pred = (test_proba >= best_thr).astype(int)
test_metrics = metrics_dict(y_test, test_pred, test_proba)
# Save artifacts
preprocessor = best_pipe.named_steps["preprocessor"]
model = best_pipe.named_steps["model"]
joblib.dump(preprocessor, os.path.join(SAVED, "preprocessor.pkl"))
joblib.dump(model, os.path.join(SAVED, "model.pkl"))
joblib.dump(best_pipe, os.path.join(SAVED, "pipeline.pkl"))

feature_names = list(preprocessor.get_feature_names_out())
with open(os.path.join(SAVED, "feature_names.json"), "w") as f:
    json.dump(feature_names, f, indent=2)

metadata = {
    "model_name": best_name,
    "dataset": "NHANES August 2021-August 2023 (cycle 2021-2023)",
    "target_definition": "Current diabetes status: DIQ010==1 (doctor diagnosed) OR HbA1c>=6.5% OR fasting glucose>=126 mg/dL.",
    "n_train": int(len(X_train)),
    "n_val": int(len(X_val)),
    "n_test": int(len(X_test)),
    "threshold": best_thr,
    "recall_oriented_threshold": recall_thr,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "feature_names": feature_names,
    "best_params": results[best_name]["best_params"],
}
with open(os.path.join(SAVED, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

report = {
    "model_comparison_validation": {n: {k: v for k, v in results[n].items() if k not in ("best_params",)} for n in results},
    "best_model": best_name,
    "threshold": best_thr,
    "test_metrics": test_metrics,
}
with open(os.path.join(REPORTS, "model_evaluation.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)

fpr, tpr, _ = roc_curve(y_test, test_proba)
prec, rec, _ = precision_recall_curve(y_test, test_proba)
np.savez(os.path.join(REPORTS, "curves.npz"), fpr=fpr, tpr=tpr, precision=prec, recall=rec)

plt.figure(); plt.plot(fpr, tpr); plt.plot([0,1],[0,1],"--"); plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title(f"ROC - {best_name}")
plt.savefig(os.path.join(FIGS, "roc_curve.png")); plt.close()
plt.figure(); plt.plot(rec, prec); plt.xlabel("Recall"); plt.ylabel("Precision"); plt.title(f"PR - {best_name}")
plt.savefig(os.path.join(FIGS, "pr_curve.png")); plt.close()

cm = confusion_matrix(y_test, test_pred)
plt.figure(); plt.imshow(cm, cmap="Blues"); plt.title("Confusion Matrix")
for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i,j], ha="center", va="center")
plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.colorbar()
plt.savefig(os.path.join(FIGS, "confusion_matrix.png")); plt.close()

names = list(results.keys())
aucs = [results[n]["roc_auc"] for n in names]
plt.figure(figsize=(8,4)); plt.bar(names, aucs); plt.xticks(rotation=30, ha="right"); plt.ylabel("Val ROC-AUC"); plt.title("Model Comparison")
plt.tight_layout(); plt.savefig(os.path.join(FIGS, "model_comparison.png")); plt.close()

train_sizes, train_scores, val_scores = learning_curve(best_pipe, X_train, y_train, cv=3, scoring="roc_auc",
    train_sizes=np.linspace(0.2,1.0,5), n_jobs=-1)
lc = {"train_sizes": train_sizes.tolist(),
     "train_mean": train_scores.mean(axis=1).tolist(),
     "val_mean": val_scores.mean(axis=1).tolist()}
with open(os.path.join(REPORTS, "learning_curve.json"), "w") as f:
    json.dump(lc, f, indent=2)
plt.figure(); plt.plot(train_sizes, train_scores.mean(axis=1), label="train"); plt.plot(train_sizes, val_scores.mean(axis=1), label="val")
plt.xlabel("Training size"); plt.ylabel("ROC-AUC"); plt.legend(); plt.title("Learning Curve")
plt.savefig(os.path.join(FIGS, "learning_curve.png")); plt.close()

prob_true, prob_pred = calibration_curve(y_test, test_proba, n_bins=10)
cal = {"prob_true": prob_true.tolist(), "prob_pred": prob_pred.tolist()}
with open(os.path.join(REPORTS, "calibration.json"), "w") as f:
    json.dump(cal, f, indent=2)
plt.figure(); plt.plot(prob_pred, prob_true, marker="o"); plt.plot([0,1],[0,1],"--")
plt.xlabel("Mean predicted prob"); plt.ylabel("Fraction positives"); plt.title("Calibration")
plt.savefig(os.path.join(FIGS, "calibration.png")); plt.close()

sub = X_test.copy()
sub["y_true"] = y_test.values
sub["y_proba"] = test_proba
sub["y_pred"] = test_pred
subgroup = {}
for col in ["sex", "smoking_status"]:
    for g in sub[col].dropna().unique():
        mask = sub[col] == g
        if mask.sum() < 30: continue
        subgroup[f"{col}={g}"] = metrics_dict(sub.loc[mask,"y_true"], sub.loc[mask,"y_pred"], sub.loc[mask,"y_proba"])
sub["age_group"] = pd.cut(sub["age"], bins=[18,40,60,120], labels=["18-39","40-59","60+"])
for g in sub["age_group"].dropna().unique():
    mask = sub["age_group"] == g
    if mask.sum() < 30: continue
    subgroup[f"age_group={g}"] = metrics_dict(sub.loc[mask,"y_true"], sub.loc[mask,"y_pred"], sub.loc[mask,"y_proba"])
with open(os.path.join(REPORTS, "subgroup_performance.json"), "w") as f:
    json.dump(subgroup, f, indent=2, default=str)

try:
    import shap
    X_test_proc = preprocessor.transform(X_test)
    if any(k in best_name for k in ["XGBoost","RandomForest","Tree","Gradient"]):
        explainer = shap.TreeExplainer(model)
    elif "Logistic" in best_name:
        explainer = shap.LinearExplainer(model, preprocessor.transform(X_train.sample(200, random_state=42)))
    else:
        explainer = shap.KernelExplainer(model.predict_proba, preprocessor.transform(X_train.sample(100, random_state=42)))
    sample_idx = np.random.RandomState(42).choice(len(X_test), size=min(200, len(X_test)), replace=False)
    Xs = X_test.iloc[sample_idx]
    Xs_proc = preprocessor.transform(Xs)
    shap_vals = explainer.shap_values(Xs_proc)
    if isinstance(shap_vals, list):
        sv = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
    else:
        sv = shap_vals
    mean_abs = np.abs(sv).mean(axis=0)
    order = np.argsort(mean_abs)[::-1]
    shap_imp = [{"feature": feature_names[i], "importance": float(mean_abs[i])} for i in order]
    with open(os.path.join(SAVED, "shap_global_importance.json"), "w") as f:
        json.dump(shap_imp, f, indent=2)
    bg = X_train.sample(min(100, len(X_train)), random_state=42)
    bg.to_csv(os.path.join(SAVED, "background_sample.csv"), index=False)
    print("SHAP importance computed.")
except Exception as e:
    print("SHAP error:", repr(e))

print("\nDONE. Best:", best_name)
print("Test metrics:", json.dumps(test_metrics, indent=2))

test_metrics_05 = metrics_dict(y_test, (test_proba>=0.5).astype(int), test_proba)
