#!/usr/bin/env python3
"""
🚀 CodeNet Server v3.0.0 - App Connection Manager
Sistema moderno de gerenciamento de conexões de aplicativos
"""

import os
import sys
import json
import uuid
import time
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/CodeNet_server.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AppConnectionManager:
    """Gerenciador de conexões de aplicativos"""
    
    def __init__(self):
        self.apps_file = "config/connected_apps.json"
        self.api_keys_file = "config/api_keys.json"
        self.sessions_file = "config/active_sessions.json"
        
        # Garantir que as pastas existem
        os.makedirs("config", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        self.connected_apps = self._load_apps()
        self.api_keys = self._load_api_keys()
        self.active_sessions = self._load_sessions()
        
    def _load_apps(self):
        """Carrega apps conectadas"""
        if os.path.exists(self.apps_file):
            try:
                with open(self.apps_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar apps: {e}")
        return {}
    
    def _save_apps(self):
        """Salva apps conectadas"""
        try:
            with open(self.apps_file, 'w', encoding='utf-8') as f:
                json.dump(self.connected_apps, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar apps: {e}")
    
    def _load_api_keys(self):
        """Carrega chaves API"""
        if os.path.exists(self.api_keys_file):
            try:
                with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar API keys: {e}")
        return {}
    
    def _save_api_keys(self):
        """Salva chaves API"""
        try:
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_keys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar API keys: {e}")
    
    def _load_sessions(self):
        """Carrega sessões ativas"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar sessões: {e}")
        return {}
    
    def _save_sessions(self):
        """Salva sessões ativas"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar sessões: {e}")
    
    def generate_api_key(self, app_name):
        """Gera uma nova API key"""
        api_key = f"kgs_{uuid.uuid4().hex}"
        secret = uuid.uuid4().hex
        
        self.api_keys[api_key] = {
            "app_name": app_name,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "requests_count": 0,
            "active": True
        }
        
        self._save_api_keys()
        return api_key, secret
    
    def validate_api_key(self, api_key):
        """Valida uma API key"""
        if api_key not in self.api_keys:
            return False, "API key inválida"
        
        key_data = self.api_keys[api_key]
        
        if not key_data.get("active", False):
            return False, "API key desativada"
        
        # Atualizar último uso e contador
        key_data["last_used"] = datetime.now().isoformat()
        key_data["requests_count"] = key_data.get("requests_count", 0) + 1
        self._save_api_keys()
        
        return True, key_data["app_name"]
    
    def register_app(self, app_name, app_version, platform, description=""):
        """Registra uma nova aplicação"""
        app_id = f"app_{uuid.uuid4().hex[:12]}"
        api_key, secret = self.generate_api_key(app_name)
        
        self.connected_apps[app_id] = {
            "app_id": app_id,
            "name": app_name,
            "version": app_version,
            "platform": platform,
            "description": description,
            "api_key": api_key,
            "registered_at": datetime.now().isoformat(),
            "last_connection": None,
            "status": "registered",
            "connection_count": 0,
            "endpoints_used": []
        }
        
        self._save_apps()
        
        logger.info(f"✅ App registrada: {app_name} (ID: {app_id})")
        
        return {
            "app_id": app_id,
            "api_key": api_key,
            "secret": secret,
            "message": "Aplicação registrada com sucesso"
        }
    
    def connect_app(self, api_key):
        """Conecta uma aplicação"""
        valid, result = self.validate_api_key(api_key)
        
        if not valid:
            return False, result
        
        app_name = result
        session_token = f"sess_{uuid.uuid4().hex}"
        
        # Encontrar app pelo nome
        app_id = None
        for aid, app_data in self.connected_apps.items():
            if app_data["api_key"] == api_key:
                app_id = aid
                app_data["last_connection"] = datetime.now().isoformat()
                app_data["status"] = "connected"
                app_data["connection_count"] = app_data.get("connection_count", 0) + 1
                break
        
        if not app_id:
            return False, "Aplicação não encontrada"
        
        # Criar sessão
        self.active_sessions[session_token] = {
            "app_id": app_id,
            "app_name": app_name,
            "connected_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "requests": 0
        }
        
        self._save_apps()
        self._save_sessions()
        
        logger.info(f"🔗 App conectada: {app_name}")
        
        return True, {
            "session_token": session_token,
            "app_name": app_name,
            "expires_in": "24 hours",
            "message": "Conexão estabelecida"
        }
    
    def disconnect_app(self, session_token):
        """Desconecta uma aplicação"""
        if session_token not in self.active_sessions:
            return False, "Sessão não encontrada"
        
        session = self.active_sessions.pop(session_token)
        app_id = session["app_id"]
        
        if app_id in self.connected_apps:
            self.connected_apps[app_id]["status"] = "disconnected"
            self._save_apps()
        
        self._save_sessions()
        
        logger.info(f"🔌 App desconectada: {session['app_name']}")
        
        return True, "Desconectado com sucesso"
    
    def get_connected_apps(self):
        """Lista apps conectadas"""
        return {
            "total": len(self.connected_apps),
            "active_sessions": len(self.active_sessions),
            "apps": list(self.connected_apps.values())
        }
    
    def validate_session(self, session_token):
        """Valida uma sessão"""
        if session_token not in self.active_sessions:
            return False, "Sessão inválida"
        
        session = self.active_sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            self.active_sessions.pop(session_token)
            self._save_sessions()
            return False, "Sessão expirada"
        
        session["requests"] += 1
        self._save_sessions()
        
        return True, session


class CodeNetServerV3:
    """Servidor CodeNet v3.0.0"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.version = "3.0.0"
        self.start_time = datetime.now()
        self.request_count = 0
        
        # Inicializar gerenciador de conexões
        self.connection_manager = AppConnectionManager()
        
        # Cache para otimização
        self._cache = {}
        self._cache_timeout = 60  # 60 segundos
        
        # Configurar rotas
        self.setup_routes()
        
        logger.info(f"🚀 CodeNet Server v{self.version} iniciado")
    
    def require_auth(self, f):
        """Decorator para autenticação"""
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    "error": "Autenticação necessária",
                    "message": "Forneça um token válido no header Authorization"
                }), 401
            
            session_token = auth_header.replace('Bearer ', '')
            valid, result = self.connection_manager.validate_session(session_token)
            
            if not valid:
                return jsonify({
                    "error": "Sessão inválida",
                    "message": result
                }), 401
            
            # Adicionar informações da sessão ao request
            request.session_data = result
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    def setup_routes(self):
        """Configura todas as rotas"""
        
        # ========== ROTAS PÚBLICAS ==========
        
        @self.app.route('/')
        def home():
            """Página inicial"""
            return jsonify({
                "name": "CodeNet Server",
                "version": self.version,
                "status": "online",
                "message": "🏛️ CodeNet App Connection Manager",
                "timestamp": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.start_time),
                "documentation": "/api/docs"
            })
        
        @self.app.route('/api/docs')
        def documentation():
            """Documentação da API"""
            return jsonify({
                "api_version": self.version,
                "endpoints": {
                    "public": {
                        "/": "Informações do servidor",
                        "/api/docs": "Documentação",
                        "/api/health": "Health check",
                        "/api/register": "Registrar nova app (POST)",
                        "/api/connect": "Conectar app (POST)"
                    },
                    "authenticated": {
                        "/api/status": "Status da sessão",
                        "/api/disconnect": "Desconectar (POST)",
                        "/api/apps/list": "Listar apps conectadas"
                    }
                },
                "authentication": {
                    "method": "Bearer Token",
                    "header": "Authorization: Bearer <session_token>",
                    "expiration": "24 hours"
                },
                "guide_url": "README_CONNECTION_GUIDE.md"
            })
        
        @self.app.route('/api/health')
        def health_check():
            """Health check"""
            self.request_count += 1
            
            return jsonify({
                "status": "healthy",
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
                "connected_apps": len(self.connection_manager.active_sessions)
            })
        
        @self.app.route('/api/register', methods=['POST'])
        def register_app():
            """Registra uma nova aplicação"""
            try:
                data = request.get_json()
                
                required_fields = ['app_name', 'app_version', 'platform']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "error": f"Campo obrigatório: {field}"
                        }), 400
                
                result = self.connection_manager.register_app(
                    app_name=data['app_name'],
                    app_version=data['app_version'],
                    platform=data['platform'],
                    description=data.get('description', '')
                )
                
                return jsonify({
                    "success": True,
                    "data": result,
                    "message": "⚠️ IMPORTANTE: Salve o API Key e Secret em local seguro!"
                }), 201
                
            except Exception as e:
                logger.error(f"Erro no registro: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/connect', methods=['POST'])
        def connect_app():
            """Conecta uma aplicação"""
            try:
                data = request.get_json()
                
                if 'api_key' not in data:
                    return jsonify({
                        "error": "API key obrigatória"
                    }), 400
                
                success, result = self.connection_manager.connect_app(data['api_key'])
                
                if not success:
                    return jsonify({
                        "error": result
                    }), 401
                
                return jsonify({
                    "success": True,
                    "data": result
                })
                
            except Exception as e:
                logger.error(f"Erro na conexão: {e}")
                return jsonify({"error": str(e)}), 500
        
        # ========== ROTAS AUTENTICADAS ==========
        
        @self.app.route('/api/status')
        @self.require_auth
        def session_status(self=self):
            """Status da sessão atual"""
            session = request.session_data
            
            return jsonify({
                "session": {
                    "app_name": session["app_name"],
                    "connected_at": session["connected_at"],
                    "expires_at": session["expires_at"],
                    "requests": session["requests"]
                },
                "server": {
                    "version": self.version,
                    "uptime": str(datetime.now() - self.start_time)
                }
            })
        
        @self.app.route('/api/disconnect', methods=['POST'])
        @self.require_auth
        def disconnect_app(self=self):
            """Desconecta a aplicação atual"""
            auth_header = request.headers.get('Authorization')
            session_token = auth_header.replace('Bearer ', '')
            
            success, message = self.connection_manager.disconnect_app(session_token)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": message
                })
            else:
                return jsonify({
                    "error": message
                }), 400
        
        @self.app.route('/api/apps/list')
        @self.require_auth
        def list_apps(self=self):
            """Lista apps conectadas"""
            apps = self.connection_manager.get_connected_apps()
            
            return jsonify({
                "success": True,
                "data": apps
            })
        
        # ========== ERROR HANDLERS ==========
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "error": "Endpoint não encontrado",
                "documentation": "/api/docs"
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Erro interno: {error}")
            return jsonify({
                "error": "Erro interno do servidor"
            }), 500
    
    def run_server(self, host='0.0.0.0', port=8000):
        """Executa o servidor"""
        try:
            logger.info(f"🌐 Servidor rodando em http://{host}:{port}")
            self.app.run(host=host, port=port, threaded=True)
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            raise


def main():
    """Função principal"""
    print("=" * 60)
    print("🏛️  CodeNet SERVER v3.0.0 - App Connection Manager")
    print("=" * 60)
    
    try:
        server = CodeNetServerV3()
        port = int(os.environ.get('PORT', 8000))
        
        print(f"\n✅ Servidor configurado")
        print(f"🌐 Rodando em: http://0.0.0.0:{port}")
        print(f"📚 Documentação: http://localhost:{port}/api/docs")
        print(f"\n⌨️  Pressione Ctrl+C para parar\n")
        
        server.run_server(host='0.0.0.0', port=port)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor parado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

