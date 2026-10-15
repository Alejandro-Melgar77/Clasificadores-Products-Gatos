import os
import sys
import json
import torch
import torch.nn as nn
from torchvision import models
import onnxruntime as ort
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def export():
    labels_file = "tienda_productos/backend/ml/labels.json"
    with open(labels_file, "r", encoding="utf-8") as f:
        classes = json.load(f)["classes"]
    num_classes = len(classes)
    
    pth_path = "tienda_productos/backend/models/product_model.pth"
    onnx_path = "tienda_productos/backend/models/product_model.onnx"
    
    print(f"[*] Cargando modelo entrenado desde: {pth_path}")
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, num_classes)
    )
    
    state_dict = torch.load(pth_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    
    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=False)
    
    print(f"[*] Exportando a ONNX: {onnx_path}")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"✔ ONNX generado exitosamente. Tamaño: {size_mb:.2f} MB")
    
    # Verify with onnxruntime
    session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    out = session.run(None, {input_name: dummy_input.numpy()})
    print(f"✔ Verificación ONNX Runtime exitosa. Salida shape: {out[0].shape}")

if __name__ == "__main__":
    export()
