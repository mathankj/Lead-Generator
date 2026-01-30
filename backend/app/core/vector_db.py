"""ChromaDB vector database client for semantic search."""

import os
from functools import lru_cache
from typing import Optional, List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class VectorDBClient:
    """ChromaDB client wrapper for lead embeddings and semantic search."""

    def __init__(self, persist_directory: str):
        """Initialize ChromaDB client with persistence."""
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        self._leads_collection: Optional[chromadb.Collection] = None

    @property
    def leads_collection(self) -> chromadb.Collection:
        """Get or create the leads collection."""
        if self._leads_collection is None:
            self._leads_collection = self.client.get_or_create_collection(
                name="leads",
                metadata={"description": "Lead company embeddings for semantic search"},
            )
        return self._leads_collection

    def add_lead_embedding(
        self,
        lead_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a lead's text embedding to the collection.

        Args:
            lead_id: Unique identifier for the lead
            text: Text to embed (company description, tech stack, etc.)
            metadata: Additional metadata to store
        """
        self.leads_collection.add(
            ids=[lead_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search_similar_leads(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar leads using semantic similarity.

        Args:
            query: Search query text
            n_results: Number of results to return
            where: Optional filter conditions

        Returns:
            List of matching leads with distances
        """
        results = self.leads_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        # Format results
        leads = []
        if results["ids"] and results["ids"][0]:
            for i, lead_id in enumerate(results["ids"][0]):
                leads.append({
                    "id": lead_id,
                    "document": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
        return leads

    def delete_lead(self, lead_id: str) -> None:
        """Delete a lead from the vector store."""
        self.leads_collection.delete(ids=[lead_id])

    def get_collection_count(self) -> int:
        """Get the number of items in the leads collection."""
        return self.leads_collection.count()

    def is_healthy(self) -> bool:
        """Check if ChromaDB is working."""
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False


# Singleton instance
_vector_db_client: Optional[VectorDBClient] = None


@lru_cache
def get_vector_db() -> VectorDBClient:
    """Get the vector database client instance."""
    global _vector_db_client
    if _vector_db_client is None:
        _vector_db_client = VectorDBClient(settings.chromadb_path)
    return _vector_db_client
