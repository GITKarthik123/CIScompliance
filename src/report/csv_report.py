import csv
import os

def write_csv_report(controls, results, out_path="reports/cis_compliance_report.csv"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Section",
            "Control ID",
            "Control Name",
            "Category",
            "Validation Type",
            "Status",
            "Non-Compliant Items",
            "Evidence"
        ])

        for c in controls:
            cid = c.get("Control ID") or c.get("ID")
            res = results.get(cid, {})

            writer.writerow([
                c.get("Section"),
                cid,
                c.get("Control Name"),
                c.get("Category"),
                c.get("Validation Type"),
                res.get("status", "MANUAL"),
                ", ".join(res.get("non_compliant", [])),
                res.get("evidence", "Not validated by automation")
            ])
