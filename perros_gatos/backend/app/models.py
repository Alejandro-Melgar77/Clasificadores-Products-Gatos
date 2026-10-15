from pydantic import BaseModel, Field
from typing import Dict

class PetPredictionResponse(BaseModel):
    prediction: str # 'perro' | 'gato' | 'ninguno'
    label_display: str # 'Perro 🐶' | 'Gato 🐱' | 'Ninguno ❓'
    confidence: float
    probabilities: Dict[str, float] = Field(default_factory=dict)
    message: str
