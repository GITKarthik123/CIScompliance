from src.loaders.cis_loader import load_cis_controls
from src.api_checks.cis_repo_management import inactive_repositories
from src.report.csv_report import write_csv_report


def main():
    # 1️⃣ Load all CIS controls from Excel
    controls = load_cis_controls("cis-standards/CIS-Benchmarks.xlsx")

    # 2️⃣ Run automated checks
    results = {}

    # ---- Repository Management (1.2.x) ----

    # 1.2.7 – Ensure inactive repositories are reviewed and archived periodically
    r = inactive_repositories()
    results[r["control_id"]] = r

    # NOTE:
    # Other Repository Management controls (1.2.1 – 1.2.6)
    # are intentionally NOT added here yet.
    # They will automatically appear in the report as:
    #   Validation Type = MANUAL
    #   Status          = MANUAL
    #   Evidence        = Not validated by automation

    # 3️⃣ Generate CSV report
    write_csv_report(controls, results)

    print("✅ CIS compliance CSV generated: reports/cis_compliance_report.csv")


if __name__ == "__main__":
    main()
