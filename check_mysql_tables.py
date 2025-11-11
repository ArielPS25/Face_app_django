#!/usr/bin/env python3
"""
Script para verificar las tablas existentes en MySQL
"""

import mysql.connector
from mysql.connector import Error

def check_mysql_tables():
    """Verificar qué tablas existen en MySQL"""
    
    config = {
        'host': 'nandu.czmoey4oapii.sa-east-1.rds.amazonaws.com',
        'user': 'admin', 
        'password': 'admin123',
        'database': 'nandu',
        'port': 3306
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("🔍 TABLAS EN LA BASE DE DATOS MYSQL:")
        print("=" * 50)
        
        # Listar todas las tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            for i, table in enumerate(tables, 1):
                table_name = table[0]
                print(f"{i:2d}. {table_name}")
                
                # Contar registros en cada tabla
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    📊 Registros: {count}")
        else:
            print("❌ No se encontraron tablas en la base de datos")
        
        print(f"\n📊 Total de tablas: {len(tables)}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_mysql_tables()
    input("\n👆 Presiona Enter para salir...")