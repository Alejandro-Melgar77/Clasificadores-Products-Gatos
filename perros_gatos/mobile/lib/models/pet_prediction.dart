class PetPrediction {
  final String prediction; // 'perro' | 'gato' | 'ninguno'
  final String labelDisplay; // 'Perro 🐶' | 'Gato 🐱' | 'Ninguno ❓'
  final double confidence;
  final Map<String, double> probabilities;
  final String message;

  PetPrediction({
    required this.prediction,
    required this.labelDisplay,
    required this.confidence,
    required this.probabilities,
    required this.message,
  });

  factory PetPrediction.fromJson(Map<String, dynamic> json) {
    Map<String, double> probs = {};
    if (json['probabilities'] != null) {
      (json['probabilities'] as Map<String, dynamic>).forEach((k, v) {
        probs[k] = (v as num).toDouble();
      });
    }

    return PetPrediction(
      prediction: json['prediction'] as String? ?? 'ninguno',
      labelDisplay: json['label_display'] as String? ?? 'Ninguno ❓',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      probabilities: probs,
      message: json['message'] as String? ?? '',
    );
  }
}
