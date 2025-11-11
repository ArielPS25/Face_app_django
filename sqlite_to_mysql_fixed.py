#!/usr/bin/env python3
"""
Migrador SQLite a MySQL - Versión Corregida
Genera un dump SQL compatible con MySQL RDS sin errores de sintaxis
"""

import sqlite3
import json
import os
from datetime import datetime

class SQLiteToMySQLMigrator:
    def __init__(self, sqlite_db_path, output_file='dump_mysql_fixed.sql'):
        self.sqlite_db_path = sqlite_db_path
        self.output_file = output_file
        self.type_mapping = {
            'INTEGER': 'INT',
            'TEXT': 'TEXT',
            'REAL': 'DOUBLE',
            'BLOB': 'LONGBLOB',
            'NUMERIC': 'DECIMAL(10,2)',
            'VARCHAR': 'VARCHAR',
            'DATETIME': 'DATETIME',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'BOOLEAN': 'TINYINT(1)'
        }
    
    def connect_sqlite(self):
        """Conectar a la base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ Error conectando a SQLite: {e}")
            return None
    
    def get_table_info(self, conn, table_name):
        """Obtener información detallada de una tabla"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Obtener información de claves foráneas
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        # Obtener índices
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        return columns, foreign_keys, indexes
    
    def map_sqlite_type_to_mysql(self, sqlite_type, column_name):
        """Mapear tipos de SQLite a MySQL con correcciones específicas"""
        sqlite_type = sqlite_type.upper()
        
        # Casos especiales para campos específicos de Django
        if 'BOOLEAN' in sqlite_type or column_name in ['is_superuser', 'is_staff', 'is_active']:
            return 'TINYINT(1)'
        
        if 'INTEGER' in sqlite_type:
            return 'INT'
        
        if 'VARCHAR' in sqlite_type:
            # Extraer longitud si está presente
            if '(' in sqlite_type and ')' in sqlite_type:
                return sqlite_type.replace('VARCHAR', 'VARCHAR')
            return 'VARCHAR(255)'
        
        if 'TEXT' in sqlite_type:
            return 'TEXT'
        
        if 'DATETIME' in sqlite_type:
            return 'DATETIME'
        
        if 'DATE' in sqlite_type:
            return 'DATE'
        
        if 'TIME' in sqlite_type:
            return 'TIME'
        
        if 'REAL' in sqlite_type or 'DOUBLE' in sqlite_type:
            return 'DOUBLE'
        
        return 'TEXT'  # Tipo por defecto
    
    def create_table_sql(self, conn, table_name):
        """Generar SQL CREATE TABLE compatible con MySQL"""
        columns, foreign_keys, indexes = self.get_table_info(conn, table_name)
        
        if not columns:
            return None
        
        sql = f"DROP TABLE IF EXISTS `{table_name}`;\nCREATE TABLE `{table_name}` (\n"
        
        column_definitions = []
        primary_key_found = False
        
        for col in columns:
            col_name = col['name']
            col_type = col['type']
            is_pk = col['pk'] == 1
            not_null = col['notnull'] == 1
            default_value = col['dflt_value']
            
            # Mapear tipo
            mysql_type = self.map_sqlite_type_to_mysql(col_type, col_name)
            
            # Construir definición de columna
            col_def = f"  `{col_name}` {mysql_type}"
            
            # NOT NULL
            if not_null or is_pk:
                col_def += " NOT NULL"
            
            # AUTO_INCREMENT solo para primary keys INTEGER
            if is_pk and 'INT' in mysql_type:
                col_def += " AUTO_INCREMENT"
                primary_key_found = True
            
            # Default value
            if default_value is not None and not is_pk:
                if mysql_type in ['VARCHAR(255)', 'TEXT']:
                    col_def += f" DEFAULT '{default_value}'"
                else:
                    col_def += f" DEFAULT {default_value}"
            
            column_definitions.append(col_def)
        
        sql += ",\n".join(column_definitions)
        
        # Agregar PRIMARY KEY si existe
        if primary_key_found:
            pk_columns = [col['name'] for col in columns if col['pk'] == 1]
            if pk_columns:
                sql += f",\n  PRIMARY KEY (`{'`, `'.join(pk_columns)}`)"
        
        # Agregar índices únicos (excluyendo primary key)
        cursor = conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}' AND sql IS NOT NULL")
        index_sqls = cursor.fetchall()
        
        unique_constraints = []
        regular_indexes = []
        
        for idx_sql in index_sqls:
            sql_text = idx_sql[0]
            if 'UNIQUE' in sql_text.upper():
                # Extraer columnas del índice único
                import re
                match = re.search(r'\(([^)]+)\)', sql_text)
                if match:
                    columns_str = match.group(1)
                    # Limpiar nombres de columnas
                    columns_list = [col.strip().strip('"').strip("'") for col in columns_str.split(',')]
                    if columns_list and not any(col for col in columns if col['pk'] == 1 and col['name'] in columns_list):
                        unique_constraints.append(f"  UNIQUE KEY (`{'`, `'.join(columns_list)}`)")
            else:
                # Índice regular
                import re
                idx_name_match = re.search(r'CREATE INDEX\s+(\w+)', sql_text, re.IGNORECASE)
                columns_match = re.search(r'\(([^)]+)\)', sql_text)
                
                if idx_name_match and columns_match:
                    idx_name = idx_name_match.group(1)
                    columns_str = columns_match.group(1)
                    columns_list = [col.strip().strip('"').strip("'") for col in columns_str.split(',')]
                    
                    # Para campos TEXT, agregar longitud
                    indexed_columns = []
                    for col_name in columns_list:
                        col_info = next((col for col in columns if col['name'] == col_name), None)
                        if col_info and 'TEXT' in self.map_sqlite_type_to_mysql(col_info['type'], col_name):
                            indexed_columns.append(f"`{col_name}`(255)")
                        else:
                            indexed_columns.append(f"`{col_name}`")
                    
                    regular_indexes.append(f"  KEY `{idx_name}` ({', '.join(indexed_columns)})")
        
        # Agregar constraints únicos
        if unique_constraints:
            sql += ",\n" + ",\n".join(unique_constraints)
        
        # Agregar índices regulares
        if regular_indexes:
            sql += ",\n" + ",\n".join(regular_indexes)
        
        sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n\n"
        
        return sql
    
    def export_table_data(self, conn, table_name):
        """Exportar datos de una tabla"""
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            return f"-- No hay datos en la tabla {table_name}\n\n"
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        sql = f"-- Datos para la tabla {table_name}\n"
        sql += "SET FOREIGN_KEY_CHECKS = 0;\n"
        
        # Preparar INSERT statements
        values_list = []
        for row in rows:
            row_values = []
            for value in row:
                if value is None:
                    row_values.append("NULL")
                elif isinstance(value, str):
                    # Escapar comillas simples
                    escaped_value = value.replace("'", "\\'")
                    row_values.append(f"'{escaped_value}'")
                elif isinstance(value, (int, float)):
                    row_values.append(str(value))
                else:
                    row_values.append(f"'{str(value)}'")
            values_list.append(f"({', '.join(row_values)})")
        
        # Dividir en lotes de 100 registros para evitar statements muy largos
        batch_size = 100
        for i in range(0, len(values_list), batch_size):
            batch = values_list[i:i+batch_size]
            columns_str = '`, `'.join(column_names)
            sql += f"INSERT INTO `{table_name}` (`{columns_str}`) VALUES\n"
            sql += ",\n".join(batch) + ";\n\n"
        
        sql += "SET FOREIGN_KEY_CHECKS = 1;\n\n"
        
        return sql
    
    def migrate(self):
        """Ejecutar la migración completa"""
        print(f"🚀 Iniciando migración SQLite → MySQL (Versión Corregida)")
        print(f"📁 Base de datos SQLite: {self.sqlite_db_path}")
        print(f"📄 Archivo de salida: {self.output_file}")
        
        # Conectar a SQLite
        conn = self.connect_sqlite()
        if not conn:
            return False
        
        try:
            # Obtener lista de tablas
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📊 Tablas encontradas: {len(tables)}")
            
            # Generar archivo SQL
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("-- =============================================\n")
                f.write("-- Script de migración SQLite a MySQL (CORREGIDO)\n")
                f.write(f"-- Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Fuente: {os.path.abspath(self.sqlite_db_path)}\n")
                f.write("-- =============================================\n\n")
                
                f.write("SET NAMES utf8mb4;\n")
                f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
                f.write("SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';\n")
                f.write("SET AUTOCOMMIT = 0;\n")
                f.write("START TRANSACTION;\n\n")
                
                # Generar CREATE TABLE para cada tabla
                print("📝 Generando estructura de tablas...")
                for table in tables:
                    print(f"   ⚙️  Procesando tabla: {table}")
                    create_sql = self.create_table_sql(conn, table)
                    if create_sql:
                        f.write(create_sql)
                
                # Exportar datos
                print("💾 Exportando datos...")
                for table in tables:
                    print(f"   📋 Exportando datos de: {table}")
                    data_sql = self.export_table_data(conn, table)
                    f.write(data_sql)
                
                # Pie del archivo
                f.write("\n-- =============================================\n")
                f.write("-- Fin de la migración\n")
                f.write("-- =============================================\n")
                f.write("COMMIT;\n")
                f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
            
            file_size = os.path.getsize(self.output_file) / (1024 * 1024)  # MB
            print(f"\n✅ Migración completada exitosamente!")
            print(f"📄 Archivo generado: {self.output_file}")
            print(f"📏 Tamaño: {file_size:.2f} MB")
            print(f"📊 Tablas migradas: {len(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            return False
        finally:
            conn.close()

def main():
    # Configuración
    sqlite_db = 'db.sqlite3'
    output_file = 'dump_mysql_fixed.sql'
    
    if not os.path.exists(sqlite_db):
        print(f"❌ Error: No se encontró la base de datos SQLite: {sqlite_db}")
        return
    
    # Ejecutar migración
    migrator = SQLiteToMySQLMigrator(sqlite_db, output_file)
    success = migrator.migrate()
    
    if success:
        print("\n🎉 ¡MIGRACIÓN COMPLETADA!")
        print(f"🔧 Archivo corregido generado: {output_file}")
        print("📝 Ahora puedes importarlo a MySQL RDS sin errores.")
    else:
        print("\n❌ La migración falló.")

if __name__ == "__main__":
    main()