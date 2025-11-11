#!/usr/bin/env python3
"""
Script para importar dump MySQL a AWS RDS
Ejecuta el archivo dump_mysql.sql en una instancia MySQL de AWS RDS
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from datetime import datetime

def read_sql_file(file_path):
    """Lee y prepara el archivo SQL para ejecución"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Dividir en statements individuales
        statements = []
        current_statement = ""
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if line.startswith('--') or not line:
                continue
            
            current_statement += line + "\n"
            
            # Si la línea termina con ;, es el final de un statement
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        return statements
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error leyendo el archivo: {e}")
        return []

def execute_sql_statements(connection, statements):
    """Ejecuta una lista de statements SQL"""
    cursor = connection.cursor()
    success_count = 0
    error_count = 0
    
    print(f"📊 Ejecutando {len(statements)} statements SQL...")
    
    for i, statement in enumerate(statements, 1):
        try:
            if statement.strip():
                cursor.execute(statement)
                success_count += 1
                if i % 10 == 0:  # Mostrar progreso cada 10 statements
                    print(f"✅ Progreso: {i}/{len(statements)} statements ejecutados")
        except Error as e:
            error_count += 1
            print(f"⚠️  Error en statement {i}: {e}")
            # Continuar con el siguiente statement
            continue
    
    cursor.close()
    return success_count, error_count

def main():
    # Configuración de conexión a AWS RDS
    config = {
        'host': input("🔗 Ingresa el host de tu RDS (ej: mydb.123456789012.us-east-1.rds.amazonaws.com): ").strip(),
        'user': input("👤 Ingresa el usuario: ").strip() or 'admin',
        'password': input("🔑 Ingresa la password: ").strip(),
        'database': input("🗄️  Ingresa el nombre de la base de datos: ").strip() or 'nandu',
        'port': 3306,
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': False
    }
    
    # Verificar que el archivo dump existe
    dump_file = 'dump_mysql_fixed.sql'
    if not os.path.exists(dump_file):
        print(f"❌ Error: No se encontró el archivo {dump_file}")
        print("   Asegúrate de que el archivo esté en el directorio actual.")
        return False
    
    print(f"\n🚀 Iniciando importación a MySQL RDS...")
    print(f"📁 Archivo: {dump_file}")
    print(f"🌐 Host: {config['host']}")
    print(f"🗄️  Base de datos: {config['database']}")
    print("-" * 50)
    
    try:
        # Conectar a MySQL
        print("🔌 Conectando a MySQL RDS...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ Conexión exitosa a MySQL RDS")
            
            # Leer el archivo SQL
            print("📖 Leyendo archivo dump_mysql.sql...")
            statements = read_sql_file(dump_file)
            
            if not statements:
                print("❌ No se pudieron leer los statements SQL")
                return False
            
            print(f"📋 Se encontraron {len(statements)} statements SQL")
            
            # Confirmar antes de ejecutar
            confirm = input(f"\n⚠️  ¿Estás seguro de que quieres ejecutar la importación? (sí/no): ").lower()
            if confirm not in ['sí', 'si', 's', 'yes', 'y']:
                print("❌ Importación cancelada por el usuario")
                return False
            
            # Ejecutar statements
            start_time = datetime.now()
            success_count, error_count = execute_sql_statements(connection, statements)
            end_time = datetime.now()
            
            # Commit de cambios
            connection.commit()
            
            # Resultados
            duration = (end_time - start_time).total_seconds()
            print("\n" + "=" * 50)
            print("📊 RESUMEN DE IMPORTACIÓN")
            print("=" * 50)
            print(f"✅ Statements ejecutados exitosamente: {success_count}")
            print(f"❌ Statements con errores: {error_count}")
            print(f"⏱️  Tiempo total: {duration:.2f} segundos")
            print(f"🗄️  Base de datos: {config['database']}")
            print(f"🌐 Host: {config['host']}")
            
            if error_count == 0:
                print("\n🎉 ¡IMPORTACIÓN COMPLETADA EXITOSAMENTE!")
                print("   Todos los datos se han migrado correctamente a MySQL RDS.")
            else:
                print(f"\n⚠️  Importación completada con {error_count} errores.")
                print("   Revisa los mensajes anteriores para más detalles.")
            
            return True
            
    except Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión a MySQL cerrada")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 IMPORTADOR DE DUMP MYSQL A AWS RDS")
    print("=" * 60)
    
    success = main()
    
    if success:
        print("\n📝 PRÓXIMOS PASOS:")
        print("1. Actualiza tu settings.py de Django con la nueva configuración MySQL")
        print("2. Instala mysqlclient: pip install mysqlclient")
        print("3. Ejecuta: python manage.py migrate --fake-initial")
        print("4. Verifica que todo funcione correctamente")
    else:
        print("\n❌ La importación falló. Revisa los errores anteriores.")
    
    input("\n👆 Presiona Enter para salir...")