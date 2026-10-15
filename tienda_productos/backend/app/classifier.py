import os
import json
from io import BytesIO
from typing import Tuple, Dict
import numpy as np
from PIL import Image
import onnxruntime as ort

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "product_model.onnx")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "labels.json")

class ProductClassifier:
    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH, confidence_threshold=0.65):
        self.confidence_threshold = confidence_threshold
        
        # Load labels
        with open(labels_path, "r", encoding="utf-8") as f:
            self.classes = json.load(f)["classes"]
            
        # Initialize ONNX Runtime session
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        
        # ImageNet normalization constants
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = np.transpose(arr, (2, 0, 1)) # HWC -> CHW
        arr = np.expand_dims(arr, 0)       # Add batch dimension -> (1, 3, 224, 224)
        arr = (arr - self.mean) / self.std
        return arr

    def predict(self, image_bytes: bytes) -> Tuple[bool, str, float, Dict[str, float]]:
        """
        Executes inference.
        Returns:
            (recognized: bool, predicted_class: str, confidence: float, all_probabilities: dict)
        """
        tensor = self.preprocess_image(image_bytes)
        outputs = self.session.run(None, {self.input_name: tensor})[0][0]
        
        # Softmax
        exp_logits = np.exp(outputs - np.max(outputs))
        probabilities = exp_logits / np.sum(exp_logits)
        
        top_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[top_idx])
        predicted_class = self.classes[top_idx]
        
        prob_dict = {self.classes[i]: round(float(probabilities[i]), 4) for i in range(len(self.classes))}
        
        is_recognized = confidence >= self.confidence_threshold
        return is_recognized, predicted_class, round(confidence, 4), prob_dict

# Singleton instance
classifier_instance = ProductClassifier()
