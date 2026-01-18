import openpyxl

HEADER_MAP = {
    "Section": ["Section", "CIS Section"],
    "Control ID": ["Control ID", "CIS Control", "Control"],
    "Control Name": ["Control Name", "Title", "Control Title"],
    "Category": ["Category", "Asset Type", "Implementation Group"],
    "Validation Type": ["Validation Type", "Automated / Manual", "Automation"],
}

def load_cis_controls(xlsx_path: str):
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active

    raw_headers = [c.value for c in ws[1]]

    def find_col(possible_names):
        for name in possible_names:
            if name in raw_headers:
                return raw_headers.index(name)
        return None

    col_idx = {
        k: find_col(v) for k, v in HEADER_MAP.items()
    }

    controls = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        controls.append({
            "Section": row[col_idx["Section"]] if col_idx["Section"] is not None else "",
            "Control ID": row[col_idx["Control ID"]] if col_idx["Control ID"] is not None else "",
            "Control Name": row[col_idx["Control Name"]] if col_idx["Control Name"] is not None else "",
            "Category": row[col_idx["Category"]] if col_idx["Category"] is not None else "",
            "Validation Type": row[col_idx["Validation Type"]] if col_idx["Validation Type"] is not None else "MANUAL",
        })

    return controls
