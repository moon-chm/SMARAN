from typing import List, Dict, Any
from app.graph.schema import MedicineNode, AppointmentNode, SymptomNode, EmotionalMemoryNode

def classify_entities(extracted_data: Dict[str, List[Any]], elder_id: str, source_type: str = "text") -> List[Any]:
    """
    Maps spaCy extracted entities into Neo4j graph nodes.
    Assigns confidence scores and structures them for ingestion.
    """
    nodes = []
    
    # 1. Medicines -> MedicineNode
    for med in extracted_data.get("medicines", []):
        # Higher confidence if dosage is also identified
        confidence = 0.9 if med.get("dosage") else 0.7
        nodes.append(MedicineNode(
            elder_id=elder_id,
            name=med["text"],
            dosage=med.get("dosage"),
            confidence_score=confidence,
            source_type=source_type
        ))
        
    # 2. Appointments -> AppointmentNode
    # In a real app, 'datetime' parsing would map 'Friday at 5 PM' to an ISO string
    # For Phase 3, we store the natural language string directly.
    for apt in extracted_data.get("appointments", []):
        nodes.append(AppointmentNode(
            elder_id=elder_id,
            title=f"Appointment on {apt['text']}",
            datetime=apt["text"],
            confidence_score=0.85,
            source_type=source_type
        ))
        
    # 3. Symptoms -> SymptomNode
    for sym in extracted_data.get("symptoms", []):
        nodes.append(SymptomNode(
            elder_id=elder_id,
            name=sym["lemma"],
            confidence_score=0.8,
            source_type=source_type
        ))
        
    # 4. Emotions -> EmotionalMemoryNode
    for emo in extracted_data.get("emotions", []):
        nodes.append(EmotionalMemoryNode(
            elder_id=elder_id,
            description=f"Felt {emo['text']}",
            emotion_tag=emo["lemma"].capitalize(),
            confidence_score=0.85,
            source_type=source_type
        ))
        
    return nodes
