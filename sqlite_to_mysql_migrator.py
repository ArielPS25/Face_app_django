#!/usr/bin/env python3
"""
Script para migrar base de datos SQLite a MySQL
Convierte db.sqlite3 de Django a formato MySQL compatible
Autor: Sistema de migración automática
Fecha: 2025
"""

import sqlite3
import re
import os
from datetime import datetime

class SQLiteToMySQLMigrator:
    def __init__(self, sqlite_db_path, output_file):
        self.sqlite_db_path = sqlite_db_path
        self.output_file = output_file
        self.mysql_sql = []
        
        # Mapeo de tipos de datos SQLite a MySQL
        self.type_mappings = {
            'INTEGER': 'INT',
            'INTEGER PRIMARY KEY': 'INT AUTO_INCREMENT PRIMARY KEY',
            'REAL': 'DOUBLE',
            'TEXT': 'TEXT',
            'BLOB': 'LONGBLOB',
            'NUMERIC': 'DECIMAL(10,2)',
            'BOOLEAN': 'TINYINT(1)',
            'DATETIME': 'DATETIME',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'VARCHAR': 'VARCHAR',
            'CHAR': 'CHAR'
        }
    
    def log(self, message):
        """Log de operaciones"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def escape_mysql_value(self, value, column_type='TEXT'):
        """Escapa valores para MySQL"""
        if value is None:
            return 'NULL'
        
        # Números
        if isinstance(value, (int, float)):
            return str(value)
        
        # Booleanos
        if isinstance(value, bool):
            return '1' if value else '0'
        
        # Strings y otros
        value_str = str(value)
        
        # Escapar caracteres especiales para MySQL
        value_str = value_str.replace('\\', '\\\\')  # Backslashes
        value_str = value_str.replace("'", "\\'")     # Comillas simples
        value_str = value_str.replace('"', '\\"')     # Comillas dobles
        value_str = value_str.replace('\n', '\\n')    # Saltos de línea
        value_str = value_str.replace('\r', '\\r')    # Retorno de carro
        value_str = value_str.replace('\t', '\\t')    # Tabs
        value_str = value_str.replace('\0', '\\0')    # Null bytes
        
        return f"'{value_str}'"
    
    def convert_sqlite_type_to_mysql(self, sqlite_type):
        """Convierte tipos de datos SQLite a MySQL"""
        sqlite_type = sqlite_type.upper().strip()
        
        # Casos especiales primero
        if 'PRIMARY KEY' in sqlite_type and 'AUTOINCREMENT' in sqlite_type:
            return 'INT AUTO_INCREMENT PRIMARY KEY'
        elif 'PRIMARY KEY' in sqlite_type:
            return 'INT PRIMARY KEY'
        elif sqlite_type.startswith('VARCHAR'):
            # Mantener el tamaño si está especificado
            return sqlite_type
        elif sqlite_type.startswith('CHAR'):
            return sqlite_type
        elif 'DECIMAL' in sqlite_type or 'NUMERIC' in sqlite_type:
            return sqlite_type
        
        # Mapeos directos
        for sqlite_key, mysql_type in self.type_mappings.items():
            if sqlite_key in sqlite_type:
                return mysql_type
        
        # Por defecto, usar TEXT si no encuentra mapeo
        return 'TEXT'
    
    def get_table_schema(self, cursor, table_name):
        """Obtiene el schema de una tabla SQLite"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        mysql_columns = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = col[3]
            default_value = col[4]
            primary_key = col[5]
            
            # Convertir tipo
            mysql_type = self.convert_sqlite_type_to_mysql(col_type)
            
            # Construir definición de columna
            column_def = f"`{col_name}` {mysql_type}"
            
            # NOT NULL
            if not_null:
                column_def += " NOT NULL"
            
            # DEFAULT
            if default_value is not None:
                if mysql_type in ['INT', 'DOUBLE', 'DECIMAL', 'TINYINT']:
                    column_def += f" DEFAULT {default_value}"
                else:
                    column_def += f" DEFAULT '{default_value}'"
            
            # AUTO_INCREMENT para primary keys enteras
            if primary_key and 'AUTO_INCREMENT' not in mysql_type:
                if mysql_type.startswith('INT'):
                    column_def += " AUTO_INCREMENT"
            
            mysql_columns.append(column_def)
        
        return mysql_columns
    
    def get_table_indexes(self, cursor, table_name):
        """Obtiene los índices de una tabla"""
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        mysql_indexes = []
        for index in indexes:
            index_name = index[1]
            is_unique = index[2]
            
            # Obtener columnas del índice
            cursor.execute(f"PRAGMA index_info({index_name})")
            index_columns = cursor.fetchall()
            
            if index_columns:
                column_names = [col[2] for col in index_columns]
                columns_str = ", ".join([f"`{col}`" for col in column_names])
                
                if is_unique:
                    mysql_indexes.append(f"UNIQUE KEY `{index_name}` ({columns_str})")
                else:
                    mysql_indexes.append(f"KEY `{index_name}` ({columns_str})")
        
        return mysql_indexes
    
    def create_table_sql(self, cursor, table_name):
        """Genera SQL CREATE TABLE para MySQL"""
        self.log(f"Procesando tabla: {table_name}")
        
        # Schema de columnas
        columns = self.get_table_schema(cursor, table_name)
        
        # Índices
        indexes = self.get_table_indexes(cursor, table_name)
        
        # Construir CREATE TABLE
        sql = f"DROP TABLE IF EXISTS `{table_name}`;\n"
        sql += f"CREATE TABLE `{table_name}` (\n"
        
        # Columnas
        all_definitions = columns + indexes
        sql += ",\n".join([f"  {definition}" for definition in all_definitions])
        
        sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n\n"
        
        return sql
    
    def export_table_data(self, cursor, table_name):
        """Exporta datos de una tabla en formato INSERT"""
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            return f"-- No hay datos en la tabla {table_name}\n\n"
        
        # Obtener nombres de columnas
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        column_types = {col[1]: col[2] for col in columns_info}
        
        sql = f"-- Datos para la tabla {table_name}\n"
        sql += "SET FOREIGN_KEY_CHECKS = 0;\n"
        
        # Procesar en lotes de 100 registros
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            sql += f"INSERT INTO `{table_name}` ("
            sql += ", ".join([f"`{col}`" for col in column_names])
            sql += ") VALUES\n"
            
            values_list = []
            for row in batch:
                values = []
                for j, value in enumerate(row):
                    col_name = column_names[j]
                    col_type = column_types[col_name]
                    escaped_value = self.escape_mysql_value(value, col_type)
                    values.append(escaped_value)
                
                values_list.append(f"({', '.join(values)})")
            
            sql += ",\n".join(values_list)
            sql += ";\n\n"
        
        sql += "SET FOREIGN_KEY_CHECKS = 1;\n\n"
        return sql
    
    def get_django_tables(self, cursor):
        """Obtiene las tablas de Django en orden correcto para evitar problemas de FK"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [table[0] for table in cursor.fetchall()]
        
        # Orden recomendado para Django
        priority_order = [
            'django_migrations',
            'django_content_type', 
            'auth_group',
            'auth_permission',
            'auth_user',
            'auth_group_permissions',
            'auth_user_groups',
            'auth_user_user_permissions',
            'django_admin_log',
            'django_session'
        ]
        
        # Tablas de la aplicación
        app_tables = [table for table in all_tables if table.startswith('attendance_')]
        
        # Ordenar: primero las de sistema, luego las de app, después el resto
        ordered_tables = []
        
        # Agregar tablas de sistema en orden
        for table in priority_order:
            if table in all_tables:
                ordered_tables.append(table)
        
        # Agregar tablas de aplicación
        ordered_tables.extend(app_tables)
        
        # Agregar las restantes
        remaining_tables = [t for t in all_tables if t not in ordered_tables]
        ordered_tables.extend(remaining_tables)
        
        return ordered_tables
    
    def migrate(self):
        """Proceso principal de migración"""
        try:
            self.log("🚀 Iniciando migración de SQLite a MySQL...")
            
            # Verificar que existe el archivo SQLite
            if not os.path.exists(self.sqlite_db_path):
                raise FileNotFoundError(f"No se encontró el archivo: {self.sqlite_db_path}")
            
            # Conectar a SQLite
            self.log(f"📁 Conectando a SQLite: {self.sqlite_db_path}")
            conn = sqlite3.connect(self.sqlite_db_path)
            cursor = conn.cursor()
            
            # Header del archivo SQL
            header = f"""-- =============================================
