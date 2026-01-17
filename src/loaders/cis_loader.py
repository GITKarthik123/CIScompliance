import openpyxl

def load_cis_controls(xlsx_path: str):
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active

    headers = [c.value for c in ws[1]]
    controls = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        record = dict(zip(headers, row))
        controls.append(record)

    return controls
