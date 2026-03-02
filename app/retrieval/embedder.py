import spacy
import numpy as np
from app.services.nlp_extractor import load_spacy_model

class Embedder:
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Using spaCy's internal vectors.
        Note: en_core_web_sm does not have true static word vectors, it uses context-sensitive tensors.
        For production, en_core_web_md or lg (or SentenceTransformers) is recommended.
        We will use the document vector which is an average of the sub-tensors in 'sm'.
        """
        self.nlp = load_spacy_model(model_name)
        # Check vector size (typically 96 for en_core_web_sm, 300 for md/lg)
        self.vector_size = self.nlp("test").vector.shape[0]

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a string into a normalized 1D numpy array.
        """
        doc = self.nlp(text)
        vector = doc.vector
        
        # Normalize the vector for cosine similarity via inner product
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.astype(np.float32)

embedder = Embedder()
