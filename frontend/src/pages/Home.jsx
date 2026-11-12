import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getModelInfo } from "../services/api";
import { loadHistory } from "../utils/history";
import { Activity, BarChart3, ClipboardList, History } from "lucide-react";

export default function Home() {
  const [info, setInfo] = useState(null);
  const [history, setHistory] = useState([]);
  useEffect(() => {
    getModelInfo().then((r) => setInfo(r.data)).catch(() => {});
    setHistory(loadHistory());
  }, []);

  const totalPreds = history.length;
  const latest = history[0];

  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold">Diabetes Status Prediction System</h1>
        <p className="text-slate-600 dark:text-slate-300 mt-2">
          Cross-sectional estimation of current diabetes status using NHANES 2021–2023 data.
          This is not a medical diagnosis and does not predict future diabetes.
        </p>
        <Link to="/assess" className="btn-primary mt-4 inline-block">Start Assessment</Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 text-slate-500"><History className="w-4 h-4" /> Total Predictions</div>
          <div className="text-3xl font-bold mt-2">{totalPreds}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-slate-500"><BarChart3 className="w-4 h-4" /> Model</div>
          <div className="text-lg font-semibold mt-2">{info?.model_name || "—"}</div>
          <div className="text-sm text-slate-500">ROC-AUC: {info?.metrics?.roc_auc?.toFixed(3) || "—"}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-slate-500"><Activity className="w-4 h-4" /> Threshold</div>
          <div className="text-lg font-semibold mt-2">{info?.threshold?.toFixed(2) || "—"}</div>
          <div className="text-sm text-slate-500">Recall (test): {info?.metrics?.recall?.toFixed(3) || "—"}</div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Recent Predictions</h2>
        {history.length === 0 ? (
          <p className="text-slate-500">No predictions yet.</p>
        ) : (
          <ul className="divide-y divide-slate-200 dark:divide-slate-700">
            {history.slice(0, 5).map((h) => (
              <li key={h.id} className="py-2 flex justify-between text-sm">
                <span>{new Date(h.timestamp).toLocaleString()}</span>
                <span className={h.predicted_class === 1 ? "text-red-500" : "text-green-500"}>
                  {h.diabetes_status} ({h.model_score.toFixed(3)})
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {latest && (
        <div className="card">
          <h2 className="font-semibold mb-2">Last Result</h2>
          <p>{latest.diabetes_status} — score {latest.model_score.toFixed(3)}</p>
        </div>
      )}
    </div>
  );
}
