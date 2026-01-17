
"""cis_checks.py
Auto-generated checks based on github_cis_controls.json.

NOTE: This module expects helper clients:
  - github_client.get(path: str) -> Any (wraps GitHub REST v3)
  - okta_client.get(path: str) -> Any (wraps Okta API)

Where possible, checks query GitHub branch protection and repository settings.
For environment-specific items (CI, build workers, artifact registries), a TODO stub is provided.
"""

from typing import Any, Dict, List
from github_client import get as gh_get
from okta_client import get as okta_get

ORG = "DevOps-Common"

# --- Utilities ---
def _list_repos(per_page: int = 100) -> List[Dict[str, Any]]:
    return gh_get(f"/orgs/{ORG}/repos?per_page={per_page}") or []

def _default_branch(repo: Dict[str, Any]) -> str:
    return repo.get('default_branch') or 'main'

def _get_branch_protection(repo_name: str, branch: str) -> Dict[str, Any]:
    # GET branch protection (200 if enabled, 404 if not)
    return gh_get(f"/repos/{ORG}/{repo_name}/branches/{branch}/protection") or {}

def _get_required_signatures(repo_name: str, branch: str) -> Dict[str, Any]:
    return gh_get(f"/repos/{ORG}/{repo_name}/branches/{branch}/protection/required_signatures") or {}

def _get_repo_content_path(repo_name: str, path: str) -> Dict[str, Any]:
    return gh_get(f"/repos/{ORG}/{repo_name}/contents/{path}") or {}

def _list_org_admins() -> List[Dict[str, Any]]:
    return gh_get(f"/orgs/{ORG}/members?role=admin") or []

# --- Concrete GitHub/Okta checks ---
def branch_protection() -> List[str]:
    """Repos missing any branch protection on default branch."""
    missing = []
    for r in _list_repos():
        name = r['name']; branch = _default_branch(r)
        bp = _get_branch_protection(name, branch)
        if not bp:
            missing.append(name)
    return missing

def security_md() -> List[str]:
    """Repos missing SECURITY.md."""
    missing = []
    for r in _list_repos():
        name = r['name']
        sec = _get_repo_content_path(name, 'SECURITY.md')
        if not sec:
            missing.append(name)
    return missing

def admin_count(max_admins: int = 5) -> bool:
    """Org has <= max_admins admins."""
    admins = _list_org_admins()
    return len(admins) <= max_admins

def app_approval() -> bool:
    """All org installations are either suspended or require owner approval (simplified)."""
    apps = gh_get(f"/orgs/{ORG}/installations") or []
    for a in apps:
        if a.get('suspended') is False:
            return False
    return True

def okta_mfa() -> bool:
    """Okta MFA enrollment policy is ACTIVE."""
    policies = okta_get("/api/v1/policies?type=MFA_ENROLL") or []
    return any(p.get('status') == 'ACTIVE' for p in policies)

# Branch protection options
def require_pr_reviews(min_approvals: int = 2) -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        pr = (_get_branch_protection(name, branch) or {}).get('required_pull_request_reviews') or {}
        require = bool(pr)
        count = pr.get('required_approving_review_count') or 0
        if not require or count < min_approvals:
            failing.append(name)
    return failing

def dismiss_stale_reviews() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        pr = (_get_branch_protection(name, branch) or {}).get('required_pull_request_reviews') or {}
        if not pr.get('dismiss_stale_reviews'):
            failing.append(name)
    return failing

def restrict_dismissals() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        pr = (_get_branch_protection(name, branch) or {}).get('required_pull_request_reviews') or {}
        if not pr.get('restrict_dismissals'):
            failing.append(name)
    return failing

def require_code_owner_reviews() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        pr = (_get_branch_protection(name, branch) or {}).get('required_pull_request_reviews') or {}
        if not pr.get('require_code_owner_reviews'):
            failing.append(name)
    return failing

