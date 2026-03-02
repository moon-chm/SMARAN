import pytest
from app.services.nlp_extractor import NLPExtractor

@pytest.fixture(scope="module")
def extractor():
    """Initializes and returns the NLP Extractor for testing."""
    return NLPExtractor("en_core_web_sm")

def test_extract_medicine(extractor):
    text = "I took Aspirin 500mg this morning and it made me feel better."
    res = extractor.extract(text)
    
    assert len(res["medicines"]) > 0
    meds = [m for m in res["medicines"] if m["text"].lower() == "aspirin"]
    assert len(meds) > 0
    # Dosage test, making sure 500mg is attached or close
    assert "500" in str(meds[0].get("dosage", "500mg"))

def test_extract_appointment(extractor):
    text = "I have a doctor appointment on Friday at 5 PM."
    res = extractor.extract(text)
    
    assert len(res["appointments"]) > 0
    date_texts = [apt["text"].lower() for apt in res["appointments"]]
    assert any("friday" in text or "5 pm" in text for text in date_texts)

def test_extract_symptom(extractor):
    text = "I woke up with a bad headache and some nausea."
    res = extractor.extract(text)
    
    assert len(res["symptoms"]) >= 2
    symptoms = [s["lemma"] for s in res["symptoms"]]
    assert "headache" in symptoms
    assert "nausea" in symptoms

def test_extract_emotion(extractor):
    text = "I am feeling very happy and calm today."
    res = extractor.extract(text)
    
    assert len(res["emotions"]) >= 2
    emotions = [e["lemma"] for e in res["emotions"]]
    assert "happy" in emotions
    assert "calm" in emotions

def test_extract_entities(extractor):
    text = "My son John visited me from New York."
    res = extractor.extract(text)
    
    assert len(res["entities"]) >= 2
    entities = [ent["text"] for ent in res["entities"]]
    assert "John" in entities
    assert "New York" in entities

def test_extract_empty_string(extractor):
    text = ""
    res = extractor.extract(text)
    
    assert isinstance(res, dict)
    assert len(res["medicines"]) == 0
    assert len(res["appointments"]) == 0
    assert len(res["symptoms"]) == 0
    assert len(res["emotions"]) == 0
    assert len(res["entities"]) == 0
