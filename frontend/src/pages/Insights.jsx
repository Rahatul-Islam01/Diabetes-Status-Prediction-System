import { useEffect, useState } from "react";
import { getModelInfo } from "../services/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend
} from "recharts";

export default function Insights() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getModelInfo()
      .then((r) => setInfo(r.data))
      .catch(() => setError("Failed to load model info."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="card">Loading...</div>;
  if (error) return <div className="card text-red-500">{error}</div>;
  if (!info) return null;

  const m = info.metrics || {};
  const comparison = Object.entries(info.model_comparison || {}).map(([name, v]) => ({
    name,
    roc_auc: v.roc_auc,
    recall: v.recall,
    f1: v.f1,
  }));

  const shapData = (info.shap_global_importance || []).slice(0, 12).map((x) => ({
    name: x.feature.replace("num__", "").replace("cat__", ""),
    value: x.importance,
  }));

  const confusion = m.confusion_matrix || {};

  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold mb-2">Model Insights</h1>
        <p className="text-sm text-slate-500">
          Selected model: <span className="font-semibold">{info.model_name}</span>. Evaluation metrics from held-out test set.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ["Accuracy", m.accuracy],
          ["Precision", m.precision],
          ["Recall", m.recall],
          ["F1-score", m.f1],
          ["ROC-AUC", m.roc_auc],
          ["PR-AUC", m.pr_auc],
          ["Specificity", m.specificity],
          ["Brier", m.brier],
        ].map(([label, val]) => (
          <div className="card" key={label}>
            <div className="text-xs text-slate-500">{label}</div>
            <div className="text-xl font-bold">{val != null ? val.toFixed(3) : "—"}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Confusion Matrix</h2>
        <div className="grid grid-cols-2 gap-2 max-w-xs">
          <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded text-center">
            <div className="text-xs">TN</div><div className="text-xl font-bold">{confusion.tn}</div>
          </div>
          <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded text-center">
            <div className="text-xs">FP</div><div className="text-xl font-bold">{confusion.fp}</div>
          </div>
          <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded text-center">
            <div className="text-xs">FN</div><div className="text-xl font-bold">{confusion.fn}</div>
          </div>
          <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded text-center">
            <div className="text-xs">TP</div><div className="text-xl font-bold">{confusion.tp}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Model Comparison (Validation ROC-AUC)</h2>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={comparison}>
              <XAxis dataKey="name" angle={-20} textAnchor="end" height={60} fontSize={11} />
              <YAxis domain={[0.7, 0.85]} />
              <Tooltip />
              <Bar dataKey="roc_auc" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Global Feature Importance (SHAP)</h2>
        <div style={{ width: "100%", height: 360 }}>
          <ResponsiveContainer>
            <BarChart data={shapData} layout="vertical">
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={140} fontSize={11} />
              <Tooltip />
              <Bar dataKey="value" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">ROC & PR Curves</h2>
        <p className="text-sm text-slate-500">
          Curves are saved as images in reports/figures. (roc_curve.png, pr_curve.png)
        </p>
      </div>
    </div>
  );
}
