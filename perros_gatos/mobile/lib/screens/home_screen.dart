import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/pet_prediction.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePicker _picker = ImagePicker();
  final ApiService _api = ApiService();

  bool _isLoading = false;
  bool? _isServerOnline;
  Uint8List? _selectedImageBytes;
  PetPrediction? _lastPrediction;
  String _hintMessage = 'Toma una foto o selecciona una imagen para analizar';

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

  Future<void> _pickAndClassify(ImageSource source) async {
    try {
      final XFile? file = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (file == null) return;

      final bytes = await file.readAsBytes();
      setState(() {
        _selectedImageBytes = bytes;
        _isLoading = true;
        _lastPrediction = null;
        _hintMessage = 'Clasificando con IA...';
      });

      final result = await _api.predictPet(file);

      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _lastPrediction = result;
        _hintMessage = result.message;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _hintMessage = 'Error al comunicarse con el backend: $e';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showConfigDialog() {
    final controller = TextEditingController(text: _api.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Configurar Backend Mascotas'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Ingresa la URL del backend FastAPI (puerto 8001 o nube):',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'URL Base',
                hintText: 'http://192.168.1.50:8001',
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                ActionChip(
                  label: const Text('Emulador (10.0.2.2:8001)'),
                  onPressed: () => controller.text = 'http://10.0.2.2:8001',
                ),
                ActionChip(
                  label: const Text('Localhost (8001)'),
                  onPressed: () => controller.text = 'http://localhost:8001',
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

  Color _getResultColor(String pred) {
    switch (pred) {
      case 'perro':
        return Colors.amber.shade800;
      case 'gato':
        return Colors.deepPurple.shade600;
      default:
        return Colors.blueGrey.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isOnline = _isServerOnline ?? false;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Row(
          children: [
            Text('🐶 🐱 ❓', style: TextStyle(fontSize: 20)),
            SizedBox(width: 8),
            Text('¿Perro, Gato o Ninguno?', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        elevation: 0,
        backgroundColor: Colors.white,
        actions: [
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
                  CircleAvatar(radius: 4, backgroundColor: isOnline ? Colors.green : Colors.red),
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
            onPressed: _showConfigDialog,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Main Visual Box
              Container(
                height: 280,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.04),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    if (_selectedImageBytes != null)
                      ClipRRect(
                        borderRadius: BorderRadius.circular(18),
                        child: Image.memory(
                          _selectedImageBytes!,
                          width: double.infinity,
                          height: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      )
                    else
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.pets, size: 64, color: Colors.deepPurple.shade200),
                          const SizedBox(height: 12),
                          const Text(
                            'Sube o toma una fotografía',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF334155)),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'El modelo identificará si es perro, gato o ningún animal',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                          ),
                        ],
                      ),

                    if (_isLoading)
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.65),
                          borderRadius: BorderRadius.circular(18),
                        ),
                        child: const Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              CircularProgressIndicator(color: Colors.white),
                              SizedBox(height: 14),
                              Text(
                                'Analizando con Red Neuronal...',
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

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF6366F1), // Indigo
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: _isLoading ? null : () => _pickAndClassify(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Tomar Foto', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF4338CA),
                        side: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: _isLoading ? null : () => _pickAndClassify(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text('Subir Foto', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Prediction Result Card
              if (_lastPrediction != null) ...[
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _getResultColor(_lastPrediction!.prediction).withValues(alpha: 0.3), width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: _getResultColor(_lastPrediction!.prediction).withValues(alpha: 0.08),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Text(
                        _lastPrediction!.labelDisplay,
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          color: _getResultColor(_lastPrediction!.prediction),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Certeza del Modelo: ${(_lastPrediction!.confidence * 100).toStringAsFixed(1)}%',
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15, color: Color(0xFF475569)),
                      ),
                      const SizedBox(height: 12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: LinearProgressIndicator(
                          value: _lastPrediction!.confidence,
                          minHeight: 10,
                          backgroundColor: Colors.grey.shade200,
                          valueColor: AlwaysStoppedAnimation<Color>(_getResultColor(_lastPrediction!.prediction)),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _lastPrediction!.message,
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
                      ),
                      const Divider(height: 28),

                      // Probabilities Breakdown
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Desglose de Probabilidades:',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                        ),
                      ),
                      const SizedBox(height: 10),
                      ..._lastPrediction!.probabilities.entries.map((entry) {
                        final label = entry.key == 'perro'
                            ? '🐶 Perro'
                            : (entry.key == 'gato' ? '🐱 Gato' : '❓ Ninguno');
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            children: [
                              SizedBox(width: 90, child: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500))),
                              Expanded(
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: entry.value,
                                    minHeight: 6,
                                    backgroundColor: Colors.grey.shade100,
                                    valueColor: AlwaysStoppedAnimation<Color>(_getResultColor(entry.key)),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 10),
                              Text('${(entry.value * 100).toStringAsFixed(1)}%', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ] else ...[
                // Helper Card
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.indigo.shade400),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _hintMessage,
                          style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
