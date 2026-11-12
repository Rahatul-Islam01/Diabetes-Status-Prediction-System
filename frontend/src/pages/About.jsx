export default function About() {
  return (
    <div className="card space-y-4 max-w-3xl">
      <h1 className="text-2xl font-bold">About & Disclaimer</h1>
      <section>
        <h2 className="font-semibold">Project Objective</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Estimate whether a person currently has diabetes based on selected health features using NHANES 2021–2023 cross-sectional data. This is not future diabetes prediction or medical diagnosis.
        </p>
      </section>
      <section>
        <h2 className="font-semibold">Dataset Source</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          CDC NHANES August 2021–August 2023. Files: DEMO_L, BMX_L, BPXO_L, GHB_L, GLU_L, DIQ_L, PAQ_L, SMQ_L, ALQ_L, SLQ_L.
        </p>
      </section>
      <section>
        <h2 className="font-semibold">Target Definition</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Current diabetes status = doctor-diagnosed diabetes (DIQ010=1) OR HbA1c ≥ 6.5% OR fasting glucose ≥ 126 mg/dL. HbA1c/glucose excluded from predictors to prevent leakage.
        </p>
      </section>
      <section>
        <h2 className="font-semibold">Methodology</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Stratified train/validation/test split, cross-validation, hyperparameter tuning (RandomizedSearchCV), threshold selection on validation data, SHAP explainability.
        </p>
      </section>
      <section>
        <h2 className="font-semibold">Limitations</h2>
        <ul className="text-sm text-slate-600 dark:text-slate-300 list-disc pl-5">
          <li>Cross-sectional data; not a diagnosis.</li>
          <li>Demographic bias and missing data.</li>
          <li>Performance varies across subgroups.</li>
          <li>Not for clinical use.</li>
        </ul>
      </section>
      <section>
        <h2 className="font-semibold">Medical Disclaimer</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          This application is for research and educational purposes only. It does not replace professional medical advice, diagnosis, or treatment.
        </p>
      </section>
    </div>
  );
}
