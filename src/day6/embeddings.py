"""Real embedding provider: a local Sentence Transformers model (no API key, no cost)."""
from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Sentence Transformers adapter. Fails loudly if the model cannot load; never mocks.

    Documents and queries are encoded the same way (this model has no query/document
    prefixes) and L2-normalized, so cosine distance in pgvector is well defined.
    """

    def __init__(self, model_name: str, device: str | None = None, batch_size: int = 32) -> None:
        from sentence_transformers import SentenceTransformer  # heavy import, keep local

        self.model_name = model_name
        self.batch_size = batch_size
        self.model = SentenceTransformer(model_name, device=device)
        get_dim = getattr(self.model, "get_embedding_dimension", None) or self.model.get_sentence_embedding_dimension
        dims = get_dim()
        if not dims:
            raise RuntimeError(f"could not determine embedding size for {model_name}")
        self.dimensions = int(dims)
        self.max_tokens = int(self.model.max_seq_length)
        self.device = str(self.model.device)

    def info(self) -> dict:
        import sentence_transformers
        import torch

        return {
            "provider": "local sentence-transformers",
            "model": self.model_name,
            "dimensions": self.dimensions,
            "max_seq_length_tokens": self.max_tokens,
            "device": self.device,
            "normalize_embeddings": True,
            "query_document_handling": "identical encoding, no prefixes",
            "sentence_transformers": sentence_transformers.__version__,
            "torch": torch.__version__,
            "cost_usd": 0,
        }

    def token_counts(self, texts: list[str]) -> list[int]:
        return [len(ids) for ids in self.model.tokenizer(texts, add_special_tokens=True)["input_ids"]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                                    convert_to_numpy=True, show_progress_bar=False)
        if len(vectors) != len(texts):
            raise RuntimeError("embedding count does not match input count")
        return vectors.tolist()

    def embed_query(self, question: str) -> list[float]:
        return self.embed_documents([question])[0]
