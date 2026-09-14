import struct
from truepass.sdr.sources import FileIQSource,SDRConfig,SyntheticIQSource
def test_synthetic_is_deterministic():
    a=SyntheticIQSource(seed=7).read_samples(4);b=SyntheticIQSource(seed=7).read_samples(4);assert a==b;assert len(a)==4
def test_file_iq_source(tmp_path):
    p=tmp_path/"iq.cf32";p.write_bytes(struct.pack("<ffff",1.0,2.0,3.0,4.0));samples=FileIQSource(p,SDRConfig(buffer_size=2)).read_samples();assert samples==[complex(1,2),complex(3,4)]
