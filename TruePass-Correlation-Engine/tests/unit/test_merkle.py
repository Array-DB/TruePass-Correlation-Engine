from truepass.evidence.merkle import MerkleTree

def test_merkle_proof_and_tamper_detection():
    t=MerkleTree([b'a',b'b',b'c']);p=t.proof(1)
    assert MerkleTree.verify(p,t.root_hex)
    assert not MerkleTree.verify(p,'00'*32)
