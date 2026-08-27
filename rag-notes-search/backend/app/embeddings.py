from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding

from . import config


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    # Loaded once per process; fastembed caches the ONNX model on disk
    # after the first download, so subsequent starts are fast and offline.
    return TextEmbedding(model_name=config.EMBEDDING_MODEL)


def embed_passages(texts: list[str]) -> np.ndarray:
    """Embed document chunks (stored side of the search index)."""
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    model = _get_model()
    vectors = list(model.passage_embed(texts))
    return np.array(vectors, dtype=np.float32)


def embed_query(text: str) -> np.ndarray:
    """Embed a search query using the model's asymmetric query prefix."""
    model = _get_model()
    return np.array(next(model.query_embed([text])), dtype=np.float32)
