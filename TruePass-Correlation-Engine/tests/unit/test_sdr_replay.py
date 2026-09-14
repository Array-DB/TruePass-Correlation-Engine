from __future__ import annotations

import struct

from truepass.sdr.sources import FileIQSource, SDRConfig, SyntheticIQSource, open_sdr_source


def test_file_iq_source_reads_sequentially_and_rewinds(tmp_path) -> None:
    path = tmp_path / "samples.cf32"
    path.write_bytes(b"".join(struct.pack("<ff", float(i), -float(i)) for i in range(4)))
    with FileIQSource(path, SDRConfig(buffer_size=2, device="file")) as source:
        assert source.read_samples(2) == [0j, complex(1.0, -1.0)]
        assert source.read_samples(2) == [complex(2.0, -2.0), complex(3.0, -3.0)]
        assert source.read_samples(2) == []
        source.rewind()
        assert source.read_samples(1) == [0j]


def test_open_sdr_source_synthetic() -> None:
    source = open_sdr_source(SDRConfig(device="synthetic"))
    assert isinstance(source, SyntheticIQSource)
    assert len(source.read_samples(8)) == 8
