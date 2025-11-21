# 🚀 Script de Deploy Automático - CodeNet Server

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   CodeNet Server - Deploy no Railway" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está na pasta correta
$currentPath = Get-Location
if ($currentPath.Path -notlike "*Codenet Server*") {
    Write-Host "❌ Execute este script na pasta do Codenet Server!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pasta correta verificada!" -ForegroundColor Green
Write-Host ""

# Passo 1: Verificar Git
Write-Host "📋 Passo 1/5: Verificando Git..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ Git não está instalado! Baixe em: https://git-scm.com" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git instalado!" -ForegroundColor Green
Write-Host ""

# Passo 2: Criar repositório no GitHub
Write-Host "📋 Passo 2/5: Criar Repositório no GitHub" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  AÇÃO NECESSÁRIA:" -ForegroundColor Yellow
Write-Host "1. Acesse: https://github.com/new" -ForegroundColor White
Write-Host "2. Nome do repositório: codenet-server" -ForegroundColor White
Write-Host "3. Deixe como PÚBLICO" -ForegroundColor White
Write-Host "4. NÃO inicialize com README, .gitignore ou license" -ForegroundColor White
Write-Host "5. Clique em 'Create repository'" -ForegroundColor White
Write-Host ""
$continue = Read-Host "Pressione ENTER após criar o repositório no GitHub..."

Write-Host ""
Write-Host "Digite o nome do seu usuário do GitHub:" -ForegroundColor Cyan
$githubUser = Read-Host "Usuário"

if ([string]::IsNullOrWhiteSpace($githubUser)) {
    Write-Host "❌ Usuário não pode estar vazio!" -ForegroundColor Red
    exit 1
}

# Passo 3: Conectar ao GitHub
Write-Host ""
Write-Host "📋 Passo 3/5: Conectando ao GitHub..." -ForegroundColor Yellow
$repoUrl = "https://github.com/$githubUser/codenet-server.git"

try {
    git remote add origin $repoUrl
    Write-Host "✅ Repositório conectado!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Remote já existe, atualizando URL..." -ForegroundColor Yellow
    git remote set-url origin $repoUrl
}

# Passo 4: Push para GitHub
Write-Host ""
Write-Host "📋 Passo 4/5: Enviando código para GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  Você pode precisar fazer login no GitHub" -ForegroundColor Yellow
Write-Host ""

try {
    git branch -M main
    git push -u origin main
    Write-Host "✅ Código enviado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao enviar código. Verifique suas credenciais do GitHub." -ForegroundColor Red
    Write-Host "Tente executar manualmente: git push -u origin main" -ForegroundColor Yellow
    exit 1
}

# Passo 5: Instruções Railway
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📋 Passo 5/5: Deploy no Railway" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Agora vamos fazer o deploy no Railway:" -ForegroundColor White
Write-Host ""
Write-Host "1️⃣  Acesse: https://railway.app" -ForegroundColor Green
Write-Host "2️⃣  Faça login (pode usar GitHub)" -ForegroundColor Green
Write-Host "3️⃣  Clique em 'New Project'" -ForegroundColor Green
Write-Host "4️⃣  Selecione 'Deploy from GitHub repo'" -ForegroundColor Green
Write-Host "5️⃣  Selecione: $githubUser/codenet-server" -ForegroundColor Green
Write-Host "6️⃣  Aguarde o deploy automático (2-3 minutos)" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Quando o deploy terminar, você receberá uma URL como:" -ForegroundColor Cyan
Write-Host "   https://codenet-server-production.up.railway.app" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Teste o servidor acessando:" -ForegroundColor Cyan
Write-Host "   https://sua-url.railway.app/api/health" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Setup concluído com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Documentação completa em: DEPLOY_RAILWAY.md" -ForegroundColor Yellow
Write-Host ""

# Abrir browser
$openBrowser = Read-Host "Deseja abrir o Railway no browser agora? (S/N)"
if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
    Start-Process "https://railway.app/new"
}

Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
