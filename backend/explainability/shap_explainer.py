import os, json, numpy as np, pandas as pd, joblib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAVED = os.path.join(ROOT, "saved_models")

class ShapExplainerService:
    def __init__(self):
        self.preprocessor = joblib.load(os.path.join(SAVED, "preprocessor.pkl"))
        self.model = joblib.load(os.path.join(SAVED, "model.pkl"))
        self.feature_names = json.load(open(os.path.join(SAVED, "feature_names.json")))
        self.metadata = json.load(open(os.path.join(SAVED, "metadata.json")))
        self.original_features = self.metadata["numeric_features"] + self.metadata["categorical_features"]
        # map transformed -> original
        self.transformed_to_original = []
        for fn in self.feature_names:
            orig = None
            for f in self.original_features:
                if fn == f"num__{f}" or fn.startswith(f"cat__{f}_") or fn == f"cat__{f}":
                    orig = f
                    break
            if orig is None:
                # fallback: strip prefix
                name = fn.split("__", 1)[-1]
                for f in self.original_features:
                    if name.startswith(f):
                        orig = f
                        break
            self.transformed_to_original.append(orig if orig else fn)
        # build explainer
        import shap
        model_name = self.metadata["model_name"]
        if any(k in model_name for k in ["XGBoost", "RandomForest", "Tree", "Gradient"]):
            self.explainer = shap.TreeExplainer(self.model)
            self.kind = "tree"
        elif "Logistic" in model_name:
            bg = pd.read_csv(os.path.join(SAVED, "background_sample.csv")) if os.path.exists(os.path.join(SAVED, "background_sample.csv")) else None
            if bg is not None:
                pass
            self.explainer = shap.LinearExplainer(self.model, self.preprocessor.transform(
                pd.read_csv(os.path.join(SAVED, "background_sample.csv"))[self.original_features] if os.path.exists(os.path.join(SAVED, "background_sample.csv")) else None
            ))
            self.kind = "linear"
        else:
            bg_df = pd.read_csv(os.path.join(SAVED, "background_sample.csv"))[self.original_features]
            self.explainer = shap.KernelExplainer(self.model.predict_proba, self.preprocessor.transform(bg_df))
            self.kind = "kernel"
        # expected value
        ev = self.explainer.expected_value
        if isinstance(ev, (list, np.ndarray)):
            self.base_value = float(ev[1]) if len(ev) > 1 else float(ev[0])
        else:
            self.base_value = float(ev)

    def explain(self, df):
        X_proc = self.preprocessor.transform(df)
        import shap
        sv = self.explainer.shap_values(X_proc)
        if isinstance(sv, list):
            sv = sv[1] if len(sv) > 1 else sv[0]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[:, :, 1]
        row_sv = sv[0]
        # aggregate to original features
        agg = {}
        for i, f in enumerate(self.original_features):
            agg[f] = 0.0
        for idx, orig in enumerate(self.transformed_to_original):
            if orig in agg:
                agg[orig] += float(row_sv[idx])
            else:
                agg[orig] = agg.get(orig, 0.0) + float(row_sv[idx])
        # input values
        input_vals = {f: (None if pd.isna(df.iloc[0][f]) else (float(df.iloc[0][f]) if isinstance(df.iloc[0][f], (np.integer, np.floating)) else df.iloc[0][f])) for f in self.original_features}
        items = []
        for f in self.original_features:
            items.append({
                "feature": f,
                "display_name": f,
                "value": input_vals[f],
                "shap_value": agg[f],
            })
        items.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        top_positive = [x for x in items if x["shap_value"] > 0][:5]
        top_negative = [x for x in items if x["shap_value"] < 0][:5]
        return {
            "base_value": self.base_value,
            "shap_sum": float(np.sum(row_sv)),
            "top_features": items[:10],
            "top_positive": top_positive,
            "top_negative": top_negative,
        }
