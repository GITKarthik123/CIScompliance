
import pandas as pd

def load_cis_controls(path: str):
    df = pd.read_excel(path)
    controls = []
    for _, row in df.iterrows():
        controls.append({
            "id": row.get("CIS ID"),
            "section": row.get("Section"),
            "title": row.get("Title"),
            "validation_type": row.get("Validation Type"),  # api | process | governance
        })
    return controls