def require_status_checks(strict_up_to_date: bool=True) -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        sc = (_get_branch_protection(name, branch) or {}).get('required_status_checks') or {}
        has = bool(sc.get('contexts') or sc.get('checks'))
        strict = sc.get('strict') is True
        if not has or (strict_up_to_date and not strict):
            failing.append(name)
    return failing

def require_conversation_resolution() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        pr = (_get_branch_protection(name, branch) or {}).get('required_pull_request_reviews') or {}
        conv = pr.get('require_conversation_resolution') or pr.get('require_last_push_approval')
        if not conv:
            failing.append(name)
    return failing

def require_signed_commits() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        rs = _get_required_signatures(name, branch)
        if not rs or not rs.get('enabled'):
            failing.append(name)
    return failing

def require_linear_history() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        bp=_get_branch_protection(name, branch)
        rl = bp.get('required_linear_history') if bp else None
        enabled = (isinstance(rl, dict) and rl.get('enabled')) or (isinstance(rl, bool) and rl)
        if not enabled:
            failing.append(name)
    return failing

def include_admins_in_protection() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        ea = (_get_branch_protection(name, branch) or {}).get('enforce_admins') or {}
        if not ea.get('enabled'):
            failing.append(name)
    return failing

def deny_force_pushes() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        allow = ((_get_branch_protection(name, branch) or {}).get('allow_force_pushes') or {}).get('enabled')
        if allow:
            failing.append(name)
    return failing

def deny_deletions() -> List[str]:
    failing=[]
    for r in _list_repos():
        name=r['name']; branch=_default_branch(r)
        allow = ((_get_branch_protection(name, branch) or {}).get('allow_deletions') or {}).get('enabled')
        if allow:
            failing.append(name)
    return failing

# --- Generic TODO stub for environment-specific checks ---
def _TODO_stub(check_name: str) -> Any:
    return {
        'implemented': False,
        'reason': f"Check '{check_name}' requires environment-specific data (CI/build workers/artifact registry) not available via GitHub API."
    }

def any_changes_code_tracked_version_control():
    return _TODO_stub('any_changes_code_tracked_version_control')


def any_change_code_can_traced_back():
    return _TODO_stub('any_change_code_can_traced_back')


def any_change_code_receives_approval_two():
    return _TODO_stub('any_change_code_receives_approval_two')


def previous_approvals_dismissed_when_updates_introduced():
    return _TODO_stub('previous_approvals_dismissed_when_updates_introduced')


def there_restrictions_who_can_dismiss_code():
    return _TODO_stub('there_restrictions_who_can_dismiss_code')


def code_owners_set_extra_sensitive_code():
    return _TODO_stub('code_owners_set_extra_sensitive_code')


def code_owner_s_review_when_change():
    return _TODO_stub('code_owner_s_review_when_change')


def inactive_branches_periodically_reviewed_removed():
    return _TODO_stub('inactive_branches_periodically_reviewed_removed')


def all_checks_have_passed_merging_new():
    return _TODO_stub('all_checks_have_passed_merging_new')


def open_git_branches_up_date_they():
    return _TODO_stub('open_git_branches_up_date_they')


def all_open_comments_resolved_allowing_code():
    return _TODO_stub('all_open_comments_resolved_allowing_code')


def verification_signed_commits_new_changes_merging():
    return _TODO_stub('verification_signed_commits_new_changes_merging')


def linear_history():
    return _TODO_stub('linear_history')


def branch_protection_rules_enforced_administrators():
    return _TODO_stub('branch_protection_rules_enforced_administrators')


def pushing_merging_new_code_restricted_specific():
    return _TODO_stub('pushing_merging_new_code_restricted_specific')


def force_push_code_branches_denied():
    return _TODO_stub('force_push_code_branches_denied')


def branch_deletions_denied():
    return _TODO_stub('branch_deletions_denied')


def any_merging_code_automatically_scanned_risks():
    return _TODO_stub('any_merging_code_automatically_scanned_risks')


def any_changes_branch_protection_rules_audited():
    return _TODO_stub('any_changes_branch_protection_rules_audited')


