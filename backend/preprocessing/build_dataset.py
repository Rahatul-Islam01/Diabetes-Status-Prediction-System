"""Build cleaned analytic dataset from NHANES 2021-2023 XPT files."""
import os, json, numpy as np, pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RAW = os.path.join(ROOT, "dataset", "raw")
PROC = os.path.join(ROOT, "dataset", "processed")
os.makedirs(PROC, exist_ok=True)

def load(n):
    return pd.read_sas(os.path.join(RAW, n))

demo = load("DEMO_L.xpt")
bmx = load("BMX_L.xpt")
bp = load("BPXO_L.xpt")
ghb = load("GHB_L.xpt")
glu = load("GLU_L.xpt")
diq = load("DIQ_L.xpt")
paq = load("PAQ_L.xpt")
smq = load("SMQ_L.xpt")
alq = load("ALQ_L.xpt")
slq = load("SLQ_L.xpt")

MISSING_CODES = {7, 9, 77, 99, 777, 999, 7777, 9999, 77777, 99999, 777777, 999999}

def clean_missing_codes(df):
    df = df.copy()
    for col in df.columns:
        if col == "SEQN":
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].replace(list(MISSING_CODES), np.nan)
    for col in df.columns:
        if col == "SEQN":
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df.loc[df[col] < 1e-30, col] = np.nan
    return df

demo = clean_missing_codes(demo)
bmx = clean_missing_codes(bmx)
bp = clean_missing_codes(bp)
ghb = clean_missing_codes(ghb)
glu = clean_missing_codes(glu)
diq = clean_missing_codes(diq)
paq = clean_missing_codes(paq)
smq = clean_missing_codes(smq)
alq = clean_missing_codes(alq)
slq = clean_missing_codes(slq)

df = demo.merge(bmx, on="SEQN", how="left")
df = df.merge(bp, on="SEQN", how="left")
df = df.merge(ghb, on="SEQN", how="left")
df = df.merge(glu, on="SEQN", how="left")
df = df.merge(diq, on="SEQN", how="left")
df = df.merge(paq, on="SEQN", how="left")
df = df.merge(smq, on="SEQN", how="left")
df = df.merge(alq, on="SEQN", how="left")
df = df.merge(slq, on="SEQN", how="left")

n_before = len(df)
print("Merged rows:", n_before)

df = df[df["RIDAGEYR"] >= 18].copy()
print("After adult filter:", len(df))

def build_target(r):
    diq = r.get("DIQ010")
    hba1c = r.get("LBXGH")
    glu_v = r.get("LBXGLU")
    lab_diab = False
    if pd.notna(hba1c) and hba1c >= 6.5:
        lab_diab = True
    if pd.notna(glu_v) and glu_v >= 126:
        lab_diab = True
    if diq == 1:
        return 1
    if diq in (2, 3):
        if lab_diab:
            return 1
        return 0
    if pd.isna(diq):
        if lab_diab:
            return 1
        if pd.notna(hba1c) or pd.notna(glu_v):
            return 0
        return np.nan
    if lab_diab:
        return 1
    if pd.notna(hba1c) or pd.notna(glu_v):
        return 0
    return np.nan

df["diabetes"] = df.apply(build_target, axis=1)
print("Target null before drop:", df["diabetes"].isna().sum())
df = df[df["diabetes"].notna()].copy()
df["diabetes"] = df["diabetes"].astype(int)
print("After target drop:", len(df))
print("Class distribution:\n", df["diabetes"].value_counts())

def smoking_status(r):
    smq020 = r.get("SMQ020")
    smq040 = r.get("SMQ040")
    if smq020 == 2:
        return "never"
    if smq020 == 1:
        if smq040 in (1, 2):
            return "current"
        if smq040 == 3:
            return "former"
    return np.nan
df["smoking_status"] = df.apply(smoking_status, axis=1)
df["alcohol_ever"] = df["ALQ111"].map({1: 1.0, 2: 0.0})
df["sex"] = df["RIAGENDR"].map({1: "male", 2: "female"})

feature_cols = [
    "SEQN",
    "RIDAGEYR", "sex", "RIDRETH3", "DMDEDUC2", "DMDMARTZ", "INDFMPIR", "DMDHHSIZ",
    "BMXBMI", "BMXWAIST", "BMXHT", "BMXWT",
    "BPXOSY1", "BPXODI1", "BPXOPLS1",
    "PAD680", "PAD800", "PAD820",
    "smoking_status", "alcohol_ever",
    "SLD012",
    "diabetes",
]
for c in feature_cols:
    if c not in df.columns:
        print("MISSING COL:", c)
        df[c] = np.nan

clean = df[feature_cols].copy()
clean = clean.rename(columns={
    "RIDAGEYR": "age",
    "RIDRETH3": "race_ethnicity",
    "DMDEDUC2": "education",
    "DMDMARTZ": "marital_status",
    "INDFMPIR": "poverty_ratio",
    "DMDHHSIZ": "household_size",
    "BMXBMI": "bmi",
    "BMXWAIST": "waist_cm",
    "BMXHT": "height_cm",
    "BMXWT": "weight_kg",
    "BPXOSY1": "systolic_bp",
    "BPXODI1": "diastolic_bp",
    "BPXOPLS1": "pulse",
    "PAD680": "sedentary_min_day",
    "PAD800": "moderate_min_session",
    "PAD820": "vigorous_min_session",
    "SLD012": "sleep_hours",
})

out_csv = os.path.join(PROC, "diabetes_cleaned.csv")
clean.to_csv(out_csv, index=False)
print("Saved:", out_csv, clean.shape)

report = {
    "merged_rows": int(n_before),
    "final_rows": int(len(clean)),
    "class_distribution": {str(k): int(v) for k, v in clean["diabetes"].value_counts().items()},
    "missing_pct": {k: round(float(v)*100, 2) for k, v in clean.isna().mean().items()},
}
with open(os.path.join(ROOT, "reports", "data_quality.json"), "w") as f:
    json.dump(report, f, indent=2, default=str)
print("Report saved.")
print("Missing %:\n", clean.isna().mean().round(3))
