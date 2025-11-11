# Configuración MySQL para AWS RDS
# Copia esta configuración a tu settings.py cuando estés listo para usar MySQL

MYSQL_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nandu',
        'USER': 'admin',
        'PASSWORD': 'admin123',
        'HOST': 'nandu.czmoey4oapii.sa-east-1.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# También puedes usar variables de entorno para mayor seguridad:
import os

MYSQL_CONFIG_ENV = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'nandu'),
        'USER': os.getenv('MYSQL_USER', 'admin'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'admin123'),
        'HOST': os.getenv('MYSQL_HOST', 'nandu.czmoey4oapii.sa-east-1.rds.amazonaws.com'),
        'PORT': os.getenv('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}