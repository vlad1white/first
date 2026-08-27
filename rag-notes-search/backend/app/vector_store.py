import json
import uuid
from dataclasses import asdict, dataclass, field

import numpy as np

from . import config

VECTORS_PATH = config.DATA_DIR / "vectors.npy"
METADATA_PATH = config.DATA_DIR / "metadata.json"


@dataclass
class Chunk:
    id: str
    doc_id: str
    filename: str
    chunk_index: int
    text: str


@dataclass
class Document:
    id: str
    filename: str
    num_chunks: int


class VectorStore:
    """A small on-disk vector index: a float32 matrix plus JSON metadata.

    Good enough for a personal notes collection; not meant to scale past a
    few thousand chunks (cosine similarity is computed as one matrix product).
    """

    def __init__(self) -> None:
        self.vectors: np.ndarray = np.empty((0, 384), dtype=np.float32)
        self.chunks: list[Chunk] = []
        self._load()

    def _load(self) -> None:
        if VECTORS_PATH.exists() and METADATA_PATH.exists():
            self.vectors = np.load(VECTORS_PATH)
            with open(METADATA_PATH, encoding="utf-8") as f:
                raw = json.load(f)
            self.chunks = [Chunk(**c) for c in raw]

    def _save(self) -> None:
        np.save(VECTORS_PATH, self.vectors)
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump([asdict(c) for c in self.chunks], f, ensure_ascii=False, indent=2)

    def add_document(self, filename: str, chunk_texts: list[str], vectors: np.ndarray) -> Document:
        doc_id = str(uuid.uuid4())
        new_chunks = [
            Chunk(id=str(uuid.uuid4()), doc_id=doc_id, filename=filename, chunk_index=i, text=text)
            for i, text in enumerate(chunk_texts)
        ]
        self.chunks.extend(new_chunks)
        self.vectors = (
            vectors.copy()
            if self.vectors.shape[0] == 0
            else np.vstack([self.vectors, vectors])
        )
        self._save()
        return Document(id=doc_id, filename=filename, num_chunks=len(new_chunks))

    def list_documents(self) -> list[Document]:
        by_doc: dict[str, Document] = {}
        for chunk in self.chunks:
            if chunk.doc_id not in by_doc:
                by_doc[chunk.doc_id] = Document(id=chunk.doc_id, filename=chunk.filename, num_chunks=0)
            by_doc[chunk.doc_id].num_chunks += 1
        return list(by_doc.values())

    def delete_document(self, doc_id: str) -> bool:
        keep_idx = [i for i, c in enumerate(self.chunks) if c.doc_id != doc_id]
        if len(keep_idx) == len(self.chunks):
            return False
        self.vectors = self.vectors[keep_idx] if keep_idx else np.empty((0, 384), dtype=np.float32)
        self.chunks = [self.chunks[i] for i in keep_idx]
        self._save()
        return True

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[Chunk, float]]:
        if self.vectors.shape[0] == 0:
            return []
        # Vectors are already normalized (fastembed default), so a dot
        # product is cosine similarity.
        scores = self.vectors @ query_vector
        top_k = min(top_k, len(self.chunks))
        top_indices = np.argsort(-scores)[:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices]


store = VectorStore()
