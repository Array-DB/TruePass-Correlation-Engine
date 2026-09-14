"""Vector similarity search; relational evidence remains authoritative."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np

@dataclass(frozen=True,slots=True)
class VectorHit:
    item_id:str
    similarity:float

class InMemoryVectorIndex:
    def __init__(self,dimension:int)->None:
        if dimension<=0:raise ValueError("dimension must be positive")
        self.dimension=dimension;self._items:dict[str,np.ndarray]={}
    def upsert(self,item_id:str,vector:Iterable[float])->None:
        v=np.asarray(list(vector),dtype=np.float32)
        if v.shape!=(self.dimension,):raise ValueError(f"expected vector dimension {self.dimension}")
        self._items[item_id]=v
    def search(self,query:Iterable[float],*,limit:int=5)->tuple[VectorHit,...]:
        q=np.asarray(list(query),dtype=np.float32)
        if q.shape!=(self.dimension,):raise ValueError(f"expected vector dimension {self.dimension}")
        qn=np.linalg.norm(q)
        hits=[]
        for item_id,v in self._items.items():
            denom=qn*np.linalg.norm(v);sim=0.0 if denom==0 else float(np.dot(q,v)/denom);hits.append(VectorHit(item_id,sim))
        return tuple(sorted(hits,key=lambda h:h.similarity,reverse=True)[:limit])

PGVECTOR_BOOTSTRAP_SQL="CREATE EXTENSION IF NOT EXISTS vector"

class PostgresVectorStore:
    """Minimal pgvector-backed similarity adapter using SQLAlchemy connections.

    This avoids making the pgvector Python package mandatory: PostgreSQL's
    pgvector extension owns the vector type and distance operator.
    """
    def __init__(self, engine: object, *, dimension: int = 32, table: str = "event_vectors") -> None:
        if dimension <= 0: raise ValueError("dimension must be positive")
        if not table.replace("_", "").isalnum(): raise ValueError("unsafe table name")
        self.engine=engine;self.dimension=dimension;self.table=table
    def bootstrap(self) -> None:
        from sqlalchemy import text
        with self.engine.begin() as c:
            c.execute(text(PGVECTOR_BOOTSTRAP_SQL))
            c.execute(text(f"CREATE TABLE IF NOT EXISTS {self.table} (item_id TEXT PRIMARY KEY, embedding vector({self.dimension}) NOT NULL, metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb)"))
    @staticmethod
    def _literal(vector: Iterable[float]) -> str:
        vals=[float(x) for x in vector]
        return "["+",".join(format(x,'.9g') for x in vals)+"]"
    def upsert(self,item_id:str,vector:Iterable[float],metadata:str="{}") -> None:
        from sqlalchemy import text
        literal=self._literal(vector)
        if literal.count(',')+1!=self.dimension:raise ValueError(f"expected vector dimension {self.dimension}")
        with self.engine.begin() as c:c.execute(text(f"INSERT INTO {self.table}(item_id,embedding,metadata) VALUES (:id,CAST(:v AS vector),CAST(:m AS jsonb)) ON CONFLICT(item_id) DO UPDATE SET embedding=EXCLUDED.embedding,metadata=EXCLUDED.metadata"),{"id":item_id,"v":literal,"m":metadata})
    def search(self,query:Iterable[float],*,limit:int=5)->tuple[VectorHit,...]:
        from sqlalchemy import text
        literal=self._literal(query)
        if literal.count(',')+1!=self.dimension:raise ValueError(f"expected vector dimension {self.dimension}")
        with self.engine.connect() as c:
            rows=c.execute(text(f"SELECT item_id, 1-(embedding <=> CAST(:q AS vector)) AS similarity FROM {self.table} ORDER BY embedding <=> CAST(:q AS vector) LIMIT :lim"),{"q":literal,"lim":limit})
            return tuple(VectorHit(str(r[0]),float(r[1])) for r in rows)
