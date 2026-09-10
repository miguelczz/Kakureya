# Kakureya

**Kakureya** is a web application built with Django that manages orders and deliveries for Japanese food takeout. It's designed to improve the customer experience and streamline the operation of digital restaurants, including dark kitchens, through an efficient system.

<div align="center">

<img src="kakureya/static/images/readme/inicio.png" alt="Home" width="800"/>

<br><br>

<img src="kakureya/static/images/readme/carrito.png" alt="Cart" width="800"/>

<br><br>

<img src="kakureya/static/images/readme/pasarela.png" alt="Payment Gateway" width="800"/>

<br><br>

<img src="kakureya/static/images/readme/contrasennia.png" alt="Password" width="800"/>

<br><br>

<h3>🏆 Certificate — Best PPI T&T Project, Third Semester Category, 2025-1</h3>

<img src="https://github.com/miguelczz/miguelczz/blob/main/certificado-kakureya.png?raw=true&v=2"
     alt="Kakureya Certificate"
     width="600"/>

</div>

---

## Main Features

| Module/Component          | Functionality                                                                |
|----------------------------|------------------------------------------------------------------------------|
| `usuarios/`                | User registration, login, password recovery, session-based authentication   |
| `productos/`               | Product management: creation, editing, deletion                             |
| `menu/`                    | Dynamic menu display organized by category                                  |
| `pedidos/`                 | Shopping cart, order confirmation, per-user order history, order status tracking |
| `pasarela/`                | Integration with the Wompi API for online payments                          |
| `templates/` and `static/` | Responsive UI with organized HTML, CSS, and JS files                        |
| `settings.py`              | Separate configuration for local and production environments                |
| `.env` (not included)      | Sensitive variables: PostgreSQL connection, AWS keys, email, Wompi          |

---

## Technologies Used

- Backend language: Python 3.10+
- Web framework: Django 4.x
- Database: PostgreSQL (production environment), SQLite (local testing mode)
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript
- Session management: Django Auth with email-based password recovery
- File storage: AWS S3 for static media
- Payment gateway: Wompi (public and private API)
- Version control: Git

---

## Local Installation & Setup

This project includes an automated installation script (`setup.bat`) for Windows environments.

### 1. Clone the repository

```bash
git clone https://github.com/miguelczz/Kakureya.git
cd Kakureya
```
