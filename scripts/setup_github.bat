@echo off
chcp 65001 >nul
echo ================================================
echo    CodeNet Server - GitHub Setup
echo ================================================
echo.
echo Digite seu usuário do GitHub:
set /p GITHUB_USER="Usuário: "
echo.
echo ================================================
echo Conectando ao GitHub...
echo ================================================
echo.

cd "c:\Users\edumps\Desktop\Codenet Server"

git remote add origin https://github.com/%GITHUB_USER%/codenet-server.git
git branch -M main
git push -u origin main

echo.
echo ================================================
echo ✅ Código enviado com sucesso!
echo ================================================
echo.
echo Próximo passo: Deploy no Railway
echo 1. Acesse: https://railway.app
echo 2. Clique em "New Project"
echo 3. Selecione "Deploy from GitHub repo"
echo 4. Escolha: %GITHUB_USER%/codenet-server
echo.
echo Pressione qualquer tecla para abrir o Railway...
pause >nul
start https://railway.app/new
