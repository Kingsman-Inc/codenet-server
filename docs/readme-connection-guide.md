# 🔗 Guia de Conexão - CodeNet Server v3.0

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Registro de Aplicação](#registro-de-aplicação)
- [Autenticação](#autenticação)
- [Exemplos de Código](#exemplos-de-código)
- [Endpoints Disponíveis](#endpoints-disponíveis)
- [Boas Práticas](#boas-práticas)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O CodeNet Server v3.0 utiliza um sistema moderno de autenticação baseado em **API Keys** e **Session Tokens** para gerenciar conexões de aplicações.

### Fluxo de Conexão

```
1. Registro    → Recebe API Key + Secret
2. Conexão     → Recebe Session Token (válido por 24h)
3. Requisições → Usa Session Token no header Authorization
4. Desconexão  → Invalida Session Token
```

---

## 📝 Registro de Aplicação

### 1. Fazer Requisição de Registro

**Endpoint:** `POST /api/register`

**Body (JSON):**
```json
{
  "app_name": "Minha Aplicação",
  "app_version": "1.0.0",
  "platform": "Windows",
  "description": "Descrição da aplicação (opcional)"
}
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "data": {
    "app_id": "app_abc123def456",
    "api_key": "kgs_1234567890abcdef1234567890abcdef",
    "secret": "secret_1234567890abcdef1234567890abcdef",
    "message": "Aplicação registrada com sucesso"
  },
  "message": "⚠️ IMPORTANTE: Salve o API Key e Secret em local seguro!"
}
```

### ⚠️ IMPORTANTE
- **Salve o `api_key` e `secret` imediatamente!**
- Eles não serão mostrados novamente
- Guarde em variáveis de ambiente ou arquivo de configuração seguro

---

## 🔐 Autenticação

### 2. Conectar ao Servidor

**Endpoint:** `POST /api/connect`

**Body (JSON):**
```json
{
  "api_key": "kgs_1234567890abcdef1234567890abcdef"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "session_token": "sess_abcdef1234567890abcdef1234567890",
    "app_name": "Minha Aplicação",
    "expires_in": "24 hours",
    "message": "Conexão estabelecida"
  }
}
```

### 3. Usar Session Token

Para todas as requisições autenticadas, adicione o header:

```
Authorization: Bearer sess_abcdef1234567890abcdef1234567890
```

---

## 💻 Exemplos de Código

### Python

```python
import requests
import json

class CodeNetClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.api_key = None
        self.session_token = None
    
    def register(self, app_name, app_version, platform, description=""):
        """Registra a aplicação no servidor"""
        url = f"{self.server_url}/api/register"
        
        data = {
            "app_name": app_name,
            "app_version": app_version,
            "platform": platform,
            "description": description
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.api_key = result['data']['api_key']
            
            # SALVAR EM ARQUIVO SEGURO
            with open('CodeNet_credentials.json', 'w') as f:
                json.dump({
                    'api_key': result['data']['api_key'],
                    'secret': result['data']['secret'],
                    'app_id': result['data']['app_id']
                }, f)
            
            print("✅ Registrado com sucesso!")
            print("⚠️ Credenciais salvas em CodeNet_credentials.json")
            return True
        else:
            print(f"❌ Erro no registro: {response.json()}")
            return False
    
    def connect(self, api_key=None):
        """Conecta ao servidor"""
        if api_key:
            self.api_key = api_key
        
        if not self.api_key:
            print("❌ API Key não fornecida")
            return False
        
        url = f"{self.server_url}/api/connect"
        data = {"api_key": self.api_key}
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.session_token = result['data']['session_token']
            print("✅ Conectado com sucesso!")
            return True
        else:
            print(f"❌ Erro na conexão: {response.json()}")
            return False
    
    def get_status(self):
        """Verifica status da sessão"""
        if not self.session_token:
            print("❌ Não conectado")
            return None
        
        url = f"{self.server_url}/api/status"
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro: {response.json()}")
            return None
    
    def disconnect(self):
        """Desconecta do servidor"""
        if not self.session_token:
            print("❌ Não conectado")
            return False
        
        url = f"{self.server_url}/api/disconnect"
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Desconectado com sucesso!")
            self.session_token = None
            return True
        else:
            print(f"❌ Erro ao desconectar: {response.json()}")
            return False


# EXEMPLO DE USO
if __name__ == "__main__":
    client = CodeNetClient("http://localhost:8000")
    
    # PRIMEIRA VEZ - REGISTRAR
    # client.register(
    #     app_name="Minha App",
    #     app_version="1.0.0",
    #     platform="Windows",
    #     description="Aplicação de teste"
    # )
    
    # CONEXÕES SUBSEQUENTES - USAR API KEY SALVA
    with open('CodeNet_credentials.json', 'r') as f:
        credentials = json.load(f)
    
    # Conectar
    if client.connect(credentials['api_key']):
        # Verificar status
        status = client.get_status()
        print(f"Status: {status}")
        
        # Fazer outras requisições...
        
        # Desconectar
        client.disconnect()
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

class CodeNetClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.apiKey = null;
        this.sessionToken = null;
    }
    
    async register(appName, appVersion, platform, description = '') {
        try {
            const response = await axios.post(`${this.serverUrl}/api/register`, {
                app_name: appName,
                app_version: appVersion,
                platform: platform,
                description: description
            });
            
            if (response.status === 201) {
                this.apiKey = response.data.data.api_key;
                
                // Salvar credenciais
                const credentials = {
                    api_key: response.data.data.api_key,
                    secret: response.data.data.secret,
                    app_id: response.data.data.app_id
                };
                
                fs.writeFileSync(
                    'CodeNet_credentials.json',
                    JSON.stringify(credentials, null, 2)
                );
                
                console.log('✅ Registrado com sucesso!');
                console.log('⚠️ Credenciais salvas em CodeNet_credentials.json');
                return true;
            }
        } catch (error) {
            console.error('❌ Erro no registro:', error.response?.data || error.message);
            return false;
        }
    }
    
    async connect(apiKey = null) {
        if (apiKey) {
            this.apiKey = apiKey;
        }
        
        if (!this.apiKey) {
            console.error('❌ API Key não fornecida');
            return false;
        }
        
        try {
            const response = await axios.post(`${this.serverUrl}/api/connect`, {
                api_key: this.apiKey
            });
            
            if (response.status === 200) {
                this.sessionToken = response.data.data.session_token;
                console.log('✅ Conectado com sucesso!');
                return true;
            }
        } catch (error) {
            console.error('❌ Erro na conexão:', error.response?.data || error.message);
            return false;
        }
    }
    
    async getStatus() {
        if (!this.sessionToken) {
            console.error('❌ Não conectado');
            return null;
        }
        
        try {
            const response = await axios.get(`${this.serverUrl}/api/status`, {
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`
                }
            });
            
            return response.data;
        } catch (error) {
            console.error('❌ Erro:', error.response?.data || error.message);
            return null;
        }
    }
    
    async disconnect() {
        if (!this.sessionToken) {
            console.error('❌ Não conectado');
            return false;
        }
        
        try {
            const response = await axios.post(`${this.serverUrl}/api/disconnect`, {}, {
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`
                }
            });
            
            if (response.status === 200) {
                console.log('✅ Desconectado com sucesso!');
                this.sessionToken = null;
                return true;
            }
        } catch (error) {
            console.error('❌ Erro ao desconectar:', error.response?.data || error.message);
            return false;
        }
    }
}

// EXEMPLO DE USO
(async () => {
    const client = new CodeNetClient('http://localhost:8000');
    
    // Carregar credenciais
    const credentials = JSON.parse(
        fs.readFileSync('CodeNet_credentials.json', 'utf8')
    );
    
    // Conectar
    if (await client.connect(credentials.api_key)) {
        // Verificar status
        const status = await client.getStatus();
        console.log('Status:', status);
        
        // Desconectar
        await client.disconnect();
    }
})();
```

### C# (.NET)

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.IO;

public class CodeNetClient
{
    private readonly HttpClient _httpClient;
    private readonly string _serverUrl;
    private string _apiKey;
    private string _sessionToken;
    
    public CodeNetClient(string serverUrl)
    {
        _serverUrl = serverUrl;
        _httpClient = new HttpClient();
    }
    
    public async Task<bool> RegisterAsync(string appName, string appVersion, 
                                         string platform, string description = "")
    {
        var data = new
        {
            app_name = appName,
            app_version = appVersion,
            platform = platform,
            description = description
        };
        
        var json = JsonSerializer.Serialize(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await _httpClient.PostAsync($"{_serverUrl}/api/register", content);
        
        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadAsStringAsync();
            var jsonDoc = JsonDocument.Parse(result);
            
            _apiKey = jsonDoc.RootElement.GetProperty("data")
                            .GetProperty("api_key").GetString();
            
            // Salvar credenciais
            File.WriteAllText("CodeNet_credentials.json", result);
            
            Console.WriteLine("✅ Registrado com sucesso!");
            return true;
        }
        
        Console.WriteLine($"❌ Erro no registro: {await response.Content.ReadAsStringAsync()}");
        return false;
    }
    
    public async Task<bool> ConnectAsync(string apiKey = null)
    {
        if (apiKey != null)
            _apiKey = apiKey;
        
        if (string.IsNullOrEmpty(_apiKey))
        {
            Console.WriteLine("❌ API Key não fornecida");
            return false;
        }
        
        var data = new { api_key = _apiKey };
        var json = JsonSerializer.Serialize(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await _httpClient.PostAsync($"{_serverUrl}/api/connect", content);
        
        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadAsStringAsync();
            var jsonDoc = JsonDocument.Parse(result);
            
            _sessionToken = jsonDoc.RootElement.GetProperty("data")
                                  .GetProperty("session_token").GetString();
            
            Console.WriteLine("✅ Conectado com sucesso!");
            return true;
        }
        
        Console.WriteLine($"❌ Erro na conexão: {await response.Content.ReadAsStringAsync()}");
        return false;
    }
    
    public async Task<string> GetStatusAsync()
    {
        if (string.IsNullOrEmpty(_sessionToken))
        {
            Console.WriteLine("❌ Não conectado");
            return null;
        }
        
        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_sessionToken}");
        
        var response = await _httpClient.GetAsync($"{_serverUrl}/api/status");
        
        if (response.IsSuccessStatusCode)
        {
            return await response.Content.ReadAsStringAsync();
        }
        
        Console.WriteLine($"❌ Erro: {await response.Content.ReadAsStringAsync()}");
        return null;
    }
    
    public async Task<bool> DisconnectAsync()
    {
        if (string.IsNullOrEmpty(_sessionToken))
        {
            Console.WriteLine("❌ Não conectado");
            return false;
        }
        
        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_sessionToken}");
        
        var response = await _httpClient.PostAsync($"{_serverUrl}/api/disconnect", null);
        
        if (response.IsSuccessStatusCode)
        {
            Console.WriteLine("✅ Desconectado com sucesso!");
            _sessionToken = null;
            return true;
        }
        
        Console.WriteLine($"❌ Erro ao desconectar: {await response.Content.ReadAsStringAsync()}");
        return false;
    }
}

// EXEMPLO DE USO
class Program
{
    static async Task Main(string[] args)
    {
        var client = new CodeNetClient("http://localhost:8000");
        
        // Carregar credenciais
        var credentials = JsonSerializer.Deserialize<JsonDocument>(
            File.ReadAllText("CodeNet_credentials.json")
        );
        
        var apiKey = credentials.RootElement.GetProperty("api_key").GetString();
        
        // Conectar
        if (await client.ConnectAsync(apiKey))
        {
            // Verificar status
            var status = await client.GetStatusAsync();
            Console.WriteLine($"Status: {status}");
            
            // Desconectar
            await client.DisconnectAsync();
        }
    }
}
```

---

## 📡 Endpoints Disponíveis

### Públicos (Sem Autenticação)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do servidor |
| GET | `/api/docs` | Documentação completa |
| GET | `/api/health` | Health check |
| POST | `/api/register` | Registrar nova aplicação |
| POST | `/api/connect` | Conectar aplicação |

### Autenticados (Requer Session Token)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/status` | Status da sessão atual |
| POST | `/api/disconnect` | Desconectar aplicação |
| GET | `/api/apps/list` | Listar apps conectadas |

---

## ✅ Boas Práticas

### 1. Segurança

```python
# ✅ BOM - Usar variáveis de ambiente
import os
api_key = os.getenv('CodeNet_API_KEY')

# ❌ RUIM - Hardcoded no código
api_key = "kgs_1234567890abcdef"
```

### 2. Tratamento de Erros

```python
def connect_safe(client):
    try:
        return client.connect()
    except requests.exceptions.ConnectionError:
        print("❌ Servidor offline")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout na conexão")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
```

### 3. Renovação de Sessão

```python
def ensure_connected(client):
    """Garante que a sessão está ativa"""
    status = client.get_status()
    
    if not status:
        # Sessão expirada, reconectar
        print("🔄 Reconectando...")
        client.connect()
```

### 4. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usar nos eventos importantes
logger.info("Conectado ao CodeNet Server")
logger.error("Falha na autenticação")
```

---

## 🔧 Troubleshooting

### Erro: "API key inválida"

**Causa:** API key incorreta ou não existe

**Solução:**
1. Verifique se a API key está correta
2. Registre uma nova aplicação se necessário
3. Verifique se não há espaços extras na key

### Erro: "Sessão expirada"

**Causa:** Session token expirou (>24h)

**Solução:**
```python
# Reconectar com a API key
client.connect(api_key)
```

### Erro: "Conexão recusada"

**Causa:** Servidor offline ou URL incorreta

**Solução:**
1. Verifique se o servidor está rodando
2. Confirme a URL do servidor
3. Verifique firewall/proxy

### Erro: "Autenticação necessária"

**Causa:** Requisição sem Authorization header

**Solução:**
```python
# Adicionar header em todas as requisições autenticadas
headers = {"Authorization": f"Bearer {session_token}"}
```

---

## 📞 Suporte

- **Documentação:** `/api/docs` no servidor
- **Logs:** `logs/CodeNet_server.log`
- **Health Check:** `/api/health`

---

## 🔄 Changelog

### v3.0.0 (2025-11-21)
- ✨ Sistema de autenticação com API Keys
- ✨ Session tokens com expiração de 24h
- ✨ Endpoints autenticados
- ✨ Gerenciamento de apps conectadas
- ✨ Sistema de logging completo
- 📚 Documentação completa

---

## 📄 Licença

MIT License - CodeNet Inc © 2025

