import torch
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List
import numpy as np

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._model = None
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer(
                settings.EMBEDDING_MODEL_NAME, 
                device=device
            )
        return self._model

    async def generate_embedding(self, text: str) -> List[float]:
        # Running in a threadpool might be better for heavy CPU tasks
        # but for now we'll do it directly as it's a service
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

embedding_service = EmbeddingService()
