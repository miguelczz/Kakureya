# Kakureya

**Kakureya** es una aplicación web desarrollada con Django que permite gestionar pedidos y despachos de comida japonesa a domicilio. Está orientada a mejorar la experiencia del cliente y optimizar la operación de restaurantes digitales, incluyendo dark kitchens, mediante un sistema robusto, escalable y seguro.

---

## Funcionalidades principales

| Módulo/Componente          | Funcionalidad                                                                |
|----------------------------|------------------------------------------------------------------------------|
| `usuarios/`                | Registro, inicio de sesión, recuperación de contraseña, autenticación con sesiones |
| `productos/`               | Administración de productos: creación, edición, eliminación |
| `menu/`                    | Visualización dinámica del menú clasificado por categorías                  |
| `pedidos/`                 | Carrito de compras, confirmación de pedidos, historial por usuario, estados de pedido |
| `pasarela/`                | Integración con la API de Wompi para pagos en línea                         |
| `templates/` y `static/`   | Interfaz responsiva con archivos HTML, CSS, JS organizados                  |
| `settings.py`              | Configuración separada para entorno local y producción                     |
| `.env` (no incluido)       | Variables sensibles: conexión a PostgreSQL, claves AWS, email, Wompi       |

---

## Tecnologías utilizadas

- Lenguaje backend: Python 3.10+
- Framework web: Django 4.x
- Base de datos: PostgreSQL (entorno de producción), SQLite (modo local de pruebas)
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript
- Control de sesiones: Django Auth con recuperación de contraseña por correo
- Almacenamiento de archivos: AWS S3 para medios estáticos
- Pasarela de pagos: Wompi (API pública y privada)
- Control de versiones: Git

---

## Instalación y ejecución local

Este proyecto cuenta con un script de instalación automatizada (`setup.bat`) para entornos Windows.

### 1. Clonar el repositorio

```bash
git clone https://github.com/miguelczz/Kakureya.git
cd Kakureya
```

### 2. Ejecutar el script de configuración (Windows)
```bash
setup.bat
```
Este script realiza las siguientes acciones:

Crea el entorno virtual en venv/

Instala automáticamente las dependencias listadas en requirements.txt

Crea un archivo .env de ejemplo con los parámetros necesarios

### 3. Configurar el archivo .env

Editar con los valores reales correspondientes:

```bash
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/kakureya

AWS_ACCESS_KEY_ID=clave_de_acceso_aws
AWS_SECRET_ACCESS_KEY=clave_secreta_aws
AWS_STORAGE_BUCKET_NAME=nombre_del_bucket_s3
AWS_S3_REGION_NAME=region

EMAIL_USER=correo@gmail.com
EMAIL_PASSWORD=contraseña_de_aplicación

WOMPI_PUBLIC_KEY=clave_pública_wompi
WOMPI_INTEGRITY_SECRET=clave_de_integridad_wompi
```

### 4. Ejecutar migraciones y crear superusuario
```bash
python manage.py migrate
python manage.py createsuperuser}
```

### 5. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```
