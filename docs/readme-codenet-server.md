# 🖥️ CodeNet SERVER - DOCUMENTAÇÃO COMPLETA

## 📋 VISÃO GERAL

O **CodeNet Server** é o sistema de backend completo que suporta o CodeNet Menu. Foi separado em uma pasta independente para facilitar manutenção e deployment.

---

## 🗂️ ESTRUTURA DO SERVIDOR

### 🔧 Core/ - Sistema Principal
```
CodeNet_server_production.py     # Servidor de produção completo
CodeNet_server_production_fixed.py # Versão corrigida
CodeNet_server_simple.py         # Versão simplificada para testes
test_server_simple.py            # Script de testes
requirements.txt                  # Dependências Python
.env.example                     # Exemplo de configuração
Procfile                         # Configuração Railway/Heroku
railway.json                     # Configuração Railway
render.yaml                      # Configuração Render
shutdown_state.json              # Estado de shutdown
dependency_check.json            # Verificação de dependências
check_dependencies.py            # Script de verificação
```

### 📁 Subpastas Core:
- **backups/**: Backups automáticos do servidor
- **config/**: Arquivos de configuração
- **deployment/**: Scripts de deployment (Railway, Render)
- **logs/**: Logs do servidor

### 🚀 Deployment/ - Sistema de Deploy
```
Core/
├── version.json                  # Controle de versões
├── CHANGELOG.md                  # Histórico de mudanças
├── patches.json                  # Sistema de patches
├── distribution.log              # Log de distribuição
├── registered_devices.json       # Dispositivos registrados
├── sync_status.json             # Status de sincronização
├── update_manifest.json         # Manifesto de atualizações
├── notification_v1.4.json       # Notificações v1.4
├── downloads/                    # Arquivos para download
│   ├── complete/                # Downloads completos
│   ├── patch/                   # Downloads de patch
│   └── updater/                 # Downloads do updater
├── patches/                     # Patches disponíveis
└── updates/                     # Atualizações disponíveis
```

### 📊 Monitoring/ - Sistema de Monitoramento
```
CodeNetServerMonitor_v1.1.0/    # Monitor v1.1.0
CodeNetServerMonitor_v1.0.0.exe # Monitor v1.0.0
CodeNetServerMonitor_v1.1.0_Final.exe # Monitor v1.1.0 Final
CodeNetServerMonitor_v2.0.0_InfrastructureComplete.exe # Monitor v2.0.0
```

### 📖 Documentation/
```
SISTEMA_SERVIDOR_CodeNet.md     # Documentação completa do sistema
```

---

## 🚀 CONFIGURAÇÃO E DEPLOY

### 🐍 Requisitos Python
```bash
# Instalar dependências
pip install -r Core/requirements.txt

# Principais dependências:
- Flask >= 2.3.0
- flask-cors >= 4.0.0
- requests >= 2.31.0
- python-dotenv >= 1.0.0
- gunicorn >= 21.0.0 (produção)
```

### 🌐 Deploy Railway
```bash
# Usar arquivo railway.json já configurado
railway login
railway deploy
```

### 🎯 Deploy Render
```yaml
# Usar arquivo render.yaml já configurado
# Conectar repositório no Render.com
# Deploy automático ativado
```

### 🐳 Deploy Local
```bash
# Servidor simples (desenvolvimento)
python Core/CodeNet_server_simple.py

# Servidor de produção (local)
python Core/CodeNet_server_production.py

# Com Gunicorn (produção)
gunicorn -w 4 -b 0.0.0.0:8000 CodeNet_server_production:app
```

---

## 🔧 FUNCIONALIDADES

### 📡 API Endpoints
- **GET /api/health** - Status de saúde do servidor
- **GET /api/status** - Status detalhado do sistema
- **GET /api/version** - Informações de versão
- **GET /api/updates** - Verificar atualizações
- **POST /api/register** - Registrar dispositivo
- **GET /api/download/{type}** - Downloads de arquivos

### 🔄 Sistema de Updates
- Verificação automática de atualizações
- Distribuição de patches incrementais
- Sincronização com dispositivos registrados
- Backup automático antes de updates

### 📊 Monitoramento
- Logs estruturados em JSON
- Métricas de performance
- Status de conectividade
- Alertas automáticos

### 🛡️ Segurança
- Verificação de integridade de arquivos
- Rate limiting automático
- Validação de requests
- Logs de auditoria

---

## 🔄 SISTEMA DE UPDATES

### 📋 Controle de Versões
```json
{
  "current_version": "1.4.2",
  "latest_version": "1.4.2",
  "update_available": false,
  "last_check": "2025-10-20T12:00:00Z"
}
```

### 🔧 Sistema de Patches
```json
{
  "patch_id": "1.4.2",
  "type": "security",
  "priority": "high",
  "files_changed": ["CodeNet_menu.py"],
  "size_mb": 1.2
}
```

### 📱 Dispositivos Registrados
```json
{
  "device_id": "unique_device_id",
  "version": "1.4.2",
  "last_sync": "2025-10-20T12:00:00Z",
  "platform": "windows"
}
```

---

## 📊 MONITORAMENTO

### 📈 Métricas Coletadas
- **Uptime**: Tempo de atividade do servidor
- **Requests**: Número de requisições por minuto
- **Errors**: Taxa de erro das requisições
- **Memory**: Uso de memória do servidor
- **CPU**: Uso de CPU do servidor
- **Storage**: Uso de armazenamento

### 🚨 Alertas Configurados
- **Server Down**: Servidor fora do ar > 5 minutos
- **High Error Rate**: Taxa de erro > 10%
- **Memory Usage**: Uso de memória > 90%
- **Disk Space**: Espaço em disco < 10%

### 📊 Dashboard de Monitoramento
Acesse via executáveis de monitoramento:
- `CodeNetServerMonitor_v2.0.0_InfrastructureComplete.exe` (Recomendado)
- `CodeNetServerMonitor_v1.1.0_Final.exe`

---

## 🔒 SEGURANÇA

### 🛡️ Medidas Implementadas
- **HTTPS Obrigatório**: Todas as comunicações criptografadas
- **Rate Limiting**: Proteção contra ataques DDoS
- **Input Validation**: Validação rigorosa de entradas
- **Error Handling**: Tratamento seguro de erros
- **Audit Logs**: Logs de auditoria completos

### 🔐 Configurações de Segurança
```python
# Rate limiting
RATELIMIT_STORAGE_URL = "memory://"
RATELIMIT_DEFAULT = "100 per hour"

# CORS configurado para domínios específicos
CORS_ORIGINS = ["https://CodeNet-inc.github.io"]

# Headers de segurança
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block"
}
```

---

## 🧪 TESTES

### 🔬 Scripts de Teste
```bash
# Teste básico de conectividade
python Core/test_server_simple.py

# Teste de funcionalidades específicas
python Core/deployment/test_complete_system.py

# Verificação de dependências
python Core/check_dependencies.py
```

### 📋 Checklist de Testes
- [ ] Servidor inicia sem erros
- [ ] Endpoints respondem corretamente
- [ ] Sistema de updates funcional
- [ ] Monitoramento ativo
- [ ] Logs sendo gerados
- [ ] Backups automáticos funcionando

---

## 🆘 TROUBLESHOOTING

### ❌ Problemas Comuns

**1. Servidor não inicia**
```bash
# Verificar dependências
python Core/check_dependencies.py

# Verificar logs
tail -f Core/logs/server.log
```

**2. Erro de conexão**
```bash
# Verificar portas
netstat -tulpn | grep :8000

# Verificar firewall
sudo ufw status
```

**3. Updates não funcionam**
```bash
# Verificar permissões
ls -la Core/deployment/Core/

# Recriar manifesto
python Core/deployment/setup_environment.py
```

### 🔧 Comandos Úteis
```bash
# Restart do servidor
pkill -f CodeNet_server && python Core/CodeNet_server_production.py

# Backup manual
cp -r Core/deployment/Core/ backups/manual_$(date +%Y%m%d_%H%M%S)/

# Limpar logs antigos
find Core/logs/ -name "*.log" -mtime +7 -delete
```

---

## 📞 CONTATO E SUPORTE

- **Documentação Técnica**: `Documentation/SISTEMA_SERVIDOR_CodeNet.md`
- **Logs**: `Core/logs/server.log`
- **Status**: Execute qualquer monitor em `Monitoring/`
- **Configuração**: Edite `Core/.env`

---

✅ **SISTEMA SERVIDOR COMPLETO E FUNCIONAL** ✅

*Documentação atualizada em 20 de outubro de 2025 - CodeNet Inc.*
