@echo off
echo =====================================
echo = Configuración del Entorno Virtual =
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

echo ====================================
echo = Entorno Configurado Exitosamente =
echo ====================================
