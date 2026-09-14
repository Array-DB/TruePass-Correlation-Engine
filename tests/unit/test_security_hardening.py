from truepass.security import ReplayGuard,assess_clock,constant_time_secret_matches,redact_secret

def test_replay_guard_rejects_duplicate_and_is_bounded():
    g=ReplayGuard(2); assert g.accept("a"); assert not g.accept("a"); assert g.accept("b"); assert g.accept("c"); assert g.accept("a")
def test_clock_and_secret_helpers():
    a=assess_clock(100,now_ns=110,maximum_skew_ns=20); assert a.healthy and a.skew_ns==10
    assert constant_time_secret_matches("x","x") and not constant_time_secret_matches("x","y")
    assert redact_secret("abcdefgh")=="***efgh"
