"""
🔧 Cliente Python para CodeNet Server v3.0
Classe pronta para usar em suas aplicações
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CodeNetClient:
    """Cliente para conectar ao CodeNet Server"""
    
    def __init__(self, server_url: str, credentials_file: str = "CodeNet_credentials.json"):
        """
        Inicializa o cliente
        
        Args:
            server_url: URL do servidor (ex: http://localhost:8000)
            credentials_file: Arquivo para salvar credenciais
        """
        self.server_url = server_url.rstrip('/')
        self.credentials_file = credentials_file
        self.api_key = None
        self.session_token = None
        self.app_id = None
        
        # Tentar carregar credenciais existentes
        self._load_credentials()
        
        logger.info(f"Cliente inicializado para {server_url}")
    
    def _load_credentials(self):
        """Carrega credenciais do arquivo"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    creds = json.load(f)
                    self.api_key = creds.get('api_key')
                    self.app_id = creds.get('app_id')
                    logger.info("Credenciais carregadas do arquivo")
            except Exception as e:
                logger.warning(f"Erro ao carregar credenciais: {e}")
    
    def _save_credentials(self, api_key: str, secret: str, app_id: str):
        """Salva credenciais no arquivo"""
        try:
            creds = {
                'api_key': api_key,
                'secret': secret,
                'app_id': app_id,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(creds, f, indent=2)
            
            logger.info(f"Credenciais salvas em {self.credentials_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar credenciais: {e}")
    
    def register(self, app_name: str, app_version: str, platform: str, 
                 description: str = "") -> bool:
        """
        Registra a aplicação no servidor
        
        Args:
            app_name: Nome da aplicação
            app_version: Versão da aplicação
            platform: Plataforma (Windows, Linux, etc)
            description: Descrição opcional
            
        Returns:
            True se registrado com sucesso
        """
        try:
            url = f"{self.server_url}/api/register"
            
            data = {
                "app_name": app_name,
                "app_version": app_version,
                "platform": platform,
                "description": description
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 201:
                result = response.json()['data']
                
                self.api_key = result['api_key']
                self.app_id = result['app_id']
                
                # Salvar credenciais
                self._save_credentials(
                    result['api_key'],
                    result['secret'],
                    result['app_id']
                )
                
                logger.info(f"✅ Aplicação registrada: {app_name}")
                return True
            else:
                logger.error(f"Erro no registro: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção no registro: {e}")
            return False
    
    def connect(self, api_key: Optional[str] = None) -> bool:
        """
        Conecta ao servidor
        
        Args:
            api_key: API key (usa a salva se não fornecida)
            
        Returns:
            True se conectado com sucesso
        """
        if api_key:
            self.api_key = api_key
        
        if not self.api_key:
            logger.error("API key não disponível. Registre a aplicação primeiro.")
            return False
        
        try:
            url = f"{self.server_url}/api/connect"
            data = {"api_key": self.api_key}
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()['data']
                self.session_token = result['session_token']
                
                logger.info("✅ Conectado com sucesso")
                return True
            else:
                logger.error(f"Erro na conexão: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção na conexão: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Desconecta do servidor
        
        Returns:
            True se desconectado com sucesso
        """
        if not self.session_token:
            logger.warning("Não conectado")
            return False
        
        try:
            url = f"{self.server_url}/api/disconnect"
            headers = {"Authorization": f"Bearer {self.session_token}"}
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Desconectado")
                self.session_token = None
                return True
            else:
                logger.error(f"Erro ao desconectar: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao desconectar: {e}")
            return False
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Obtém status da sessão
        
        Returns:
            Dados de status ou None em caso de erro
        """
        if not self.session_token:
            logger.error("Não conectado")
            return None
        
        try:
            url = f"{self.server_url}/api/status"
            headers = {"Authorization": f"Bearer {self.session_token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter status: {response.json()}")
                return None
                
        except Exception as e:
            logger.error(f"Exceção ao obter status: {e}")
            return None
    
    def is_connected(self) -> bool:
        """
        Verifica se está conectado
        
        Returns:
            True se conectado e sessão válida
        """
        status = self.get_status()
        return status is not None
    
    def ensure_connected(self) -> bool:
        """
        Garante que está conectado (reconecta se necessário)
        
        Returns:
            True se conectado
        """
        if self.is_connected():
            return True
        
        logger.info("🔄 Reconectando...")
        return self.connect()
    
    def request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """
        Faz uma requisição autenticada
        
        Args:
            method: GET, POST, etc
            endpoint: Endpoint da API (ex: /api/custom)
            **kwargs: Argumentos para requests
            
        Returns:
            Response object ou None em caso de erro
        """
        if not self.ensure_connected():
            logger.error("Não foi possível estabelecer conexão")
            return None
        
        try:
            url = f"{self.server_url}{endpoint}"
            headers = kwargs.get('headers', {})
            headers["Authorization"] = f"Bearer {self.session_token}"
            kwargs['headers'] = headers
            
            response = requests.request(method, url, timeout=10, **kwargs)
            return response
            
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            return None


# ============ EXEMPLO DE USO ============

def exemplo_uso_completo():
    """Demonstra uso completo do cliente"""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Criar cliente
    client = CodeNetClient("http://localhost:8000")
    
    # SE É A PRIMEIRA VEZ - REGISTRAR
    # client.register(
    #     app_name="Minha Aplicação",
    #     app_version="1.0.0",
    #     platform="Windows",
    #     description="Descrição da aplicação"
    # )
    
    # CONECTAR (usa credenciais salvas)
    if client.connect():
        print("✅ Conectado!")
        
        # Verificar status
        status = client.get_status()
        print(f"Status: {status}")
        
        # Fazer requisições customizadas
        # response = client.request('GET', '/api/custom_endpoint')
        
        # Desconectar
        client.disconnect()
    else:
        print("❌ Falha na conexão")


def exemplo_uso_com_env():
    """Exemplo usando variáveis de ambiente"""
    
    # Carregar do .env
    server_url = os.getenv('CodeNet_SERVER_URL', 'http://localhost:8000')
    api_key = os.getenv('CodeNet_API_KEY')
    
    client = CodeNetClient(server_url)
    
    if api_key:
        # Conectar com API key do ambiente
        if client.connect(api_key):
            print("✅ Conectado via .env")
            
            # Sua lógica aqui...
            
            client.disconnect()
    else:
        print("⚠️ Configure CodeNet_API_KEY no .env")


if __name__ == "__main__":
    exemplo_uso_completo()

