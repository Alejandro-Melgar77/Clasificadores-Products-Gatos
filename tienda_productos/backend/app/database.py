import sqlite3
import os
from typing import List, Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "store.db")

INITIAL_PRODUCTS = [
    {
        "class_id": "cocacola",
        "sku": "BEV-COCA-350",
        "name": "Coca-Cola Original 350ml",
        "category": "Bebidas y Refrescos",
        "price": 8.00,
        "currency": "Bs",
        "stock": 45,
        "description": "Bebida gaseosa refrescante sabor original. Lata de aluminio 350ml. Servir bien fría.",
        "barcode": "777123456001",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Coca-cola_50cl_can_-_Italia.jpg/400px-Coca-cola_50cl_can_-_Italia.jpg"
    },
    {
        "class_id": "oreo",
        "sku": "SNK-OREO-108",
        "name": "Galletas Oreo Clásicas 108g",
        "category": "Snacks y Galletas",
        "price": 6.50,
        "currency": "Bs",
        "stock": 30,
        "description": "Galletas de cacao rellenas con crema de vainilla. Paquete clásico de 108g para compartir.",
        "barcode": "777123456002",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Oreo-Two-Cookies.png/400px-Oreo-Two-Cookies.png"
    },
    {
        "class_id": "lays",
        "sku": "SNK-LAYS-140",
        "name": "Papas Fritas Lay's Clásicas 140g",
        "category": "Snacks y Frituras",
        "price": 10.00,
        "currency": "Bs",
        "stock": 22,
        "description": "Crujientes papas fritas seleccionadas con sal marina. Bolsa familiar de 140g.",
        "barcode": "777123456003",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Potato-Chips.jpg/400px-Potato-Chips.jpg"
    },
    {
        "class_id": "nescafe",
        "sku": "HOT-NESC-100",
        "name": "Café Nescafé Clásico 100g",
        "category": "Cafetería y Desayuno",
        "price": 28.00,
        "currency": "Bs",
        "stock": 15,
        "description": "Café 100% puro soluble instantáneo. Frasco de vidrio de 100g, aroma intenso y sabor balanceado.",
        "barcode": "777123456004",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Nescaf%C3%A8_instant_coffee%2C_2019-%2801%29.jpg/400px-Nescaf%C3%A8_instant_coffee%2C_2019-%2801%29.jpg"
    },
    {
        "class_id": "leche_pil",
        "sku": "LAC-PIL-1000",
        "name": "Leche Fluida Pasteurizada Pil 1L",
        "category": "Lácteos",
        "price": 6.00,
        "currency": "Bs",
        "stock": 50,
        "description": "Leche entera fresca natural pasteurizada Pil Andina. Bolsa sachet de 1000ml rica en calcio.",
        "barcode": "777123456005",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Milk_carton.jpg/400px-Milk_carton.jpg"
    },
    {
        "class_id": "agua_mineral",
        "sku": "BEV-AGUA-600",
        "name": "Agua Mineral Vital sin Gas 600ml",
        "category": "Bebidas e Hidratación",
        "price": 5.00,
        "currency": "Bs",
        "stock": 60,
        "description": "Agua purificada de vertiente natural sin gas. Botella ecológica PET de 600ml.",
        "barcode": "777123456006",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Water_bottle.jpg/400px-Water_bottle.jpg"
    },
    {
        "class_id": "chocolate_block",
        "sku": "DUL-BLOK-150",
        "name": "Chocolate Cofler Block con Maní 150g",
        "category": "Golosinas y Chocolates",
        "price": 12.50,
        "currency": "Bs",
        "stock": 18,
        "description": "Tableta maciza de chocolate con leche y trozos de maní tostado seleccionado.",
        "barcode": "777123456007",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Chocolate_bar.jpg/400px-Chocolate_bar.jpg"
    },
    {
        "class_id": "cerveza_pacena",
        "sku": "ALC-PACE-355",
        "name": "Cerveza Paceña Pilsener 355ml",
        "category": "Bebidas Alcohólicas",
        "price": 11.00,
        "currency": "Bs",
        "stock": 35,
        "description": "Cerveza tradicional boliviana tipo Pilsener elaborada con agua de deshielo de los Andes. Lata 355ml.",
        "barcode": "777123456008",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Beer_can.jpg/400px-Beer_can.jpg"
    }
]

def get_connection():
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id TEXT UNIQUE NOT NULL,
        sku TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        currency TEXT NOT NULL DEFAULT 'Bs',
        stock INTEGER NOT NULL,
        description TEXT NOT NULL,
        barcode TEXT NOT NULL,
        image_url TEXT
    )
    """)
    conn.commit()
    
    # Populate initial products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        for p in INITIAL_PRODUCTS:
            cursor.execute("""
            INSERT INTO products (class_id, sku, name, category, price, currency, stock, description, barcode, image_url)
            VALUES (:class_id, :sku, :name, :category, :price, :currency, :stock, :description, :barcode, :image_url)
            """, p)
        conn.commit()
        print(f"✔ Base de datos inicializada con {len(INITIAL_PRODUCTS)} productos.")
    conn.close()

def get_all_products() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = cursor.fetchall()
    products = [dict(r) for r in rows]
    conn.close()
    return products

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_product_by_class_id(class_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE class_id = ?", (class_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_product_stock(product_id: int, new_stock: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Initialize database on module load
init_db()