def repository_creation_limited_specific_members():
    return _TODO_stub('repository_creation_limited_specific_members')


def repository_deletion_limited_specific_users():
    return _TODO_stub('repository_deletion_limited_specific_users')


def issue_deletion_limited_specific_users():
    return _TODO_stub('issue_deletion_limited_specific_users')


def all_copies_forks_code_tracked_accounted():
    return _TODO_stub('all_copies_forks_code_tracked_accounted')


def all_code_projects_tracked_changes_visibility():
    return _TODO_stub('all_code_projects_tracked_changes_visibility')


def inactive_repositories_reviewed_archived_periodically():
    return _TODO_stub('inactive_repositories_reviewed_archived_periodically')


def inactive_users_reviewed_removed_periodically():
    return _TODO_stub('inactive_users_reviewed_removed_periodically')


def team_creation_limited_specific_members():
    return _TODO_stub('team_creation_limited_specific_members')


def multi_factor_authentication_mfa_contributors_new():
    return _TODO_stub('multi_factor_authentication_mfa_contributors_new')


def organization_requiring_members_use_multi_factor():
    return _TODO_stub('organization_requiring_members_use_multi_factor')


def new_members_invited_company_approved_email():
    return _TODO_stub('new_members_invited_company_approved_email')


def two_administrators_set_each_repository():
    return _TODO_stub('two_administrators_set_each_repository')


def strict_base_permissions_set_repositories():
    return _TODO_stub('strict_base_permissions_set_repositories')


def organization_s_identity_confirmed_verified_badge():
    return _TODO_stub('organization_s_identity_confirmed_verified_badge')


def source_code_management_scm_email_notifications():
    return _TODO_stub('source_code_management_scm_email_notifications')


def organization_provides_ssh_certificates():
    return _TODO_stub('organization_provides_ssh_certificates')


def git_access_limited_based_ip_addresses():
    return _TODO_stub('git_access_limited_based_ip_addresses')


def anomalous_code_behavior_tracked():
    return _TODO_stub('anomalous_code_behavior_tracked')


def stale_applications_reviewed_inactive_ones_removed():
    return _TODO_stub('stale_applications_reviewed_inactive_ones_removed')


def access_granted_each_installed_application_limited():
    return _TODO_stub('access_granted_each_installed_application_limited')


def only_secured_webhooks_used():
    return _TODO_stub('only_secured_webhooks_used')


def scanners_place_identify_prevent_sensitive_data():
    return _TODO_stub('scanners_place_identify_prevent_sensitive_data')


def scanners_place_secure_continuous_integration_ci():
    return _TODO_stub('scanners_place_secure_continuous_integration_ci')


def scanners_place_secure_infrastructure_as_code():
    return _TODO_stub('scanners_place_secure_infrastructure_as_code')


def scanners_place_code_vulnerabilities():
    return _TODO_stub('scanners_place_code_vulnerabilities')


def scanners_place_open_source_vulnerabilities_used():
    return _TODO_stub('scanners_place_open_source_vulnerabilities_used')


def scanners_place_open_source_license_issues():
    return _TODO_stub('scanners_place_open_source_license_issues')


def each_pipeline_has_single_responsibility():
    return _TODO_stub('each_pipeline_has_single_responsibility')


def all_aspects_pipeline_infrastructure_configuration_immutable():
    return _TODO_stub('all_aspects_pipeline_infrastructure_configuration_immutable')


def build_environment_logged():
    return _TODO_stub('build_environment_logged')


def creation_build_environment_automated():
    return _TODO_stub('creation_build_environment_automated')


def access_build_environments_limited():
    return _TODO_stub('access_build_environments_limited')


def users_must_authenticate_access_build_environment():
    return _TODO_stub('users_must_authenticate_access_build_environment')


def build_secrets_limited_minimal_necessary_scope():
    return _TODO_stub('build_secrets_limited_minimal_necessary_scope')


