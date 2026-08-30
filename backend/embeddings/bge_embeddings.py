from typing import List
from backend.config import settings

class EmbeddingService:
    """
    Embedding service generating 384-dimensional dense vectors
    using BAAI/bge-small-en-v1.5 via fastembed (ONNX runtime - no PyTorch required).
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._load_model()
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        model = self._load_model()
        embeddings = list(model.embed(documents))
        return [e.tolist() for e in embeddings]

embedding_service = EmbeddingService()
