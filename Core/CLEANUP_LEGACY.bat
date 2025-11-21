@echo off
echo ========================================
echo   LIMPEZA DE ARQUIVOS LEGADOS
echo   CodeNet Server v3.0
echo ========================================
echo.
echo Este script ira remover arquivos antigos
echo para otimizar o sistema v3.0
echo.
echo ATENCAO: Esta acao nao pode ser desfeita!
echo.
pause

python cleanup_legacy_files.py

echo.
echo ========================================
echo   Limpeza concluida!
echo ========================================
pause

