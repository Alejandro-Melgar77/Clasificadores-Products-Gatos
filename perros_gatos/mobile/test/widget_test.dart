import 'package:flutter_test/flutter_test.dart';
import 'package:perros_gatos_mobile/main.dart';

void main() {
  testWidgets('PetClassifierApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const PetClassifierApp());

    // Verify Title and Action buttons exist
    expect(find.text('¿Perro, Gato o Ninguno?'), findsOneWidget);
    expect(find.text('Tomar Foto'), findsOneWidget);
    expect(find.text('Subir Foto'), findsOneWidget);
  });
}
