import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class BaseGraphNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_type: str = Field(..., description="e.g., voice, text, external_api")
    last_reinforced_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    elder_id: str = Field(..., description="Used for per-elder isolation in queries")

class ElderNode(BaseGraphNode):
    name: str
    age: Optional[int] = None

class CaregiverNode(BaseGraphNode):
    name: str

class MedicineNode(BaseGraphNode):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None

class AppointmentNode(BaseGraphNode):
    title: str
    datetime_str: str = Field(alias="datetime")

class SymptomNode(BaseGraphNode):
    name: str
    severity: Optional[int] = Field(default=1, ge=1, le=10)

class MoodNode(BaseGraphNode):
    state: str
    intensity: Optional[int] = Field(default=5, ge=1, le=10)

class ContentItemNode(BaseGraphNode):
    title: str
    url: Optional[str] = None
    media_type: str

class EmotionalMemoryNode(BaseGraphNode):
    description: str
    emotion_tag: str

class MemoryIngestRequest(BaseModel):
    elder_id: str
    text: str
    source_type: str = "text"
    
class MindmapResponse(BaseModel):
    elder_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
