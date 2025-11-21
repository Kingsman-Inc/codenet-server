#!/bin/bash
# 🚀 KINGSMAN SERVER - RAILWAY SETUP AUTOMATION
# Script para configuração automática no Railway.app

echo "🚀 Kingsman Server - Railway Setup Automation"
echo "=============================================="

# Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login no Railway (será solicitado token)
echo "🔐 Logging into Railway..."
railway login

# Criar novo projeto
echo "🏗️ Creating new Railway project..."
railway init kingsman-server

# Configurar variáveis de ambiente
echo "⚙️ Setting up environment variables..."
railway vars set PYTHONUNBUFFERED=1
railway vars set HOST=0.0.0.0
railway vars set DEBUG=False
railway vars set LOG_LEVEL=INFO
railway vars set HEALTH_CHECK_INTERVAL=30
railway vars set BACKUP_INTERVAL=3600

# Deploy inicial
echo "🚀 Deploying to Railway..."
railway deploy

# Configurar domínio personalizado (opcional)
echo "🌐 Setting up custom domain..."
railway domain

echo "✅ Railway setup completed!"
echo "🔗 Your server will be available at the provided Railway URL"
echo "📊 Monitor your deployment at: https://railway.app/dashboard"