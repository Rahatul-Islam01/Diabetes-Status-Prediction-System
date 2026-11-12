import { useState } from "react";
import { loadHistory, deleteHistory, clearHistory } from "../utils/history";

export default function HistoryPage() {
  const [items, setItems] = useState(loadHistory());

  const handleDelete = (id) => setItems(deleteHistory(id));
  const handleClear = () => {
    if (confirm("Clear all history?")) {
      clearHistory();
      setItems([]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="card flex justify-between items-center">
        <h1 className="text-2xl font-bold">Prediction History</h1>
        {items.length > 0 && (
          <button onClick={handleClear} className="btn-secondary text-sm">Clear All</button>
        )}
      </div>
      {items.length === 0 ? (
        <div className="card text-center text-slate-500">No history yet.</div>
      ) : (
        <div className="space-y-3">
          {items.map((h) => (
            <div key={h.id} className="card">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold">{h.diabetes_status}</div>
                  <div className="text-sm text-slate-500">{new Date(h.timestamp).toLocaleString()}</div>
                  <div className="text-sm mt-1">Score: {h.model_score.toFixed(3)} (threshold {h.threshold.toFixed(2)})</div>
                </div>
                <button onClick={() => handleDelete(h.id)} className="text-red-500 text-sm">Delete</button>
              </div>
              <details className="mt-2 text-xs">
                <summary className="cursor-pointer text-slate-500">Input values</summary>
                <pre className="mt-2 overflow-auto">{JSON.stringify(h.input, null, 2)}</pre>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
