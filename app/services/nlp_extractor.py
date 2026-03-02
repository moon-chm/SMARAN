import spacy
from typing import Dict, List, Any
import logging
import subprocess

logger = logging.getLogger("smaran.nlp.extractor")

def load_spacy_model(model_name: str = "en_core_web_sm") -> Any:
    try:
        return spacy.load(model_name)
    except OSError:
        logger.info(f"Downloading spaCy model {model_name}...")
        subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)
        return spacy.load(model_name)

class NLPExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = load_spacy_model(model_name)
        
        # Simple domain vocabularies for rule-based identification 
        # (Could scale to sophisticated custom NER in the future)
        self.symptoms = {"pain", "ache", "fever", "cough", "nausea", "headache", "dizziness", "tired", "fatigue", "rash"}
        self.medicines = {"aspirin", "tylenol", "ibuprofen", "lisinopril", "metformin", "amoxicillin", "advil"}
        self.emotions = {"happy", "sad", "angry", "anxious", "calm", "frustrated", "lonely", "joyful", "excited"}
        
    def extract(self, text: str) -> Dict[str, List[Any]]:
        doc = self.nlp(text)
        
        extracted = {
            "medicines": [],
            "appointments": [],
            "symptoms": [],
            "emotions": [],
            "entities": []
        }
        
        # Process Named Entities
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "GPE", "LOC", "ORG"]:
                extracted["entities"].append({"text": ent.text, "label": ent.label_})
            elif ent.label_ in ["DATE", "TIME"]:
                extracted["appointments"].append({"text": ent.text, "label": ent.label_})
                
        # Heuristic matching for specific healthcare words (Token-based)
        for token in doc:
            lemma = token.lemma_.lower()
            
            # --- Symptoms Extraction ---
            if lemma in self.symptoms or any(symptom in token.text.lower() for symptom in self.symptoms):
                extracted["symptoms"].append({"text": token.text, "lemma": lemma})
                
            # --- Medicines Extraction ---
            elif lemma in self.medicines or any(med in token.text.lower() for med in self.medicines):
                dosage = None
                
                # Check neighbors for dosage patterns (e.g., 500mg)
                left_neighbor = token.nbor(-1) if token.i > 0 else None
                right_neighbor = token.nbor(1) if token.i < len(doc) - 1 else None
                
                for neighbor in [left_neighbor, right_neighbor]:
                    if neighbor and (neighbor.like_num or any(m in neighbor.text.lower() for m in ["mg", "ml", "pill"])):
                        dosage = neighbor.text
                        break
                        
                extracted["medicines"].append({"text": token.text, "dosage": dosage})
                
            # --- Emotions Extraction ---
            elif lemma in self.emotions or any(emo in token.text.lower() for emo in self.emotions):
                extracted["emotions"].append({"text": token.text, "lemma": lemma})
                
        return extracted