def build_infrastructure_automatically_scanned_vulnerabilities():
    return _TODO_stub('build_infrastructure_automatically_scanned_vulnerabilities')


def default_passwords_not_used():
    return _TODO_stub('default_passwords_not_used')


def webhooks_build_environment_secured():
    return _TODO_stub('webhooks_build_environment_secured')


def minimum_number_administrators_set_build_environment():
    return _TODO_stub('minimum_number_administrators_set_build_environment')


def build_workers_single_used():
    return _TODO_stub('build_workers_single_used')


def build_worker_environments_commands_passed_not():
    return _TODO_stub('build_worker_environments_commands_passed_not')


def duties_each_build_worker_segregated():
    return _TODO_stub('duties_each_build_worker_segregated')


def build_workers_have_minimal_network_connectivity():
    return _TODO_stub('build_workers_have_minimal_network_connectivity')


def run_time_security_enforced_build_workers():
    return _TODO_stub('run_time_security_enforced_build_workers')


def build_workers_automatically_scanned_vulnerabilities():
    return _TODO_stub('build_workers_automatically_scanned_vulnerabilities')


def build_workers_deployment_configuration_stored_version():
    return _TODO_stub('build_workers_deployment_configuration_stored_version')


def resource_consumption_build_workers_monitored():
    return _TODO_stub('resource_consumption_build_workers_monitored')


def all_build_steps_defined_as_code():
    return _TODO_stub('all_build_steps_defined_as_code')


def steps_have_clearly_defined_build_stage():
    return _TODO_stub('steps_have_clearly_defined_build_stage')


def output_written_separate_secured_storage_repository():
    return _TODO_stub('output_written_separate_secured_storage_repository')


def changes_pipeline_files_tracked_reviewed():
    return _TODO_stub('changes_pipeline_files_tracked_reviewed')


def access_build_process_triggering_minimized():
    return _TODO_stub('access_build_process_triggering_minimized')


def pipelines_automatically_scanned_misconfigurations():
    return _TODO_stub('pipelines_automatically_scanned_misconfigurations')


def pipelines_automatically_scanned_vulnerabilities():
    return _TODO_stub('pipelines_automatically_scanned_vulnerabilities')


def all_artifacts_all_releases_signed():
    return _TODO_stub('all_artifacts_all_releases_signed')


def all_external_dependencies_used_build_process():
    return _TODO_stub('all_external_dependencies_used_build_process')


def dependencies_validated_being_used():
    return _TODO_stub('dependencies_validated_being_used')


def build_pipeline_creates_reproducible_artifacts():
    return _TODO_stub('build_pipeline_creates_reproducible_artifacts')


def pipeline_steps_produce_software_bill_materials():
    return _TODO_stub('pipeline_steps_produce_software_bill_materials')


def pipeline_steps_sign_software_bill_materials():
    return _TODO_stub('pipeline_steps_sign_software_bill_materials')


def third_party_artifacts_open_source_libraries():
    return _TODO_stub('third_party_artifacts_open_source_libraries')


def software_bill_materials_sbom_all_third():
    return _TODO_stub('software_bill_materials_sbom_all_third')


def signed_metadata_build_process_verified():
    return _TODO_stub('signed_metadata_build_process_verified')


def dependencies_monitored_between_open_source_components():
    return _TODO_stub('dependencies_monitored_between_open_source_components')


def trusted_package_managers_repositories_defined_prioritized():
    return _TODO_stub('trusted_package_managers_repositories_defined_prioritized')


def signed_software_bill_materials_sbom_code():
    return _TODO_stub('signed_software_bill_materials_sbom_code')


def dependencies_pinned_specific_verified_version():
    return _TODO_stub('dependencies_pinned_specific_verified_version')


def all_packages_used_more_than_60():
    return _TODO_stub('all_packages_used_more_than_60')


def organization_wide_dependency_usage_policy_enforced():
    return _TODO_stub('organization_wide_dependency_usage_policy_enforced')


def packages_automatically_scanned_known_vulnerabilities():
    return _TODO_stub('packages_automatically_scanned_known_vulnerabilities')


