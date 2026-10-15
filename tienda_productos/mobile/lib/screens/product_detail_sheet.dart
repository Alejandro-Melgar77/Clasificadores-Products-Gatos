import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../models/product_model.dart';
import '../services/api_service.dart';

class ProductDetailSheet extends StatefulWidget {
  final Product product;
  final double confidence;
  final Uint8List? imageBytes;

  const ProductDetailSheet({
    super.key,
    required this.product,
    required this.confidence,
    this.imageBytes,
  });

  @override
  State<ProductDetailSheet> createState() => _ProductDetailSheetState();
}

class _ProductDetailSheetState extends State<ProductDetailSheet> {
  late int _currentStock;
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _currentStock = widget.product.stock;
  }

  Color _getStockColor(int stock) {
    if (stock > 20) return Colors.green.shade700;
    if (stock > 5) return Colors.orange.shade800;
    return Colors.red.shade700;
  }

  String _getStockText(int stock) {
    if (stock > 20) return 'Disponible ($stock unid.)';
    if (stock > 5) return 'Stock Limitado ($stock unid.)';
    return '¡Últimas unidades! ($stock)';
  }

  Future<void> _changeStock(int delta) async {
    final newStock = _currentStock + delta;
    if (newStock < 0) return;

    setState(() => _isUpdating = true);
    try {
      final updated = await ApiService().updateStock(widget.product.id, newStock);
      if (mounted) {
        setState(() {
          _currentStock = updated.stock;
          _isUpdating = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Stock actualizado a $_currentStock unidades'),
            duration: const Duration(seconds: 1),
            backgroundColor: Colors.teal.shade700,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isUpdating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al actualizar: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final product = widget.product;
    final stockColor = _getStockColor(_currentStock);

    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 5,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Top Status Bar: Recognized Badge & Confidence
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.green.shade300),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.check_circle, size: 16, color: Colors.green.shade700),
                      const SizedBox(width: 6),
                      Text(
                        'Reconocido (${(widget.confidence * 100).toStringAsFixed(1)}%)',
                        style: TextStyle(
                          color: Colors.green.shade800,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.blueGrey.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'SKU: ${product.sku}',
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.blueGrey.shade800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Captured Image or Product Image
            if (widget.imageBytes != null)
              Center(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.memory(
                    widget.imageBytes!,
                    height: 170,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            const SizedBox(height: 16),

            // Title & Category
            Text(
              product.name,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E293B),
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.category_outlined, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  product.category,
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                ),
                const Spacer(),
                Text(
                  '${product.currency} ${product.price.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                    color: Colors.teal.shade800,
                  ),
                ),
              ],
            ),
            const Divider(height: 24),

            // Stock Section with live modification
            Row(
              children: [
                Icon(Icons.inventory_2_outlined, color: stockColor),
                const SizedBox(width: 8),
                Text(
                  'Estado de Inventario:',
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: stockColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: stockColor),
                  ),
                  child: Text(
                    _getStockText(_currentStock),
                    style: TextStyle(
                      color: stockColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Stock Counter Controls
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  const Text(
                    'Modificar Stock:',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                  const Spacer(),
                  IconButton.filledTonal(
                    onPressed: _isUpdating ? null : () => _changeStock(-1),
                    icon: const Icon(Icons.remove, size: 18),
                    tooltip: 'Restar unidad',
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Text(
                      '$_currentStock',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                  IconButton.filledTonal(
                    onPressed: _isUpdating ? null : () => _changeStock(1),
                    icon: const Icon(Icons.add, size: 18),
                    tooltip: 'Añadir unidad',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Product Description / Characteristics
            const Text(
              'Características del Producto',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF334155)),
            ),
            const SizedBox(height: 6),
            Text(
              product.description,
              style: TextStyle(fontSize: 14, color: Colors.grey.shade700, height: 1.4),
            ),
            const SizedBox(height: 12),

            // Barcode
            Row(
              children: [
                Icon(Icons.qr_code_2, size: 18, color: Colors.grey.shade600),
                const SizedBox(width: 6),
                Text(
                  'Código de barras: ${product.barcode}',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontFamily: 'monospace'),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Close button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.check),
                label: const Text('Entendido', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
