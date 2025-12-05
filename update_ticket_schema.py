import sqlite3
import os

DB_PATH = os.path.join('belgrano_tickets', 'belgrano_tickets.db')

def add_columns():
    if not os.path.exists(DB_PATH):
        print(f"No se encontro la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        ('grupo_compra', 'TEXT'),
        ('negocio_nombre', 'TEXT'),
        ('tickets_grupo_total', 'INTEGER DEFAULT 1')
    ]
    
    print(f"Verificando columnas en {DB_PATH}...")
    
    # Obtener columnas existentes
    cursor.execute("PRAGMA table_info(ticket)")
    existing_columns = [info[1] for info in cursor.fetchall()]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                print(f"Agregando columna '{col_name}'...")
                cursor.execute(f"ALTER TABLE ticket ADD COLUMN {col_name} {col_type}")
                print(f"   Columna '{col_name}' agregada correctamente.")
            except Exception as e:
                print(f"   Error agregando columna '{col_name}': {e}")
        else:
            print(f"   La columna '{col_name}' ya existe.")
            
    conn.commit()
    conn.close()
    print("Actualizacion de esquema finalizada.")

if __name__ == '__main__':
    add_columns()
