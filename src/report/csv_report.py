import csv
import os

def write_csv_report(controls, results, out_path="reports/cis_compliance_report.csv"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Section",
                "Control ID",
                "Control Name",
                "Category",
                "Validation Type",
                "Status",
                "Non-Compliant Items",
                "Evidence",
            ],
        )
        writer.writeheader()

        for c in controls:
            cid = c["Control ID"]

            r = results.get(cid)


            if r:
                status = r["status"]
                non_compliant = ", ".join(r.get("non_compliant", []))
                evidence = r.get("evidence", "")
                validation_type = "AUTOMATED"
            else:
                status = "MANUAL"
                non_compliant = ""
                evidence = "Not validated by automation"
                validation_type = c["Validation Type"]

            writer.writerow({
                "Section": c["Section"],
                "Control ID": cid,
                "Control Name": c["Control Name"],
                "Category": c["Category"],
                "Validation Type": c["Validation Type"],
                "Status": status,
                "Non-Compliant Items": non_compliant,
                "Evidence": evidence,
            })
