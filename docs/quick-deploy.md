# 🚀 Deploy Rápido - CodeNet Server no Railway

## ✅ Status: Git Inicializado

O repositório Git já foi inicializado e o commit inicial foi criado!

## 📝 Próximos Passos

### 1. Criar Repositório no GitHub

Acesse: https://github.com/new

- **Nome**: `codenet-server`
- **Visibilidade**: Público
- **NÃO** marque: "Add README", "Add .gitignore" ou "Choose license"
- Clique em **"Create repository"**

### 2. Conectar e Enviar o Código

Após criar o repositório, execute no PowerShell:

```powershell
cd "c:\Users\edumps\Desktop\Codenet Server"

# Substitua SEU_USUARIO pelo seu usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/codenet-server.git
git branch -M main
git push -u origin main
```

**Exemplo**:
Se seu usuário é `joaosilva`, use:
```powershell
git remote add origin https://github.com/joaosilva/codenet-server.git
```

### 3. Deploy no Railway

1. Acesse: https://railway.app
2. Faça login (pode usar sua conta GitHub)
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub repo"**
5. Autorize o Railway a acessar seus repositórios
6. Selecione o repositório **codenet-server**
7. Aguarde o deploy (2-3 minutos)

### 4. Obter a URL do Servidor

Após o deploy:
1. Clique no seu projeto no Railway
2. Vá em **"Settings"** > **"Networking"**
3. Clique em **"Generate Domain"**
4. Copie a URL gerada (exemplo: `codenet-server-production.up.railway.app`)

### 5. Testar o Servidor

Acesse no navegador ou use curl:

```
https://sua-url.railway.app/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-11-21T...",
  "uptime_seconds": 45,
  "connected_apps": 0
}
```

## 🔄 Atualizações Futuras

Para atualizar o servidor após mudanças:

```powershell
cd "c:\Users\edumps\Desktop\Codenet Server"
git add .
git commit -m "Descrição da atualização"
git push
```

O Railway fará o deploy automático!

## 🛠️ Arquivos Criados para Deploy

- ✅ `Procfile` - Comando de inicialização
- ✅ `railway.json` - Configuração do Railway
- ✅ `runtime.txt` - Versão do Python
- ✅ `.gitignore` - Arquivos ignorados
- ✅ `.env.example` - Exemplo de variáveis

## 🆘 Problemas Comuns

### Erro ao fazer push
Se der erro de autenticação, configure suas credenciais:
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### Deploy falhou no Railway
- Verifique os logs no dashboard do Railway
- Confirme que o `Procfile` está na raiz do projeto
- Verifique se `requirements_v3.txt` tem o `gunicorn`

## 📚 Documentação Completa

Para mais detalhes, veja: `DEPLOY_RAILWAY.md`

---

**CodeNet Server v3.0.0** 🚀
