from src.loaders.cis_loader import load_cis_controls
from src.api_checks.cis_repo_management import inactive_repositories
from src.report.csv_report import write_csv_report
def main():
    controls = load_cis_controls("cis-standards/CIS-Benchmarks.xlsx")
    # Run automated checks
    results = {}
    r = inactive_repositories()
    results[r["control_id"]] = r
    # add more checks here...
    # results["RM-1.3"] = require_branch_protection()
    # results["RM-1.4"] = require_signed_commits()
    write_csv_report(controls, results)
    print("CIS compliance CSV generated: reports/cis_compliance_report.csv")
if __name__ == "__main__":
    main()