import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../models/product_model.dart';

class ApiService {
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Render production cloud server by default
  String baseUrl = 'https://api-tienda-productos.onrender.com';

  void setBaseUrl(String url) {
    if (url.endsWith('/')) {
      baseUrl = url.substring(0, url.length - 1);
    } else {
      baseUrl = url;
    }
  }

  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final res = await http.get(uri).timeout(const Duration(seconds: 4));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<Product>> getProducts() async {
    final uri = Uri.parse('$baseUrl/products');
    final res = await http.get(uri).timeout(const Duration(seconds: 8));
    if (res.statusCode == 200) {
      final List<dynamic> list = json.decode(utf8.decode(res.bodyBytes));
      return list.map((item) => Product.fromJson(item)).toList();
    } else {
      throw Exception('Error al obtener productos: ${res.statusCode}');
    }
  }

  Future<PredictionResponse> predictProduct(XFile imageFile) async {
    final uri = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', uri);

    final bytes = await imageFile.readAsBytes();
    final multipartFile = http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: imageFile.name.isNotEmpty ? imageFile.name : 'product.jpg',
    );
    request.files.add(multipartFile);

    final streamedResponse = await request.send().timeout(const Duration(seconds: 15));
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(utf8.decode(response.bodyBytes));
      return PredictionResponse.fromJson(data);
    } else {
      throw Exception('Fallo en la predicción del servidor (${response.statusCode}): ${response.body}');
    }
  }

  Future<Product> updateStock(int productId, int newStock) async {
    final uri = Uri.parse('$baseUrl/products/$productId/stock');
    final res = await http.put(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'stock': newStock}),
    );
    if (res.statusCode == 200) {
      final data = json.decode(utf8.decode(res.bodyBytes));
      return Product.fromJson(data);
    } else {
      throw Exception('Error al actualizar stock: ${res.statusCode}');
    }
  }
}
