import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import PetPredictionResponse
from .classifier import pet_classifier_instance

app = FastAPI(
    title="Clasificador Perro / Gato / Ninguno API",
    description="Backend FastAPI con modelo ONNX optimizado para distinguir perros, gatos o ninguno.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "Dog vs Cat vs Neither Classifier",
        "classes": pet_classifier_instance.classes
    }

@app.post("/predict", response_model=PetPredictionResponse)
async def predict_pet(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser una imagen.")
        
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Archivo vacío.")
        
    try:
        prediction, label_display, confidence, probabilities, message = pet_classifier_instance.predict(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en inferencia: {str(e)}")
        
    return PetPredictionResponse(
        prediction=prediction,
        label_display=label_display,
        confidence=confidence,
        probabilities=probabilities,
        message=message
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("perros_gatos.backend.app.main:app", host="0.0.0.0", port=8001, reload=True)
