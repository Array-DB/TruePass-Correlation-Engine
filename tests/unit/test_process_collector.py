from truepass.collectors.processes import ProcessCollector, ProcessSnapshot
from truepass.models.events import EventType


def snap(pid: int) -> ProcessSnapshot:
    return ProcessSnapshot(
        pid=pid,
        ppid=1,
        name=f"p{pid}",
        executable=f"/bin/p{pid}",
        username="tester",
        create_time_ns=1,
        cpu_percent=0.0,
        memory_rss=1024,
        command_line=None,
        sockets=(),
    )


def test_poll_detects_process_start_and_stop(monkeypatch) -> None:
    collector = ProcessCollector(include_sockets=False, host="test-host")
    snapshots = iter([{1: snap(1)}, {1: snap(1), 2: snap(2)}, {2: snap(2)}])
    monkeypatch.setattr(collector, "snapshot", lambda: next(snapshots))

    assert collector.poll() == []
    started = collector.poll()
    stopped = collector.poll()

    assert [event.event_type for event in started] == [EventType.PROCESS_STARTED]
    assert started[0].features["pid"] == 2
    assert [event.event_type for event in stopped] == [EventType.PROCESS_STOPPED]
    assert stopped[0].features["pid"] == 1
