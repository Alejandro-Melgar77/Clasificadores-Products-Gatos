import 'package:flutter_test/flutter_test.dart';
import 'package:tienda_mobile/main.dart';

void main() {
  testWidgets('StoreApp smoke test and navigation verify', (WidgetTester tester) async {
    await tester.pumpWidget(const StoreApp());

    // Verify Title and Navigation items exist
    expect(find.text('Tienda Inteligente'), findsOneWidget);
    expect(find.text('Escanear'), findsOneWidget);
    expect(find.text('Inventario'), findsOneWidget);
  });
}
