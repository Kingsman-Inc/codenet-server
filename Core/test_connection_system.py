"""
🧪 Teste do Sistema de Conexão - CodeNet Server v3.0
Script para testar todas as funcionalidades de conexão
"""

import requests
import json
import time
from datetime import datetime

class TestCodeNetConnection:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.api_key = None
        self.session_token = None
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Registra resultado do teste"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {message}")
    
    def test_server_online(self):
        """Testa se o servidor está online"""
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Servidor Online", True, f"Versão {data['version']}")
                return True
            else:
                self.log_test("Servidor Online", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Servidor Online", False, str(e))
            return False
    
    def test_health_check(self):
        """Testa endpoint de health check"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data['status']}")
                return True
            else:
                self.log_test("Health Check", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_documentation(self):
        """Testa endpoint de documentação"""
        try:
            response = requests.get(f"{self.server_url}/api/docs", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Documentação", True, f"API v{data['api_version']}")
                return True
            else:
                self.log_test("Documentação", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Documentação", False, str(e))
            return False
    
    def test_register_app(self):
        """Testa registro de aplicação"""
        try:
            data = {
                "app_name": "Test App",
                "app_version": "1.0.0",
                "platform": "Test Platform",
                "description": "Aplicação de teste automático"
            }
            
            response = requests.post(
                f"{self.server_url}/api/register",
                json=data,
                timeout=5
            )
            
            if response.status_code == 201:
                result = response.json()
                self.api_key = result['data']['api_key']
                
                # Salvar credenciais de teste
                with open('test_credentials.json', 'w') as f:
                    json.dump(result['data'], f, indent=2)
                
                self.log_test("Registro de App", True, f"API Key recebida")
                return True
            else:
                self.log_test("Registro de App", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Registro de App", False, str(e))
            return False
    
    def test_connect(self):
        """Testa conexão com API key"""
        if not self.api_key:
            self.log_test("Conexão", False, "API Key não disponível")
            return False
        
        try:
            data = {"api_key": self.api_key}
            
            response = requests.post(
                f"{self.server_url}/api/connect",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.session_token = result['data']['session_token']
                self.log_test("Conexão", True, "Session token recebido")
                return True
            else:
                self.log_test("Conexão", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Conexão", False, str(e))
            return False
    
    def test_session_status(self):
        """Testa verificação de status da sessão"""
        if not self.session_token:
            self.log_test("Status da Sessão", False, "Session token não disponível")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            
            response = requests.get(
                f"{self.server_url}/api/status",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                app_name = result['session']['app_name']
                self.log_test("Status da Sessão", True, f"App: {app_name}")
                return True
            else:
                self.log_test("Status da Sessão", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Status da Sessão", False, str(e))
            return False
    
    def test_list_apps(self):
        """Testa listagem de apps"""
        if not self.session_token:
            self.log_test("Listar Apps", False, "Session token não disponível")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            
            response = requests.get(
                f"{self.server_url}/api/apps/list",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                total = result['data']['total']
                self.log_test("Listar Apps", True, f"Total: {total} apps")
                return True
            else:
                self.log_test("Listar Apps", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Listar Apps", False, str(e))
            return False
    
    def test_disconnect(self):
        """Testa desconexão"""
        if not self.session_token:
            self.log_test("Desconexão", False, "Session token não disponível")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            
            response = requests.post(
                f"{self.server_url}/api/disconnect",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.log_test("Desconexão", True, "Desconectado com sucesso")
                self.session_token = None
                return True
            else:
                self.log_test("Desconexão", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Desconexão", False, str(e))
            return False
    
    def test_invalid_auth(self):
        """Testa requisição com autenticação inválida"""
        try:
            headers = {"Authorization": "Bearer token_invalido"}
            
            response = requests.get(
                f"{self.server_url}/api/status",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 401:
                self.log_test("Auth Inválida", True, "Erro 401 esperado")
                return True
            else:
                self.log_test("Auth Inválida", False, f"Status inesperado: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Inválida", False, str(e))
            return False
    
    def test_missing_auth(self):
        """Testa requisição sem autenticação"""
        try:
            response = requests.get(
                f"{self.server_url}/api/status",
                timeout=5
            )
            
            if response.status_code == 401:
                self.log_test("Auth Ausente", True, "Erro 401 esperado")
                return True
            else:
                self.log_test("Auth Ausente", False, f"Status inesperado: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Ausente", False, str(e))
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 60)
        print("🧪 INICIANDO TESTES - CodeNet Server v3.0")
        print("=" * 60)
        print()
        
        tests = [
            ("1. Servidor Online", self.test_server_online),
            ("2. Health Check", self.test_health_check),
            ("3. Documentação", self.test_documentation),
            ("4. Registro de App", self.test_register_app),
            ("5. Conexão", self.test_connect),
            ("6. Status da Sessão", self.test_session_status),
            ("7. Listar Apps", self.test_list_apps),
            ("8. Auth Inválida", self.test_invalid_auth),
            ("9. Auth Ausente", self.test_missing_auth),
            ("10. Desconexão", self.test_disconnect),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔄 Executando: {test_name}")
            test_func()
            time.sleep(0.5)  # Pequena pausa entre testes
        
        # Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"\nTotal de testes: {total}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"📈 Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        # Salvar resultados
        with open('test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": f"{(passed/total)*100:.1f}%"
                },
                "tests": self.test_results
            }, f, indent=2)
        
        print("\n💾 Resultados salvos em: test_results.json")
        
        if failed == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n⚠️  {failed} teste(s) falharam. Verifique os detalhes acima.")
        
        print("=" * 60)


def main():
    """Função principal"""
    import sys
    
    server_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print(f"🎯 URL do servidor: {server_url}\n")
    
    tester = TestCodeNetConnection(server_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()

