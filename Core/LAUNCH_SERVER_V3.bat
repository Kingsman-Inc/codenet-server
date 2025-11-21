@echo off
echo ========================================
echo   CodeNet SERVER v3.0 - LAUNCHER
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar dependências
echo Verificando dependencias...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar dependencias
        pause
        exit /b 1
    )
)

echo [OK] Dependencias instaladas
echo.

REM Criar pastas necessárias
if not exist "config" mkdir config
if not exist "logs" mkdir logs

echo ========================================
echo   INICIANDO SERVIDOR...
echo ========================================
echo.
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/api/docs
echo.
echo Pressione Ctrl+C para parar
echo ========================================
echo.

REM Iniciar servidor
python CodeNet_server_v3.py

pause

