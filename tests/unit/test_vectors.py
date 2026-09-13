import pytest
from truepass.vectors import InMemoryVectorIndex

def test_cosine_similarity_search():
    v=InMemoryVectorIndex(3);v.upsert('same',[1,0,0]);v.upsert('other',[0,1,0])
    hits=v.search([1,0,0])
    assert hits[0].item_id=='same' and hits[0].similarity==pytest.approx(1.0)
