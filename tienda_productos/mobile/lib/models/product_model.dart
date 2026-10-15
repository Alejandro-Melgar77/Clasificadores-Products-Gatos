class Product {
  final int id;
  final String classId;
  final String sku;
  final String name;
  final String category;
  final double price;
  final String currency;
  final int stock;
  final String description;
  final String barcode;
  final String? imageUrl;

  Product({
    required this.id,
    required this.classId,
    required this.sku,
    required this.name,
    required this.category,
    required this.price,
    required this.currency,
    required this.stock,
    required this.description,
    required this.barcode,
    this.imageUrl,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as int,
      classId: json['class_id'] as String,
      sku: json['sku'] as String,
      name: json['name'] as String,
      category: json['category'] as String,
      price: (json['price'] as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'Bs',
      stock: json['stock'] as int,
      description: json['description'] as String,
      barcode: json['barcode'] as String,
      imageUrl: json['image_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'class_id': classId,
      'sku': sku,
      'name': name,
      'category': category,
      'price': price,
      'currency': currency,
      'stock': stock,
      'description': description,
      'barcode': barcode,
      'image_url': imageUrl,
    };
  }
}

class PredictionResponse {
  final bool recognized;
  final String? classId;
  final double confidence;
  final Product? product;
  final String message;
  final Map<String, double> probabilities;

  PredictionResponse({
    required this.recognized,
    this.classId,
    required this.confidence,
    this.product,
    required this.message,
    required this.probabilities,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    Map<String, double> probs = {};
    if (json['probabilities'] != null) {
      (json['probabilities'] as Map<String, dynamic>).forEach((k, v) {
        probs[k] = (v as num).toDouble();
      });
    }

    return PredictionResponse(
      recognized: json['recognized'] as bool? ?? false,
      classId: json['class_id'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      product: json['product'] != null ? Product.fromJson(json['product']) : null,
      message: json['message'] as String? ?? '',
      probabilities: probs,
    );
  }
}
