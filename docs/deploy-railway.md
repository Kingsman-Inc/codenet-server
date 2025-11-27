# 🚀 CodeNet Server - Deploy no Railway

## 📋 Pré-requisitos

1. Conta no [GitHub](https://github.com)
2. Conta no [Railway](https://railway.app)
3. Git instalado no seu computador

## 🔧 Passo a Passo para Deploy

### 1. Preparar o Repositório GitHub

```powershell
# Navegar até a pasta do projeto
cd "c:\Users\edumps\Desktop\Codenet Server"

# Inicializar git (se ainda não foi inicializado)
git init

# Adicionar todos os arquivos
git add .

# Fazer o commit inicial
git commit -m "Initial commit - CodeNet Server v3.0.0"

# Criar repositório no GitHub e conectar
# Substitua SEU_USUARIO pelo seu nome de usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/codenet-server.git

# Fazer push para o GitHub
git branch -M main
git push -u origin main
```

### 2. Deploy no Railway

#### Opção A: Via Dashboard do Railway (Recomendado)

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Selecione o repositório **codenet-server**
5. O Railway detectará automaticamente o `railway.json` e fará o deploy

#### Opção B: Via Railway CLI

```powershell
# Instalar Railway CLI
npm install -g @railway/cli

# Fazer login
railway login

# Criar novo projeto
railway init

# Fazer deploy
railway up
```

### 3. Configurar Variáveis de Ambiente (Opcional)

No dashboard do Railway, vá em **Variables** e adicione:

```
PORT=8080
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui
```

### 4. Verificar o Deploy

Após o deploy, o Railway fornecerá uma URL como:
```
https://codenet-server-production.up.railway.app
```

Teste o servidor:
```
https://sua-url.railway.app/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-11-21T...",
  "uptime_seconds": 123,
  "connected_apps": 0
}
```

## 📁 Arquivos de Configuração Criados

- ✅ `Procfile` - Comando para iniciar o servidor
- ✅ `railway.json` - Configuração específica do Railway
- ✅ `runtime.txt` - Versão do Python
- ✅ `.gitignore` - Arquivos a ignorar no Git
- ✅ `.env.example` - Exemplo de variáveis de ambiente

## 🔄 Atualizações Futuras

Para fazer updates:

```powershell
git add .
git commit -m "Descrição da atualização"
git push
```

O Railway fará o re-deploy automaticamente!

## 🆘 Troubleshooting

### Erro: "Application failed to respond"
- Verifique se o arquivo `Procfile` está correto
- Confirme que `gunicorn` está em `requirements_v3.txt`

### Erro: "Module not found"
- Verifique o `requirements_v3.txt`
- Tente fazer rebuild no Railway

### Logs do Railway
- Acesse o dashboard do Railway
- Clique no seu projeto
- Vá em **"Deployments"** > **"View Logs"**

## 📞 Suporte

Para mais informações, consulte:
- [Documentação do Railway](https://docs.railway.app)
- [README do CodeNet Server](README_codenet_SERVER.md)

---

**CodeNet Server v3.0.0** - Desenvolvido com ❤️ por CodeNet Inc
