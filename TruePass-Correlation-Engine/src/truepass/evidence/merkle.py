"""SHA-256 Merkle trees and inclusion proofs for immutable evidence batches."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib

def _h(data:bytes)->bytes:return hashlib.sha256(data).digest()

def _normalize(leaf:bytes)->bytes:
    return leaf if len(leaf)==32 else _h(leaf)

@dataclass(frozen=True,slots=True)
class ProofStep:
    sibling_hex:str
    sibling_on_left:bool
@dataclass(frozen=True,slots=True)
class MerkleProof:
    leaf_hex:str
    index:int
    steps:tuple[ProofStep,...]

class MerkleTree:
    def __init__(self,leaves:list[bytes])->None:
        if not leaves:raise ValueError("at least one leaf is required")
        self.leaves=[_normalize(x) for x in leaves];self.levels=[self.leaves]
        level=self.leaves
        while len(level)>1:
            if len(level)%2:level=level+[level[-1]]
            level=[_h(level[i]+level[i+1]) for i in range(0,len(level),2)];self.levels.append(level)
    @property
    def root_hex(self)->str:return self.levels[-1][0].hex()
    def proof(self,index:int)->MerkleProof:
        if not 0<=index<len(self.leaves):raise IndexError(index)
        steps=[];idx=index
        for level in self.levels[:-1]:
            work=level if len(level)%2==0 else level+[level[-1]];sib=idx-1 if idx%2 else idx+1;steps.append(ProofStep(work[sib].hex(),sib<idx));idx//=2
        return MerkleProof(self.leaves[index].hex(),index,tuple(steps))
    @staticmethod
    def verify(proof:MerkleProof,root_hex:str)->bool:
        value=bytes.fromhex(proof.leaf_hex)
        for step in proof.steps:
            sib=bytes.fromhex(step.sibling_hex);value=_h(sib+value if step.sibling_on_left else value+sib)
        return value.hex()==root_hex
