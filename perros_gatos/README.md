# 🐶🐱❓ Clasificador Perro / Gato / Ninguno

Aplicación independiente para detección de mascotas mediante IA:
1. **Backend FastAPI**: Inferencia con modelo ONNX (`pet_classifier.onnx`, ~0.26 MB) y regla de rechazo seguro (<70% certeza = Ninguno).
2. **App Móvil en Flutter**: Cámara nativa, selector de fotos de galería, desglose de porcentajes y tarjeta visual interactiva (`Perro 🐶`, `Gato 🐱`, `Ninguno ❓`).

---

## 🚀 1. Ejecución Local del Backend

```bash
# Desde la carpeta raíz del proyecto
python -m uvicorn perros_gatos.backend.app.main:app --host 0.0.0.0 --port 8001 --reload
```

- Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)
- Health check: [http://localhost:8001/health](http://localhost:8001/health)

### Pruebas automatizadas de la API:
```bash
python perros_gatos/backend/test_api.py
```

---

## 📱 2. Ejecución de la App Móvil (Flutter)

```bash
cd perros_gatos/mobile
flutter run
```

> **Consejo de Conexión:**
> - En **Emulador Android**: Usa `http://10.0.2.2:8001` (configurado por defecto).
> - En **Dispositivo Físico**: Usa el botón ⚙️ de la app e ingresa la IP local de tu PC (ej: `http://192.168.1.50:8001`).

---

## ☁️ 3. Despliegue Gratuito en la Nube

### Opción A: Hugging Face Spaces (Recomendada - 16 GB RAM Gratis)
1. En [Hugging Face](https://huggingface.co/) crea un **New Space** con SDK **Docker**.
2. Sube el contenido de `perros_gatos/backend/`.
3. ¡Listo! Tu URL pública HTTPS estará activa para consumo desde el móvil.

### Opción B: Render (Web Service Gratis)
1. Conecta tu repositorio a [Render](https://render.com/).
2. Directorio raíz: `perros_gatos/backend`.
3. **Build Command**: `pip install -r requirements.txt`.
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
