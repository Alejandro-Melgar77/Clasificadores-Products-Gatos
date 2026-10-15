# 🛒 Tienda Inteligente - Clasificador de Productos con IA

Aplicación completa compuesta por:
1. **Backend FastAPI**: Inferencia ultraligera con modelo ONNX (`product_model.onnx`, ~0.26 MB) y base de datos SQLite con inventario en tiempo real (stock, precio, descripción, SKU).
2. **App Móvil en Flutter**: Escáner de productos con cámara nativa, selector de galería, visualización de stock y catálogo interactivo.

---

## 📦 Productos Soportados (8 Clases)

1. `cocacola`: **Coca-Cola Original 350ml** (Bs 8.00 | Stock: 45)
2. `oreo`: **Galletas Oreo Clásicas 108g** (Bs 6.50 | Stock: 30)
3. `lays`: **Papas Fritas Lay's Clásicas 140g** (Bs 10.00 | Stock: 22)
4. `nescafe`: **Café Nescafé Clásico 100g** (Bs 28.00 | Stock: 15)
5. `leche_pil`: **Leche Pasteurizada Pil 1L** (Bs 6.00 | Stock: 50)
6. `agua_mineral`: **Agua Mineral Vital sin Gas 600ml** (Bs 5.00 | Stock: 60)
7. `chocolate_block`: **Chocolate Cofler Block con Maní 150g** (Bs 12.50 | Stock: 18)
8. `cerveza_pacena`: **Cerveza Paceña Pilsener 355ml** (Bs 11.00 | Stock: 35)

---

## 🚀 1. Ejecución Local del Backend

```bash
# Desde la carpeta raíz del proyecto
python -m uvicorn tienda_productos.backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Documentación interactiva Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Verificación de estado: [http://localhost:8000/health](http://localhost:8000/health)
- Catálogo de productos: [http://localhost:8000/products](http://localhost:8000/products)

### Pruebas automatizadas de la API:
```bash
python tienda_productos/backend/test_api.py
```

---

## 📱 2. Ejecución de la App Móvil (Flutter)

```bash
cd tienda_productos/mobile
flutter run
```

> **Consejo de Conexión:**
> - En **Emulador Android**: Usa `http://10.0.2.2:8000` (configurado por defecto).
> - En **Dispositivo Físico** (conectado por USB o Wi-Fi): Pulsa el ícono de engranaje ⚙️ en la app e ingresa la IP local de tu PC (ej: `http://192.168.1.50:8000`).
> - En **Navegador Chrome**: `flutter run -d chrome` (usa `http://localhost:8000`).

---

## ☁️ 3. Despliegue Gratuito en la Nube

### Opción A: Hugging Face Spaces (Recomendada - 16 GB RAM Gratis)
1. Crea una cuenta en [Hugging Face](https://huggingface.co/).
2. Ve a **New Space** -> Elige **Docker** (Blank).
3. Sube los archivos de `tienda_productos/backend/`:
   - `Dockerfile`
   - `requirements.txt`
   - `app/`
   - `models/`
   - `ml/labels.json`
   - `data/`
4. En cuestión de 2 minutos tu API estará pública con HTTPS: `https://<tu-usuario>-<nombre-space>.hf.space`.
5. Coloca esa URL en el botón de ajustes ⚙️ de la app móvil.

### Opción B: Render (Web Service Gratis - 512 MB RAM)
Gracias a que convertimos el modelo a **ONNX**, el consumo en producción es de solo **~80 MB RAM**:
1. Conecta tu repositorio de GitHub a [Render](https://render.com/).
2. Crea un **New Web Service** apuntando al directorio `tienda_productos/backend`.
3. Configura:
   - **Environment**: `Python 3` (o `Docker`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. Tu backend quedará desplegado gratuitamente con URL HTTPS `https://<tu-servicio>.onrender.com`.
