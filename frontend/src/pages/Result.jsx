import { useLocation, useNavigate, Link } from "react-router-dom";
import { useEffect } from "react";
import { addHistory } from "../utils/history";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const { payload, prediction, explanation } = location.state || {};

  useEffect(() => {
    if (prediction && payload) {
      const record = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        input: payload,
        predicted_class: prediction.predicted_class,
        diabetes_status: prediction.diabetes_status,
        model_score: prediction.model_score,
        threshold: prediction.threshold,
      };
      addHistory(record);
    }
  }, [prediction, payload]);

  if (!prediction) {
    return (
      <div className="card text-center">
        <p>No result available.</p>
        <Link to="/assess" className="btn-primary mt-4 inline-block">Go to Assessment</Link>
      </div>
    );
  }

  const positive = prediction.predicted_class === 1;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className={`card ${positive ? "border-red-300" : "border-green-300"}`}>
        <div className="flex items-center gap-3">
          {positive ? <AlertTriangle className="w-8 h-8 text-red-500" /> : <CheckCircle2 className="w-8 h-8 text-green-500" />}
          <div>
            <h1 className="text-2xl font-bold">{prediction.diabetes_status}</h1>
            <p className="text-sm text-slate-500">
              Model-estimated score: {prediction.model_score.toFixed(3)} (threshold {prediction.threshold.toFixed(2)})
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-3">
          The score is a model output for cross-sectional status classification, not a guaranteed personal probability of having or developing diabetes.
        </p>
      </div>

      <div className="card">
        <h2 className="font-semibold mb-3">Top Contributing Features</h2>
        {explanation?.top_positive?.length ? (
          <div className="mb-4">
            <h3 className="text-sm font-medium text-red-500 mb-2">Increasing likelihood</h3>
            <ul className="space-y-1 text-sm">
              {explanation.top_positive.map((f) => (
                <li key={f.feature} className="flex justify-between">
                  <span>{f.display_name} ({f.value})</span>
                  <span>+{f.shap_value.toFixed(3)}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {explanation?.top_negative?.length ? (
          <div>
            <h3 className="text-sm font-medium text-green-500 mb-2">Decreasing likelihood</h3>
            <ul className="space-y-1 text-sm">
              {explanation.top_negative.map((f) => (
                <li key={f.feature} className="flex justify-between">
                  <span>{f.display_name} ({f.value})</span>
                  <span>{f.shap_value.toFixed(3)}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <div className="card">
        <h2 className="font-semibold mb-2">Medical Disclaimer</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          This tool is for educational and research purposes only. It is not a medical diagnosis. Consult a qualified healthcare professional for diagnosis and treatment.
        </p>
      </div>

      <div className="flex gap-3">
        <Link to="/assess" className="btn-primary">New Assessment</Link>
        <Link to="/history" className="btn-secondary">View History</Link>
      </div>
    </div>
  );
}
