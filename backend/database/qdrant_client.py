from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.config import settings

class QdrantVectorStore:
    """
    Qdrant vector database store for jobs and resume embeddings.
    Uses BAAI/bge-small-en-v1.5 (Vector dimension: 384).
    """
    JOBS_COLLECTION = "jobs_collection"
    RESUMES_COLLECTION = "resumes_collection"
    VECTOR_SIZE = 384  # bge-small-en-v1.5 dimension size

    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )

    def init_collections(self):
        """Creates vector collections if they do not exist."""
        existing_collections = [c.name for c in self.client.get_collections().collections]

        if self.JOBS_COLLECTION not in existing_collections:
            self.client.create_collection(
                collection_name=self.JOBS_COLLECTION,
                vectors_config=qmodels.VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=qmodels.Distance.COSINE
                )
            )

        if self.RESUMES_COLLECTION not in existing_collections:
            self.client.create_collection(
                collection_name=self.RESUMES_COLLECTION,
                vectors_config=qmodels.VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=qmodels.Distance.COSINE
                )
            )

    def upsert_job_vector(self, job_id: str, vector: List[float], payload: Dict[str, Any]):
        """Upserts a job vector into Qdrant."""
        self.client.upsert(
            collection_name=self.JOBS_COLLECTION,
            points=[
                qmodels.PointStruct(
                    id=job_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search_similar_jobs(self, query_vector: List[float], limit: int = 30) -> List[Dict[str, Any]]:
        """Searches for top N similar jobs using Cosine distance."""
        results = self.client.search(
            collection_name=self.JOBS_COLLECTION,
            query_vector=query_vector,
            limit=limit
        )
        return [
            {
                "job_id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]

qdrant_store = QdrantVectorStore()
