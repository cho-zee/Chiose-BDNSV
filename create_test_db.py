import sqlite3
import os

# Numele bazei de date
db_path = os.path.join("data", "test_db.sqlite")

# Conectare (creează fișierul dacă nu există)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Creare Tabel: Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    signup_date DATE
)
''')

# 2. Creare Tabel: Orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_date DATE,
    total_amount REAL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# 3. Creare Tabel: Products
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL,
    stock INTEGER
)
''')

# 4. Inserare Date Dummy (Doar dacă tabelele sunt goale)
# Verificăm dacă avem useri
cursor.execute('SELECT count(*) FROM users')
if cursor.fetchone()[0] == 0:
    print("Se populează baza de date cu date de test...")
    
    # Users
    users_data = [
        ('Ion Popescu', 'ion@example.com', '2023-01-15'),
        ('Maria Ionescu', 'maria@example.com', '2023-02-20'),
        ('Andrei Radu', 'andrei@test.com', '2023-03-10')
    ]
    cursor.executemany('INSERT INTO users (name, email, signup_date) VALUES (?, ?, ?)', users_data)

    # Products
    products_data = [
        ('Laptop Gaming', 1200.50, 10),
        ('Mouse Wireless', 25.00, 50),
        ('Monitor 4K', 300.00, 15),
        ('Tastatura Mecanica', 80.00, 30)
    ]
    cursor.executemany('INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)', products_data)

    # Orders (User 1 are 2 comenzi, User 2 are 1 comandă)
    orders_data = [
        (1, '2023-04-01', 1225.50), # Laptop + Mouse
        (1, '2023-05-01', 80.00),   # Tastatura
        (2, '2023-04-15', 300.00)   # Monitor
    ]
    cursor.executemany('INSERT INTO orders (user_id, order_date, total_amount) VALUES (?, ?, ?)', orders_data)
    
    print("Datele au fost inserate.")
else:
    print("Baza de date conține deja date.")

conn.commit()
conn.close()
print(f"Baza de date a fost creată cu succes la: {db_path}")