#!/usr/bin/env python3
"""
Script para crear la tabla attendance_attendancerecord faltante en MySQL
"""

import mysql.connector
from mysql.connector import Error

def create_missing_table():
    """Crear la tabla attendance_attendancerecord en MySQL"""
    
    config = {
        'host': 'nandu.czmoey4oapii.sa-east-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'admin123',
        'database': 'nandu',
        'port': 3306
    }
    
    # SQL para crear la tabla attendance_attendancerecord
    create_table_sql = """
    CREATE TABLE `attendance_attendancerecord` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `timestamp` DATETIME NOT NULL,
        `date` DATE NOT NULL,
        `confidence` DOUBLE NOT NULL,
        `notes` TEXT NOT NULL,
        `person_id` INT NOT NULL,
        PRIMARY KEY (`id`),
        KEY `attendance_attendancerecord_person_id_f3ee39d2` (`person_id`),
        UNIQUE KEY `attendance_attendancerecord_person_id_date_2ba89fe7_uniq` (`person_id`, `date`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # Datos para insertar
    insert_data_sql = """
    INSERT INTO `attendance_attendancerecord` (`id`, `timestamp`, `date`, `confidence`, `notes`, `person_id`) VALUES
    (1, '2025-11-07 02:57:00.142469', '2025-11-06', 0.6088143718739032, '', 1),
    (2, '2025-11-07 03:01:22.451848', '2025-11-06', 0.7268329871233541, '', 4),
    (4, '2025-11-08 16:58:23.211858', '2025-11-08', 0.6634706719575313, '', 1),
    (5, '2025-11-08 17:16:02.184179', '2025-11-08', 0.5916567209697949, '', 5),
    (6, '2025-11-08 17:23:00.186830', '2025-11-08', 0.5467209735449348, '', 4),
    (9, '2025-11-09 16:54:44.870931', '2025-11-09', 0.6571194334901118, '', 1),
    (10, '2025-11-09 20:07:58.230410', '2025-11-09', 0.6941206254759251, '', 4),
    (11, '2025-11-09 20:08:11.219206', '2025-11-09', 0.5188016890086083, '', 5),
    (13, '2025-11-09 20:29:10.374918', '2025-11-09', 0.5437791373843165, '', 7);
    """
    
    try:
        print("🔧 CREANDO TABLA FALTANTE EN MYSQL")
        print("=" * 50)
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("SHOW TABLES LIKE 'attendance_attendancerecord'")
        if cursor.fetchone():
            print("⚠️  La tabla attendance_attendancerecord ya existe")
            return True
        
        # Crear la tabla
        print("📝 Creando tabla attendance_attendancerecord...")
        cursor.execute(create_table_sql)
        print("✅ Tabla creada exitosamente")
        
        # Insertar datos
        print("💾 Insertando registros de asistencia...")
        cursor.execute(insert_data_sql)
        print("✅ Datos insertados exitosamente")
        
        # Confirmar cambios
        connection.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM attendance_attendancerecord")
        count = cursor.fetchone()[0]
        print(f"📊 Total de registros de asistencia: {count}")
        
        cursor.close()
        connection.close()
        
        print(f"\n🎉 ¡TABLA CREADA EXITOSAMENTE!")
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_table()
    
    if success:
        print("\n✅ La base de datos MySQL ahora está completa")
        print("📝 Puedes ejecutar test_mysql.py para verificar")
    
    input("\n👆 Presiona Enter para salir...")