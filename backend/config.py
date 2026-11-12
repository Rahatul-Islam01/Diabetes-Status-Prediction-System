import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAVED_DIR = os.path.join(ROOT_DIR, "saved_models")
REPORTS_DIR = os.path.join(ROOT_DIR, "..", "reports")

FEATURE_SCHEMA = {
    "age": {"type": "number", "min": 18, "max": 80, "unit": "years", "description": "Age in years (NHANES top-codes ages 80+).", "required": True},
    "sex": {"type": "category", "options": ["male", "female"], "description": "Biological sex.", "required": True},
    "race_ethnicity": {"type": "category", "options": [1,2,3,4,6,7], "labels": {"1":"Mexican American","2":"Other Hispanic","3":"Non-Hispanic White","4":"Non-Hispanic Black","6":"Non-Hispanic Asian","7":"Other/Multi-racial"}, "description": "Race/ethnicity category (NHANES RIDRETH3).", "required": True},
    "education": {"type": "category", "options": [1,2,3,4,5], "labels": {"1":"Less than 9th grade","2":"9-11th grade","3":"High school/GED","4":"Some college/AA","5":"College graduate+"}, "description": "Education level (DMDEDUC2).", "required": False},
    "marital_status": {"type": "category", "options": [1,2,3], "labels": {"1":"Married/living with partner","2":"Widowed/divorced/separated","3":"Never married"}, "description": "Marital status (DMDMARTZ).", "required": False},
    "poverty_ratio": {"type": "number", "min": 0, "max": 5, "unit": "ratio", "description": "Family poverty income ratio (INDFMPIR).", "required": False},
    "household_size": {"type": "number", "min": 1, "max": 7, "unit": "people", "description": "Number of people in household.", "required": False},
    "bmi": {"type": "number", "min": 12, "max": 80, "unit": "kg/m2", "description": "Body mass index.", "required": True},
    "waist_cm": {"type": "number", "min": 40, "max": 200, "unit": "cm", "description": "Waist circumference.", "required": True},
    "height_cm": {"type": "number", "min": 120, "max": 220, "unit": "cm", "description": "Standing height.", "required": False},
    "weight_kg": {"type": "number", "min": 30, "max": 250, "unit": "kg", "description": "Body weight.", "required": False},
    "systolic_bp": {"type": "number", "min": 70, "max": 260, "unit": "mmHg", "description": "Systolic blood pressure.", "required": True},
    "diastolic_bp": {"type": "number", "min": 40, "max": 150, "unit": "mmHg", "description": "Diastolic blood pressure.", "required": True},
    "pulse": {"type": "number", "min": 40, "max": 140, "unit": "bpm", "description": "60-second pulse.", "required": True},
    "sedentary_min_day": {"type": "number", "min": 0, "max": 1440, "unit": "min/day", "description": "Minutes sedentary per day.", "required": False},
    "moderate_min_session": {"type": "number", "min": 0, "max": 720, "unit": "min", "description": "Minutes moderate activity per session.", "required": False},
    "vigorous_min_session": {"type": "number", "min": 0, "max": 900, "unit": "min", "description": "Minutes vigorous activity per session.", "required": False},
    "sleep_hours": {"type": "number", "min": 2, "max": 14, "unit": "hours", "description": "Weekday sleep hours.", "required": False},
    "smoking_status": {"type": "category", "options": ["never", "former", "current"], "description": "Smoking status.", "required": False},
    "alcohol_ever": {"type": "category", "options": [0, 1], "labels": {"0": "No", "1": "Yes"}, "description": "Ever consumed alcohol.", "required": False},
}

NUMERIC_FEATURES = [k for k,v in FEATURE_SCHEMA.items() if v["type"]=="number"]
CATEGORICAL_FEATURES = [k for k,v in FEATURE_SCHEMA.items() if v["type"]=="category"]
ALL_FEATURES = list(FEATURE_SCHEMA.keys())

DISPLAY_NAMES = {
    "age": "Age",
    "sex": "Sex",
    "race_ethnicity": "Race/Ethnicity",
    "education": "Education",
    "marital_status": "Marital status",
    "poverty_ratio": "Poverty-income ratio",
    "household_size": "Household size",
    "bmi": "BMI",
    "waist_cm": "Waist circumference",
    "height_cm": "Height",
    "weight_kg": "Weight",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "pulse": "Pulse",
    "sedentary_min_day": "Sedentary minutes/day",
    "moderate_min_session": "Moderate activity min/session",
    "vigorous_min_session": "Vigorous activity min/session",
    "sleep_hours": "Sleep hours",
    "smoking_status": "Smoking status",
    "alcohol_ever": "Alcohol use",
}
