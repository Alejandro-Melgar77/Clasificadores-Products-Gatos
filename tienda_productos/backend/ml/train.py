import os
import sys
import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def train_and_export():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Dispositivo de entrenamiento: {device}")
    
    data_dir = "tienda_productos/backend/data/dataset"
    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")
    
    # Preprocessing pipelines (standard ImageNet normalization for MobileNetV2)
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    
    image_datasets = {
        'train': datasets.ImageFolder(train_dir, data_transforms['train']),
        'val': datasets.ImageFolder(val_dir, data_transforms['val'])
    }
    
    dataloaders = {
        'train': torch.utils.data.DataLoader(image_datasets['train'], batch_size=16, shuffle=True, num_workers=0),
        'val': torch.utils.data.DataLoader(image_datasets['val'], batch_size=16, shuffle=False, num_workers=0)
    }
    
    class_names = image_datasets['train'].classes
    num_classes = len(class_names)
    print(f"[*] Clases detectadas ({num_classes}): {class_names}")
    
    # Save labels json
    labels_file = "tienda_productos/backend/ml/labels.json"
    with open(labels_file, "w", encoding="utf-8") as f:
        json.dump({"classes": class_names}, f, indent=2)
    print(f"✔ Mapeo guardado en {labels_file}")
    
    # Load Pre-trained MobileNetV2
    try:
        weights = models.MobileNet_V2_Weights.DEFAULT
        model = models.mobilenet_v2(weights=weights)
    except Exception:
        model = models.mobilenet_v2(pretrained=True)
        
    # Replace final classification head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, num_classes)
    )
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)
    
    num_epochs = 5
    print("\n" + "=" * 60)
    print(f"INICIANDO TRANSFER LEARNING CON MOBILENET-V2 ({num_epochs} ÉPOCAS)")
    print("=" * 60)
    
    best_acc = 0.0
    models_dir = "tienda_productos/backend/models"
    os.makedirs(models_dir, exist_ok=True)
    best_pth_path = os.path.join(models_dir, "product_model.pth")
    onnx_path = os.path.join(models_dir, "product_model.onnx")
    
    start_time = time.time()
    
    for epoch in range(num_epochs):
        print(f"\n--- Época {epoch + 1}/{num_epochs} ---")
        
        # Training Phase
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels in dataloaders['train']:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
        scheduler.step()
        epoch_loss = running_loss / len(image_datasets['train'])
        epoch_acc = running_corrects.double() / len(image_datasets['train'])
        print(f"  [Train] Loss: {epoch_loss:.4f} | Precisión: {epoch_acc * 100:.2f}%")
        
        # Validation Phase
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        
        with torch.no_grad():
            for inputs, labels in dataloaders['val']:
                inputs = inputs.to(device)
                labels = labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
                
        val_loss = val_loss / len(image_datasets['val'])
        val_acc = val_corrects.double() / len(image_datasets['val'])
        print(f"  [Val]   Loss: {val_loss:.4f} | Precisión: {val_acc * 100:.2f}%")
        
        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), best_pth_path)
            
    total_time = time.time() - start_time
    print(f"\n✔ Entrenamiento completado en {total_time:.1f}s. Mejor precisión en validación: {best_acc * 100:.2f}%")
    print(f"✔ Checkpoint guardado en {best_pth_path}")
    
    # Export to ONNX
    print("\n" + "=" * 60)
    print("EXPORTANDO MODELO A ONNX (OPTIMIZADO PARA PRODUCCIÓN)")
    print("=" * 60)
    
    model.load_state_dict(torch.load(best_pth_path, map_location="cpu"))
    model.eval()
    model.to("cpu")
    
    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=False)
    
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
    
    onnx_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"✔ Modelo exportado exitosamente a: {onnx_path}")
    print(f"✔ Tamaño del modelo ONNX: {onnx_size_mb:.2f} MB (Ultraligero para Render / Hugging Face)")
    
    # Validate with ONNX Runtime
    import onnxruntime as ort
    session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    
    # Test inference on dummy array
    dummy_np = dummy_input.numpy()
    ort_outs = session.run(None, {input_name: dummy_np})
    print(f"✔ Inferencia ONNX verificada. Salida shape: {ort_outs[0].shape}")
    print("=" * 60)
    print("LISTO PARA INFERENCIA EN FASTAPI")
    print("=" * 60)

if __name__ == "__main__":
    train_and_export()
