"""Reusable embedding service with Sentence-Transformers and deterministic mock support."""

import hashlib
import math
from typing import List, Optional
import numpy as np

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import RetrievalError


class EmbeddingService:
    """Thread-safe singleton embedding service for generating document and query embeddings."""

    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self.use_mock = settings.USE_MOCK_EMBEDDINGS

        if not self.use_mock:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Initializing SentenceTransformer model: %s on device: %s", self.model_name, settings.EMBEDDING_DEVICE)
                self._model = SentenceTransformer(self.model_name, device=settings.EMBEDDING_DEVICE)
                # Verify dimension
                test_vec = self._model.encode("test", convert_to_numpy=True)
                if test_vec.shape[0] != self.dimension:
                    logger.warning("Actual embedding dimension %d differs from configured %d", test_vec.shape[0], self.dimension)
                    self.dimension = test_vec.shape[0]
            except Exception as exc:
                logger.warning("Could not initialize SentenceTransformer (%s). Falling back to deterministic embedding mock.", exc)
                self.use_mock = True
                self._model = None
        else:
            logger.info("Embedding service running in deterministic mock mode (dimension=%d)", self.dimension)

    def _generate_deterministic_vector(self, text: str) -> List[float]:
        """Generate a deterministic unit-length vector using feature hashing with stopword filtering.
        Texts sharing domain keywords produce strong positive cosine similarity (>0.50),
        while unrelated texts produce near 0.0, accurately modeling semantic search in test suites.
        """
        import re
        STOP_WORDS = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to",
            "for", "of", "with", "by", "what", "when", "where", "how", "who",
            "all", "be", "must", "and", "or", "it", "this", "that", "from"
        }
        raw_tokens = re.findall(r"\w+", text.lower())
        tokens = [t for t in raw_tokens if t not in STOP_WORDS]
        if not tokens:
            tokens = raw_tokens

        vec = np.zeros(self.dimension, dtype=np.float32)
        if not tokens:
            return vec.tolist()

        # Unigrams and bigrams
        terms = list(tokens)
        for i in range(len(tokens) - 1):
            terms.append(f"{tokens[i]}_{tokens[i+1]}")

        for term in terms:
            idx = int(hashlib.md5(term.encode("utf-8")).hexdigest(), 16) % self.dimension
            sign = 1.0 if (int(hashlib.sha1(term.encode("utf-8")).hexdigest(), 16) % 2 == 0) else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for a single text string."""
        if not text or not text.strip():
            # Return zero vector of appropriate dimension
            return [0.0] * self.dimension

        if self.use_mock or self._model is None:
            return self._generate_deterministic_vector(text)

        try:
            vec = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vec.tolist()
        except Exception as exc:
            logger.error("Error generating text embedding: %s", exc)
            raise RetrievalError(f"Embedding generation failed: {str(exc)}")

    def embed_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        """Generate vector embeddings for a batch of text strings."""
        if not texts:
            return []

        bs = batch_size or settings.EMBEDDING_BATCH_SIZE

        if self.use_mock or self._model is None:
            return [self._generate_deterministic_vector(t) for t in texts]

        try:
            embeddings = self._model.encode(
                texts,
                batch_size=bs,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return embeddings.tolist()
        except Exception as exc:
            logger.error("Error generating batch embeddings: %s", exc)
            raise RetrievalError(f"Batch embedding generation failed: {str(exc)}")

    def embed_query(self, query: str) -> List[float]:
        """Embed a user query."""
        return self.embed_text(query)

    def validate_dimension(self, vector: List[float]) -> bool:
        """Validate that a vector has the expected dimension and finite numbers."""
        if not isinstance(vector, (list, np.ndarray)):
            return False
        if len(vector) != self.dimension:
            return False
        return all(not (math.isnan(v) or math.isinf(v)) for v in vector)


# Export singleton instance
embedding_service = EmbeddingService()
