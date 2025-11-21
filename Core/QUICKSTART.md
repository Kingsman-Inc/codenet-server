# 🚀 CodeNet Server v3.0 - Quick Start

## 🎯 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar Servidor

```bash
python CodeNet_server_v3.py
```

O servidor iniciará em `http://localhost:8000`

### 3. Testar Sistema

```bash
python test_connection_system.py
```

---

## 📁 Arquivos Importantes

### Servidor
- `CodeNet_server_v3.py` - Servidor principal
- `requirements.txt` - Dependências Python

### Configuração (criados automaticamente)
- `config/connected_apps.json` - Apps registradas
- `config/api_keys.json` - Chaves de API
- `config/active_sessions.json` - Sessões ativas

### Logs
- `logs/CodeNet_server.log` - Logs do servidor

### Documentação
- `README_CONNECTION_GUIDE.md` - Guia completo de conexão

---

## 🔗 Fluxo Básico

### Para uma Nova Aplicação

```python
import requests

# 1. REGISTRAR (apenas uma vez)
response = requests.post('http://localhost:8000/api/register', json={
    "app_name": "Minha App",
    "app_version": "1.0.0",
    "platform": "Windows"
})

api_key = response.json()['data']['api_key']
# SALVAR API_KEY EM LOCAL SEGURO!

# 2. CONECTAR
response = requests.post('http://localhost:8000/api/connect', json={
    "api_key": api_key
})

session_token = response.json()['data']['session_token']

# 3. USAR (com autenticação)
headers = {"Authorization": f"Bearer {session_token}"}

response = requests.get(
    'http://localhost:8000/api/status',
    headers=headers
)

print(response.json())
```

---

## 📡 Endpoints Principais

### Públicos
- `GET /` - Info do servidor
- `GET /api/docs` - Documentação
- `GET /api/health` - Health check
- `POST /api/register` - Registrar app
- `POST /api/connect` - Conectar app

### Autenticados (requer session token)
- `GET /api/status` - Status da sessão
- `POST /api/disconnect` - Desconectar
- `GET /api/apps/list` - Listar apps

---

## 🔐 Segurança

### API Key
- Gerada no registro
- Use apenas em backend
- Não compartilhe publicamente
- Salve em arquivo `.env` ou similar

### Session Token
- Válido por 24 horas
- Deve ser enviado no header Authorization
- Formato: `Bearer <token>`

---

## 🛠️ Comandos Úteis

### Iniciar Servidor
```bash
python CodeNet_server_v3.py
```

### Testar Sistema
```bash
python test_connection_system.py
```

### Ver Logs
```bash
# Windows PowerShell
Get-Content logs\CodeNet_server.log -Tail 50

# Linux/Mac
tail -f logs/CodeNet_server.log
```

### Limpar Dados (resetar apps)
```bash
# Windows PowerShell
Remove-Item config\*.json

# Linux/Mac
rm config/*.json
```

---

## 📞 Problemas Comuns

### "Conexão recusada"
- Verifique se o servidor está rodando
- Confirme a URL (porta 8000 por padrão)

### "API key inválida"
- Verifique se registrou a aplicação
- Confirme se a API key está correta
- Não há espaços extras na key

### "Sessão expirada"
- Session tokens duram 24h
- Reconecte com sua API key

---

## 📚 Documentação Completa

Ver arquivo: `README_CONNECTION_GUIDE.md`

---

## 🆕 Novidades v3.0

✨ Sistema de autenticação com API Keys
✨ Session tokens com expiração
✨ Gerenciamento de apps conectadas
✨ Sistema de logging completo
✨ Endpoints autenticados
✨ Documentação completa

---

## 📄 Licença

MIT License - CodeNet Inc © 2025