-- Script de migración de SQLite a MySQL
-- Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Fuente: {self.sqlite_db_path}
-- =============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET AUTOCOMMIT = 0;
START TRANSACTION;

"""
            self.mysql_sql.append(header)
            
            # Obtener todas las tablas en orden correcto
            tables = self.get_django_tables(cursor)
            self.log(f"📋 Encontradas {len(tables)} tablas: {', '.join(tables)}")
            
            # Procesar cada tabla
            self.log("🔄 Generando estructura de tablas...")
            for table_name in tables:
                # Crear estructura
                create_sql = self.create_table_sql(cursor, table_name)
                self.mysql_sql.append(create_sql)
            
            # Exportar datos
            self.log("📊 Exportando datos...")
            for table_name in tables:
                data_sql = self.export_table_data(cursor, table_name)
                self.mysql_sql.append(data_sql)
            
            # Footer
            footer = """
-- =============================================
-- Fin de la migración
-- =============================================
COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
"""
            self.mysql_sql.append(footer)
            
            # Escribir archivo
            self.log(f"💾 Escribiendo archivo: {self.output_file}")
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.mysql_sql))
            
            # Cerrar conexión
            conn.close()
            
            # Estadísticas finales
            file_size = os.path.getsize(self.output_file) / 1024 / 1024  # MB
            self.log(f"✅ Migración completada exitosamente!")
            self.log(f"📄 Archivo generado: {self.output_file}")
            self.log(f"📏 Tamaño del archivo: {file_size:.2f} MB")
            self.log(f"🎯 Tablas migradas: {len(tables)}")
            
            print("\n" + "="*60)
            print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            print(f"✅ Archivo MySQL generado: {self.output_file}")
            print(f"📊 Tablas procesadas: {len(tables)}")
            print(f"💾 Tamaño: {file_size:.2f} MB")
            print("\n🚀 SIGUIENTES PASOS:")
            print("1. Crear base de datos MySQL: CREATE DATABASE face_attendance_db;")
            print("2. Importar el archivo: mysql -u usuario -p face_attendance_db < dump_mysql.sql")
            print("3. Actualizar settings.py de Django con configuración MySQL")
            print("="*60)
            
        except Exception as e:
            self.log(f"❌ Error durante la migración: {str(e)}")
            raise

def main():
    """Función principal"""
    # Configuración
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_db_path = os.path.join(current_dir, 'db.sqlite3')
    output_file = os.path.join(current_dir, 'dump_mysql.sql')
    
    print("🗄️  MIGRADOR SQLite → MySQL")
    print("="*40)
    print(f"📁 Base de datos origen: {sqlite_db_path}")
    print(f"📄 Archivo destino: {output_file}")
    print("="*40)
    
    # Confirmar antes de proceder
    response = input("\n¿Proceder con la migración? (s/N): ")
    if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
        print("❌ Migración cancelada por el usuario.")
        return
    
    # Ejecutar migración
    migrator = SQLiteToMySQLMigrator(sqlite_db_path, output_file)
    migrator.migrate()

if __name__ == "__main__":
    main()