def packages_automatically_scanned_license_implications():
    return _TODO_stub('packages_automatically_scanned_license_implications')


def packages_automatically_scanned_ownership_change():
    return _TODO_stub('packages_automatically_scanned_ownership_change')


def all_artifacts_signed_build_pipeline_itself():
    return _TODO_stub('all_artifacts_signed_build_pipeline_itself')


def artifacts_encrypted_distribution():
    return _TODO_stub('artifacts_encrypted_distribution')


def only_authorized_platforms_have_decryption_capabilities():
    return _TODO_stub('only_authorized_platforms_have_decryption_capabilities')


def authority_certify_artifacts_limited():
    return _TODO_stub('authority_certify_artifacts_limited')


def number_permitted_users_who_may_upload():
    return _TODO_stub('number_permitted_users_who_may_upload')


def user_access_package_registry_utilizes_multi():
    return _TODO_stub('user_access_package_registry_utilizes_multi')


def user_management_package_registry_not_local():
    return _TODO_stub('user_management_package_registry_not_local')


def anonymous_access_artifacts_revoked():
    return _TODO_stub('anonymous_access_artifacts_revoked')


def minimum_number_administrators_set_package_registry():
    return _TODO_stub('minimum_number_administrators_set_package_registry')


def all_signed_artifacts_validated_upon_uploading():
    return _TODO_stub('all_signed_artifacts_validated_upon_uploading')


def all_versions_existing_artifact_have_their():
    return _TODO_stub('all_versions_existing_artifact_have_their')


def changes_package_registry_configuration_audited():
    return _TODO_stub('changes_package_registry_configuration_audited')


def webhooks_repository_secured():
    return _TODO_stub('webhooks_repository_secured')


def artifacts_contain_information_about_their_origin():
    return _TODO_stub('artifacts_contain_information_about_their_origin')


def deployment_configuration_files_separated_source_code():
    return _TODO_stub('deployment_configuration_files_separated_source_code')


def changes_deployment_configuration_audited():
    return _TODO_stub('changes_deployment_configuration_audited')


def limit_access_deployment_configurations():
    return _TODO_stub('limit_access_deployment_configurations')


def scan_infrastructure_as_code_iac():
    return _TODO_stub('scan_infrastructure_as_code_iac')


def deployment_configuration_manifests_verified():
    return _TODO_stub('deployment_configuration_manifests_verified')


def deployment_configuration_manifests_pinned_specific_verified():
    return _TODO_stub('deployment_configuration_manifests_pinned_specific_verified')


def deployments_automated():
    return _TODO_stub('deployments_automated')


def deployment_environment_reproducible():
    return _TODO_stub('deployment_environment_reproducible')


def access_production_environment_limited():
    return _TODO_stub('access_production_environment_limited')

import json as _json
import re as _re

def run_all_checks() -> Dict[str, Any]:
    """Run every check listed in github_cis_controls.json and return a mapping from control id to result."""
    with open('github_cis_controls.json','r',encoding='utf-8') as f:
        controls = _json.load(f)
    results: Dict[str, Any] = {}
    for c in controls:
        cname=c['check']
        cid=c['id']
        fn_name=_re.sub(r'[^a-zA-Z0-9_]', '_', cname)
        fn=globals().get(fn_name)
        if callable(fn):
            try:
                results[cid]=fn()
            except Exception as e:
                results[cid]={'implemented': False, 'error': str(e)}
        else:
            results[cid]={'implemented': False, 'reason': f"No function generated for check '{cname}'"}
    return results

# Compatibility alias for historical slug
any_changes_code_tracked_version = any_changes_code_tracked_version_control
any_change_code_can_traced = any_change_code_can_traced_back
any_change_code_receives_approval = any_change_code_receives_approval_two
previous_approvals_dismissed_when_updates = previous_approvals_dismissed_when_updates_introduced
there_restrictions_who_can_dismiss = there_restrictions_who_can_dismiss_code