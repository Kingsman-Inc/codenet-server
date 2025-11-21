@echo off
REM 🚀 KINGSMAN SERVER - RAILWAY SETUP (WINDOWS)
REM Script para configuração automática no Railway.app

echo 🚀 Kingsman Server - Railway Setup Automation
echo ==============================================

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado! Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

REM Instalar Railway CLI
echo 📦 Installing Railway CLI...
npm install -g @railway/cli

REM Login no Railway
echo 🔐 Logging into Railway...
echo ℹ️  Você precisará fazer login no browser que será aberto
railway login

REM Navegar para a pasta do servidor
cd /d "%~dp0.."

REM Inicializar projeto
echo 🏗️ Creating new Railway project...
railway init kingsman-server

REM Configurar variáveis de ambiente
echo ⚙️ Setting up environment variables...
railway vars set PYTHONUNBUFFERED=1
railway vars set HOST=0.0.0.0
railway vars set DEBUG=False
railway vars set LOG_LEVEL=INFO
railway vars set HEALTH_CHECK_INTERVAL=30
railway vars set BACKUP_INTERVAL=3600

REM Deploy inicial
echo 🚀 Deploying to Railway...
railway deploy

echo ✅ Railway setup completed!
echo 🔗 Your server will be available at the provided Railway URL
echo 📊 Monitor your deployment at: https://railway.app/dashboard
pause