import faiss
import numpy as np
import os
import pickle
import logging
from typing import List, Tuple
from app.retrieval.embedder import embedder

logger = logging.getLogger("smaran.retrieval.faiss")

# Ensure the FAISS indices directory exists
INDEX_DIR = os.path.join(os.getcwd(), "data", "faiss_indices")
os.makedirs(INDEX_DIR, exist_ok=True)

class FaissIndexManager:
    def __init__(self, vector_dim: int = embedder.vector_size):
        self.vector_dim = vector_dim
        # memory cache for loaded indices: elder_id -> (faiss_index, list_of_node_ids)
        self.indices = {}

    def _get_index_paths(self, elder_id: str) -> Tuple[str, str]:
        idx_path = os.path.join(INDEX_DIR, f"{elder_id}.index")
        map_path = os.path.join(INDEX_DIR, f"{elder_id}_map.pkl")
        return idx_path, map_path

    def load_index(self, elder_id: str):
        if elder_id in self.indices:
            return

        idx_path, map_path = self._get_index_paths(elder_id)
        
        if os.path.exists(idx_path) and os.path.exists(map_path):
            try:
                index = faiss.read_index(idx_path)
                with open(map_path, "rb") as f:
                    node_id_map = pickle.load(f)
                self.indices[elder_id] = {"index": index, "map": node_id_map}
                logger.info(f"Loaded existing FAISS index for {elder_id}")
            except Exception as e:
                logger.error(f"Failed to load FAISS index for {elder_id}: {e}")
                self._create_new_index(elder_id)
        else:
            self._create_new_index(elder_id)

    def _create_new_index(self, elder_id: str):
        # We use IndexFlatIP for cosine similarity since vectors are normalized
        index = faiss.IndexFlatIP(self.vector_dim)
        self.indices[elder_id] = {"index": index, "map": []}
        logger.info(f"Created new FAISS index for {elder_id}")

    def save_index(self, elder_id: str):
        if elder_id not in self.indices:
            return
            
        data = self.indices[elder_id]
        idx_path, map_path = self._get_index_paths(elder_id)
        
        faiss.write_index(data["index"], idx_path)
        with open(map_path, "wb") as f:
            pickle.dump(data["map"], f)

    def add_vector(self, elder_id: str, node_id: str, vector: np.ndarray):
        """Adds a normalized vector and its Neo4j node ID to the FAISS index."""
        self.load_index(elder_id)
        data = self.indices[elder_id]
        
        # FAISS requires 2D array
        vec_2d = np.expand_dims(vector, axis=0)
        
        data["index"].add(vec_2d)
        data["map"].append(node_id)
        
        # In a high-throughput env, we might save periodically. We save eagerly here.
        self.save_index(elder_id)

    def search(self, elder_id: str, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Returns a list of (node_id, similarity_score).
        """
        self.load_index(elder_id)
        data = self.indices[elder_id]
        index = data["index"]
        
        if index.ntotal == 0:
            return []
            
        # Limit top_k to the number of elements in index
        k = min(top_k, index.ntotal)
        if k == 0:
            return []

        vec_2d = np.expand_dims(query_vector, axis=0)
        distances, indices = index.search(vec_2d, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # Indicates a valid FAISS result
                node_id = data["map"][idx]
                score = distances[0][i]
                results.append((node_id, float(score)))
                
        return results

faiss_manager = FaissIndexManager()
