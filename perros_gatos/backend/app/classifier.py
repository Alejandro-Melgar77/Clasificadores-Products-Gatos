import os
import json
from io import BytesIO
from typing import Tuple, Dict
import numpy as np
from PIL import Image
import onnxruntime as ort

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "pet_classifier.onnx")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "labels.json")

DISPLAY_MAP = {
    "perro": "Perro 🐶",
    "gato": "Gato 🐱",
    "ninguno": "Ninguno ❓"
}

class PetClassifier:
    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH, confidence_threshold=0.70):
        self.confidence_threshold = confidence_threshold
        with open(labels_path, "r", encoding="utf-8") as f:
            self.classes = json.load(f)["classes"]
            
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = np.transpose(arr, (2, 0, 1))
        arr = np.expand_dims(arr, 0)
        arr = (arr - self.mean) / self.std
        return arr

    def predict(self, image_bytes: bytes) -> Tuple[str, str, float, Dict[str, float], str]:
        tensor = self.preprocess_image(image_bytes)
        outputs = self.session.run(None, {self.input_name: tensor})[0][0]
        
        exp = np.exp(outputs - np.max(outputs))
        probabilities = exp / np.sum(exp)
        
        prob_dict = {self.classes[i]: round(float(probabilities[i]), 4) for i in range(len(self.classes))}
        top_idx = int(np.argmax(probabilities))
        top_confidence = float(probabilities[top_idx])
        top_class = self.classes[top_idx]
        
        # Dual rejection rule:
        # 1. If predicted class is 'ninguno'
        # 2. Or if predicted class is perro/gato but confidence < threshold (70%)
        if top_class == "ninguno" or top_confidence < self.confidence_threshold:
            final_pred = "ninguno"
            label_display = DISPLAY_MAP["ninguno"]
            msg = "La imagen no corresponde a un perro ni a un gato (o la imagen no es lo suficientemente nítida)."
            # Show confidence of being 'neither' or 1 - max(dog, cat)
            final_conf = prob_dict.get("ninguno", 1.0 - top_confidence)
            if top_class != "ninguno":
                final_conf = max(final_conf, round(1.0 - top_confidence, 4))
        else:
            final_pred = top_class
            label_display = DISPLAY_MAP.get(top_class, top_class.capitalize())
            final_conf = top_confidence
            msg = f"¡Es un {top_class}! Identificado con alta certeza."
            
        return final_pred, label_display, round(final_conf, 4), prob_dict, msg

pet_classifier_instance = PetClassifier()
