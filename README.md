# 🍣 Kakureya – Sistema Web de Pedidos de Comida Japonesa

**Kakureya** es una aplicación web desarrollada en Django que permite gestionar eficientemente pedidos y despachos de comida japonesa a domicilio. Su objetivo es mejorar la experiencia del cliente y optimizar la operación interna de restaurantes digitales o dark kitchens.

Este sistema cuenta con autenticación de usuarios, visualización de menú, carrito de compras y una interfaz de administración para gestionar productos y pedidos. Está diseñado con un enfoque modular, responsivo y seguro, ideal para negocios gastronómicos emergentes.

---

## 📸 Capturas de pantalla (opcional)

<!-- Puedes agregar imágenes si las tienes disponibles -->
<!-- 
<img src="assets/images/inicio.png" alt="Inicio"/>
<img src="assets/images/menu.png" alt="Menú"/>
<img src="assets/images/pedido.png" alt="Pedido"/>
<img src="assets/images/admin.png" alt="Administración"/>
-->

---

## 🚀 Funcionalidades principales

| Módulo                     | Funcionalidad                                                                 |
|----------------------------|-------------------------------------------------------------------------------|
| `usuarios/`                | Registro, inicio de sesión, autenticación segura, encriptación de contraseñas |
| `productos/`               | Administración de productos: creación, edición y eliminación                  |
| `menu/`                    | Visualización pública del menú clasificado por categoría                     |
| `pedidos/`                 | Carrito de compras, confirmación de pedidos, historial por usuario            |
| `templates/`               | Vistas HTML organizadas por sección                                          |
| `static/`                  | Archivos CSS, JS, imágenes y recursos de interfaz                             |
| `core/`                    | Configuración global, rutas, modelos compartidos                             |
| `.env` (no incluido)       | Variables sensibles como claves y conexiones (no debe compartirse)           |

---

## 🛠️ Stack tecnológico

- **Backend:** Django 4.x (Python 3.10+)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Base de datos:** SQLite (modo local)
- **Estilo visual:** Plantillas personalizadas, interfaz responsiva
- **Control de versiones:** Git + GitHub
- **Persistencia de sesión:** Django Auth
- **Despliegue (opcional):** Compatible con Heroku, Render u otras plataformas

---

## ⚙️ Instalación y ejecución local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu_usuario/Kakureya.git
cd Kakureya
