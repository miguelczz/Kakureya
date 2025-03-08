@echo off
echo =====================================
echo = Configuracion del Entorno Virtual 
echo =====================================

:: Verificar si el entorno virtual existe
if exist venv (
    echo El entorno virtual ya existe.
) else (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar el entorno virtual
echo Activando el entorno virtual...
call venv\Scripts\activate

:: Instalar dependencias
echo Instalando dependencias...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo El archivo requirements.txt no existe. Instalación cancelada.
    exit /b 1
)

:: Crear el archivo .env si no existe
echo.
echo =====================================
echo = Configuracion de variables de entorno =
echo =====================================

if exist .env (
    echo El archivo .env ya existe. No se modificará.
) else (
    echo Creando archivo .env...
    echo DATABASE_URL=postgresql://postgres:contraseña@localhost/kakureya > .env
    echo Archivo .env creado con éxito.
)

echo ====================================
echo = Entorno Configurado Exitosamente =
echo ====================================
