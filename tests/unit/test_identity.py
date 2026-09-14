from truepass.identity import ContextAssertionFactor, IdentityPolicy, IdentityVerifier


def test_identity_policy_requires_threshold_and_factor_count() -> None:
    verifier = IdentityVerifier(
        [ContextAssertionFactor("device", "device_present"), ContextAssertionFactor("os", "os_credential")],
        IdentityPolicy(threshold=0.75, minimum_factors=2),
    )
    denied = verifier.verify("subject-1", {"device_present": True, "os_credential": False})
    allowed = verifier.verify("subject-1", {"device_present": True, "os_credential": True})
    assert not denied.authorized
    assert allowed.authorized
    assert allowed.score == 1.0
