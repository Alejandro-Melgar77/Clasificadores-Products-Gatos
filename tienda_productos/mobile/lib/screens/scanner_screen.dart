import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../models/product_model.dart';
import 'product_detail_sheet.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final ImagePicker _picker = ImagePicker();
  final ApiService _api = ApiService();

  bool _isLoading = false;
  bool? _isServerOnline;
  String _statusMessage = 'Apunta la cámara a un producto o sube una imagen';
  Uint8List? _previewImageBytes;

  @override
  void initState() {
    super.initState();
    _checkServer();
  }

  Future<void> _checkServer() async {
    final online = await _api.checkHealth();
    if (mounted) {
      setState(() => _isServerOnline = online);
    }
  }

  Future<void> _pickAndProcessImage(ImageSource source) async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (pickedFile == null) return;

      final bytes = await pickedFile.readAsBytes();
      setState(() {
        _previewImageBytes = bytes;
        _isLoading = true;
        _statusMessage = 'Analizando producto con IA...';
      });

      final PredictionResponse result = await _api.predictProduct(pickedFile);

      if (!mounted) return;
      setState(() => _isLoading = false);

      if (result.recognized && result.product != null) {
        setState(() {
          _statusMessage = '¡Producto encontrado!';
        });
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          builder: (ctx) => ProductDetailSheet(
            product: result.product!,
            confidence: result.confidence,
            imageBytes: _previewImageBytes,
          ),
        );
      } else {
        setState(() {
          _statusMessage = result.message;
        });
        _showUnrecognizedDialog(result.message, result.confidence);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _statusMessage = 'Error de conexión con el backend: $e';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  void _showUnrecognizedDialog(String message, double confidence) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        icon: const Icon(Icons.help_outline, size: 48, color: Colors.orange),
        title: const Text('Producto No Reconocido'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message),
            const SizedBox(height: 12),
            Text(
              'Confianza de predicción: ${(confidence * 100).toStringAsFixed(1)}% (mínimo requerido 65%)',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  void _showConfigServerDialog() {
    final controller = TextEditingController(text: _api.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Configurar Backend FastAPI'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Ingresa la URL del servidor FastAPI (local o desplegado en Render/HuggingFace):',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'http://192.168.1.50:8000',
                labelText: 'URL Base',
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                ActionChip(
                  label: const Text('Emulador (10.0.2.2)'),
                  onPressed: () => controller.text = 'http://10.0.2.2:8000',
                ),
                ActionChip(
                  label: const Text('Web/Local (localhost)'),
                  onPressed: () => controller.text = 'http://localhost:8000',
                ),
              ],
            )
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () {
              _api.setBaseUrl(controller.text.trim());
              Navigator.pop(ctx);
              _checkServer();
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isOnline = _isServerOnline ?? false;

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.storefront, color: Colors.teal),
            SizedBox(width: 8),
            Text('Tienda Inteligente', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        elevation: 0,
        backgroundColor: Colors.white,
        actions: [
          // Connection status pill
          GestureDetector(
            onTap: _checkServer,
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: isOnline ? Colors.green.shade50 : Colors.red.shade50,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: isOnline ? Colors.green.shade300 : Colors.red.shade300),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircleAvatar(
                    radius: 4,
                    backgroundColor: isOnline ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    isOnline ? 'Online' : 'Offline',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isOnline ? Colors.green.shade800 : Colors.red.shade800,
                    ),
                  ),
                ],
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Configurar servidor',
            onPressed: _showConfigServerDialog,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Scanner Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      // Camera viewfinder / preview box
                      Container(
                        height: 280,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFF334155), width: 2),
                        ),
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            if (_previewImageBytes != null)
                              ClipRRect(
                                borderRadius: BorderRadius.circular(14),
                                child: Image.memory(
                                  _previewImageBytes!,
                                  width: double.infinity,
                                  height: double.infinity,
                                  fit: BoxFit.cover,
                                ),
                              )
                            else
                              Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.qr_code_scanner, size: 70, color: Colors.teal.shade300),
                                  const SizedBox(height: 12),
                                  const Text(
                                    'Encuadra el producto aquí',
                                    style: TextStyle(color: Colors.white70, fontSize: 14),
                                  ),
                                  const SizedBox(height: 4),
                                  const Text(
                                    'Coca-Cola, Oreo, Lay\'s, Nescafé, Pil, etc.',
                                    style: TextStyle(color: Colors.white38, fontSize: 12),
                                  ),
                                ],
                              ),

                            // Corner guides
                            Positioned(
                              top: 16,
                              left: 16,
                              child: Container(width: 24, height: 24, decoration: const BoxDecoration(border: Border(top: BorderSide(color: Colors.teal, width: 3), left: BorderSide(color: Colors.teal, width: 3)))),
                            ),
                            Positioned(
                              top: 16,
                              right: 16,
                              child: Container(width: 24, height: 24, decoration: const BoxDecoration(border: Border(top: BorderSide(color: Colors.teal, width: 3), right: BorderSide(color: Colors.teal, width: 3)))),
                            ),
                            Positioned(
                              bottom: 16,
                              left: 16,
                              child: Container(width: 24, height: 24, decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.teal, width: 3), left: BorderSide(color: Colors.teal, width: 3)))),
                            ),
                            Positioned(
                              bottom: 16,
                              right: 16,
                              child: Container(width: 24, height: 24, decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.teal, width: 3), right: BorderSide(color: Colors.teal, width: 3)))),
                            ),

                            // Loading overlay
                            if (_isLoading)
                              Container(
                                decoration: BoxDecoration(
                                  color: Colors.black.withValues(alpha: 0.65),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: const Center(
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      CircularProgressIndicator(color: Colors.tealAccent),
                                      SizedBox(height: 16),
                                      Text(
                                        'Identificando producto...',
                                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      Text(
                        _statusMessage,
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 13, color: Colors.blueGrey.shade700),
                      ),
                      const SizedBox(height: 20),

                      // Action Buttons: Camera and Gallery
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.teal.shade700,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 14),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                              onPressed: _isLoading ? null : () => _pickAndProcessImage(ImageSource.camera),
                              icon: const Icon(Icons.camera_alt),
                              label: const Text('Tomar Foto', style: TextStyle(fontWeight: FontWeight.bold)),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: OutlinedButton.icon(
                              style: OutlinedButton.styleFrom(
                                foregroundColor: Colors.teal.shade900,
                                side: BorderSide(color: Colors.teal.shade700, width: 1.5),
                                padding: const EdgeInsets.symmetric(vertical: 14),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                              onPressed: _isLoading ? null : () => _pickAndProcessImage(ImageSource.gallery),
                              icon: const Icon(Icons.photo_library),
                              label: const Text('Galería', style: TextStyle(fontWeight: FontWeight.bold)),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Supported products card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.inventory, size: 20, color: Colors.teal),
                        SizedBox(width: 8),
                        Text(
                          '8 Productos Soportados por el Modelo:',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: const [
                        Chip(label: Text('Coca-Cola'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Galletas Oreo'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Papas Lay\'s'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Café Nescafé'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Leche Pil'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Agua Mineral'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Chocolate Block'), avatar: Icon(Icons.check, size: 16)),
                        Chip(label: Text('Cerveza Paceña'), avatar: Icon(Icons.check, size: 16)),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
