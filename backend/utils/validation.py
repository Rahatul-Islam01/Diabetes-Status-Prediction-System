import numpy as np
import pandas as pd
try:
    from ..config import FEATURE_SCHEMA, ALL_FEATURES
except Exception:
    from config import FEATURE_SCHEMA, ALL_FEATURES

REQUIRED_FEATURES = [f for f in ALL_FEATURES if FEATURE_SCHEMA[f].get("required", True)]

def validate_input(data):
    errors = []
    if not isinstance(data, dict):
        return None, ["Input must be a JSON object."]
    # only required fields are mandatory
    missing = [f for f in REQUIRED_FEATURES if f not in data or data[f] in (None, "") ]
    if missing:
        errors.append(f"Missing required fields: {missing}")
    # type/range checks
    cleaned = {}
    for f in ALL_FEATURES:
        # optional field not provided -> NaN (imputer will fill)
        if f not in data or data[f] in (None, ""):
            if f in REQUIRED_FEATURES:
                continue  # already reported above
            cleaned[f] = np.nan
            continue
        val = data[f]
        schema = FEATURE_SCHEMA[f]
        if schema["type"] == "number":
            try:
                num = float(val)
            except (TypeError, ValueError):
                errors.append(f"{f}: must be a number.")
                continue
            if "min" in schema and num < schema["min"]:
                errors.append(f"{f}: below minimum {schema['min']}.")
            if "max" in schema and num > schema["max"]:
                errors.append(f"{f}: above maximum {schema['max']}.")
            cleaned[f] = num
        else:
            # category
            opts = schema["options"]
            # coerce numeric options
            if all(isinstance(o, (int, float)) for o in opts) and not isinstance(val, str):
                try:
                    valc = int(val) if float(val).is_integer() else float(val)
                except (TypeError, ValueError):
                    errors.append(f"{f}: invalid value.")
                    continue
            else:
                valc = val
            if valc not in opts:
                # try string match for numeric options
                if str(valc) in [str(o) for o in opts]:
                    valc = opts[[str(o) for o in opts].index(str(valc))]
                else:
                    errors.append(f"{f}: must be one of {opts}.")
                    continue
            cleaned[f] = valc
    if errors:
        return None, errors
    # build dataframe in correct column order
    row = {f: cleaned.get(f) for f in ALL_FEATURES}
    df = pd.DataFrame([row])
    return df, []
