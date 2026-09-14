from truepass.verification import run_overall_dod_audit


def test_source_level_dod_audit_passes() -> None:
    audit = run_overall_dod_audit(include_external=False)
    assert audit.implementation_complete
    assert audit.overall_pass
    assert all(check.status == "pass" for check in audit.checks)
