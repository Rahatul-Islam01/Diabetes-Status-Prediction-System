import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getFeatures, predict, explain } from "../services/api";

export default function Assessment() {
  const [features, setFeatures] = useState([]);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getFeatures()
      .then((r) => {
        setFeatures(r.data.features);
        const init = {};
        r.data.features.forEach((f) => {
          init[f.name] = f.type === "number" ? "" : (f.options ? f.options[0] : "");
        });
        setForm(init);
      })
      .catch(() => setError("Failed to load features."));
  }, []);

  const handleChange = (name, value) => setForm((prev) => ({ ...prev, [name]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    // validate only required fields
    for (const f of features) {
      if (f.required && (form[f.name] === "" || form[f.name] === null || form[f.name] === undefined)) {
        setError(`Please fill ${f.display_name || f.name}.`);
        return;
      }
    }
    setLoading(true);
    try {
      const payload = {};
      features.forEach((f) => {
        const val = form[f.name];
        // skip empty optional fields entirely
        if (val === "" || val === null || val === undefined) {
          if (!f.required) return;
          return;
        }
        if (f.type === "number") payload[f.name] = Number(val);
        else if (f.type === "category" && f.options.every((o) => typeof o === "number")) {
          payload[f.name] = Number(val);
        } else {
          payload[f.name] = val;
        }
      });
      const [predRes, explRes] = await Promise.all([predict(payload), explain(payload)]);
      navigate("/result", { state: { payload, prediction: predRes.data, explanation: explRes.data } });
    } catch (err) {
      setError(err?.response?.data?.details || err.message || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  if (features.length === 0) {
    return <div className="card">Loading form...</div>;
  }

  return (
    <div className="card max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Diabetes Assessment</h1>
      <p className="text-sm text-slate-500 mb-6">
        Marked fields (<span className="font-semibold text-red-500">*</span>) are required. Others are optional — you may skip them.
      </p>
      {error && <div className="mb-4 p-3 rounded bg-red-100 text-red-700 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map((f) => (
          <div key={f.name}>
            <label className="label">
              {f.display_name || f.name} {f.required ? <span className="text-red-500 ml-1 font-bold">*</span> : <span className="text-slate-400 ml-1 text-xs">(Optional)</span>} {f.unit ? `(${f.unit})` : ""}
            </label>
            {f.type === "number" ? (
              <input
                type="number"
                step="any"
                min={f.min}
                max={f.max}
                value={form[f.name]}
                onChange={(e) => handleChange(f.name, e.target.value)}
                className="input"
              />
            ) : (
              <select
                value={form[f.name]}
                onChange={(e) => handleChange(f.name, e.target.value)}
                className="input"
              >
                {f.options.map((opt) => (
                  <option key={opt} value={opt}>
                    {f.labels ? f.labels[String(opt)] : opt}
                  </option>
                ))}
              </select>
            )}
            <p className="text-xs text-slate-500 mt-1">{f.description}</p>
          </div>
        ))}
        <div className="md:col-span-2">
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Analyzing..." : "Predict"}
          </button>
        </div>
      </form>
    </div>
  );
}
