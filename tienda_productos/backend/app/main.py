import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Product, PredictionResponse, StockUpdateRequest
from .database import get_all_products, get_product_by_id, get_product_by_class_id, update_product_stock
from .classifier import classifier_instance

app = FastAPI(
    title="API de Tienda - Reconocimiento de Productos con IA",
    description="Backend FastAPI con modelo ONNX optimizado para reconocimiento visual de productos e inventario.",
    version="1.0.0"
)

# Enable CORS for Flutter mobile apps and web
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
        "service": "Store Product Classifier API",
        "classes_count": len(classifier_instance.classes),
        "supported_products": classifier_instance.classes
    }

@app.get("/products", response_model=List[Product])
def list_products():
    """Retorna todos los productos del inventario con su stock y precio actual."""
    products = get_all_products()
    return products

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Retorna el detalle completo de un producto por su ID."""
    prod = get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@app.put("/products/{product_id}/stock", response_model=Product)
def update_stock(product_id: int, req: StockUpdateRequest):
    """Actualiza la cantidad en stock del producto."""
    success = update_product_stock(product_id, req.stock)
    if not success:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return get_product_by_id(product_id)

@app.post("/predict", response_model=PredictionResponse)
async def predict_product(file: UploadFile = File(...)):
    """
    Recibe la fotografía tomada con la cámara nativa del celular.
    Ejecuta inferencia ONNX y retorna la información completa del producto (stock, precio, etc.).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser una imagen (JPEG/PNG/WEBP).")
        
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Archivo de imagen vacío.")
        
    try:
        is_recognized, class_id, confidence, probabilities = classifier_instance.predict(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el procesamiento del modelo: {str(e)}")
        
    if is_recognized:
        product_data = get_product_by_class_id(class_id)
        if product_data:
            return PredictionResponse(
                recognized=True,
                class_id=class_id,
                confidence=confidence,
                product=Product(**product_data),
                message=f"Producto reconocido exitosamente: {product_data['name']}",
                probabilities=probabilities
            )
            
    # If not recognized or confidence below threshold
    return PredictionResponse(
        recognized=False,
        class_id=class_id,
        confidence=confidence,
        product=None,
        message="Producto no identificado en el inventario o imagen poco clara. Por favor intente enfocar mejor.",
        probabilities=probabilities
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tienda_productos.backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
