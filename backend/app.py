import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import FEATURE_SCHEMA, ALL_FEATURES, DISPLAY_NAMES
    from utils.validation import validate_input
except Exception:
    from backend.config import FEATURE_SCHEMA, ALL_FEATURES, DISPLAY_NAMES
    from backend.utils.validation import validate_input

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAVED = os.path.join(ROOT, "backend", "saved_models")

app = Flask(__name__)
CORS(app)

# Load artifacts
import joblib
preprocessor = joblib.load(os.path.join(SAVED, "preprocessor.pkl"))
model = joblib.load(os.path.join(SAVED, "model.pkl"))
metadata = json.load(open(os.path.join(SAVED, "metadata.json")))
threshold = float(metadata["threshold"])

# SHAP service (lazy)
_shap_service = None
def get_shap_service():
    global _shap_service
    if _shap_service is None:
        try:
            from explainability.shap_explainer import ShapExplainerService
        except Exception:
            from backend.explainability.shap_explainer import ShapExplainerService
        _shap_service = ShapExplainerService()
    return _shap_service

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None, "preprocessor_loaded": preprocessor is not None})

@app.route("/api/model-info", methods=["GET"])
def model_info():
    import json as _j
    eval_path = os.path.join(ROOT, "reports", "model_evaluation.json")
    eval_data = {}
    if os.path.exists(eval_path):
        eval_data = _j.load(open(eval_path))
    # shap global importance
    shap_path = os.path.join(SAVED, "shap_global_importance.json")
    shap_imp = []
    if os.path.exists(shap_path):
        shap_imp = _j.load(open(shap_path))
    return jsonify({
        "model_name": metadata["model_name"],
        "dataset": metadata["dataset"],
        "target_definition": metadata["target_definition"],
        "threshold": threshold,
        "recall_oriented_threshold": metadata.get("recall_oriented_threshold"),
        "n_train": metadata["n_train"],
        "n_val": metadata["n_val"],
        "n_test": metadata["n_test"],
        "metrics": eval_data.get("test_metrics", {}),
        "model_comparison": eval_data.get("model_comparison_validation", {}),
        "shap_global_importance": shap_imp,
        "numeric_features": metadata["numeric_features"],
        "categorical_features": metadata["categorical_features"],
    })

@app.route("/api/features", methods=["GET"])
def features():
    out = []
    for name, schema in FEATURE_SCHEMA.items():
        item = {"name": name, "display_name": DISPLAY_NAMES.get(name, name), **schema}
        out.append(item)
    return jsonify({"features": out})

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    df, errors = validate_input(data)
    if errors:
        return jsonify({"error": "Invalid input", "details": errors}), 400
    try:
        X_proc = preprocessor.transform(df)
        proba = float(model.predict_proba(X_proc)[0, 1])
        pred_class = int(proba >= threshold)
        status = "Diabetes (positive screen)" if pred_class == 1 else "No diabetes (negative screen)"
        return jsonify({
            "predicted_class": pred_class,
            "diabetes_status": status,
            "model_score": proba,
            "threshold": threshold,
            "above_threshold": bool(proba >= threshold),
            "disclaimer": "This model estimates current diabetes status from cross-sectional data. It is not a medical diagnosis and the score is not a guaranteed personal probability."
        })
    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500

@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.get_json(silent=True)
    df, errors = validate_input(data)
    if errors:
        return jsonify({"error": "Invalid input", "details": errors}), 400
    try:
        svc = get_shap_service()
        result = svc.explain(df)
        # attach display names
        for item in result.get("top_features", []):
            item["display_name"] = DISPLAY_NAMES.get(item["feature"], item["feature"])
        for item in result.get("top_positive", []):
            item["display_name"] = DISPLAY_NAMES.get(item["feature"], item["feature"])
        for item in result.get("top_negative", []):
            item["display_name"] = DISPLAY_NAMES.get(item["feature"], item["feature"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Explanation failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
