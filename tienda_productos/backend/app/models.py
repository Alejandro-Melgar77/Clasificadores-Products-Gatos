from pydantic import BaseModel, Field
from typing import Optional, Dict

class Product(BaseModel):
    id: int
    class_id: str
    sku: str
    name: str
    category: str
    price: float
    currency: str = "Bs"
    stock: int
    description: str
    barcode: str
    image_url: Optional[str] = None

class PredictionResponse(BaseModel):
    recognized: bool
    class_id: Optional[str] = None
    confidence: float
    product: Optional[Product] = None
    message: str
    probabilities: Dict[str, float] = Field(default_factory=dict)

class StockUpdateRequest(BaseModel):
    stock: int
