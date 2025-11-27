# CodeNet Server v3.0 - Sistema de Conexão de Apps

## 🎯 O que foi criado?

Sistema completo e moderno para gerenciar conexões de aplicações com o CodeNet Server, incluindo:

### ✨ Novos Arquivos

1. **`CodeNet_server_v3.py`** - Servidor principal com autenticação
2. **`CodeNet_client.py`** - Classe cliente pronta para usar
3. **`test_connection_system.py`** - Testes automatizados
4. **`README_CONNECTION_GUIDE.md`** - Guia completo de integração
5. **`QUICKSTART.md`** - Início rápido
6. **`LAUNCH_SERVER_V3.bat`** - Launcher do servidor
7. **`requirements_v3.txt`** - Dependências atualizadas
8. **`env_example.txt`** - Template de variáveis de ambiente

### 🔑 Principais Funcionalidades

#### Sistema de Autenticação
- **API Keys** - Geradas no registro da aplicação
- **Session Tokens** - Válidos por 24 horas
- **Autenticação Bearer** - Headers padrão da indústria

#### Endpoints

**Públicos:**
- `POST /api/register` - Registrar nova aplicação
- `POST /api/connect` - Conectar aplicação
- `GET /api/health` - Health check
- `GET /api/docs` - Documentação

**Autenticados:**
- `GET /api/status` - Status da sessão
- `POST /api/disconnect` - Desconectar
- `GET /api/apps/list` - Listar apps conectadas

### 📦 Estrutura de Dados

#### Registro de App
```json
{
  "app_id": "app_abc123",
  "api_key": "kgs_...",
  "secret": "...",
  "registered_at": "2025-11-21T...",
  "status": "registered"
}
```

#### Sessão Ativa
```json
{
  "session_token": "sess_...",
  "app_name": "Minha App",
  "expires_at": "2025-11-22T...",
  "requests": 42
}
```

### 🚀 Como Usar

#### 1. Iniciar Servidor
```bash
# Opção 1: Launcher
LAUNCH_SERVER_V3.bat

# Opção 2: Direto
python CodeNet_server_v3.py
```

#### 2. Registrar Aplicação (primeira vez)
```python
from CodeNet_client import CodeNetClient

client = CodeNetClient("http://localhost:8000")

client.register(
    app_name="Minha App",
    app_version="1.0.0",
    platform="Windows"
)
# Credenciais salvas em CodeNet_credentials.json
```

#### 3. Conectar e Usar
```python
# Conectar (usa credenciais salvas)
client.connect()

# Verificar status
status = client.get_status()

# Fazer requisições customizadas
response = client.request('GET', '/api/custom')

# Desconectar
client.disconnect()
```

### 🧪 Testar Sistema

```bash
python test_connection_system.py
```

Executa 10 testes automatizados:
- ✅ Servidor online
- ✅ Health check
- ✅ Documentação
- ✅ Registro de app
- ✅ Conexão
- ✅ Status da sessão
- ✅ Listar apps
- ✅ Autenticação inválida
- ✅ Autenticação ausente
- ✅ Desconexão

### 📚 Documentação

- **Guia Completo:** `README_CONNECTION_GUIDE.md`
  - Fluxo de conexão detalhado
  - Exemplos em Python, JavaScript e C#
  - Boas práticas
  - Troubleshooting

- **Quick Start:** `QUICKSTART.md`
  - Comandos essenciais
  - Endpoints principais
  - Problemas comuns

### 🔒 Segurança

1. **API Keys** armazenadas em arquivo separado
2. **Session Tokens** com expiração de 24h
3. **Logs completos** de todas as operações
4. **Validação de autenticação** em endpoints protegidos

### 📁 Arquivos Gerados Automaticamente

O servidor cria automaticamente:
```
config/
  ├── connected_apps.json      # Apps registradas
  ├── api_keys.json            # Chaves de API
  └── active_sessions.json     # Sessões ativas

logs/
  └── CodeNet_server.log      # Logs do servidor
```

### 🔄 Migração do Sistema Antigo

O sistema v3.0 é **completamente novo** e não depende de apps antigas. Para migrar:

1. Registre suas aplicações novamente via `/api/register`
2. Atualize o código das apps para usar o novo sistema de autenticação
3. Use `CodeNet_client.py` como base

### 🌟 Vantagens do v3.0

- ✅ Autenticação moderna e segura
- ✅ API RESTful completa
- ✅ Sistema de sessões com expiração
- ✅ Logs detalhados
- ✅ Fácil integração
- ✅ Cliente Python pronto
- ✅ Documentação completa
- ✅ Testes automatizados

### 🚀 Próximos Passos

1. Iniciar o servidor v3
2. Testar com `test_connection_system.py`
3. Registrar suas aplicações
4. Integrar usando `CodeNet_client.py`
5. Ler o guia completo em `README_CONNECTION_GUIDE.md`

### 📞 Suporte

- Documentação: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health
- Logs: `logs/CodeNet_server.log`

---

**CodeNet Server v3.0** - Sistema moderno de gerenciamento de conexões 🏛️

