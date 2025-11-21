#!/usr/bin/env python3
"""
🧪 KINGSMAN MENU v1.4 - TESTE DE LANÇAMENTO
============================================
Verifica se tudo está pronto para o lançamento da v1.4
"""

import json
import requests
import time
import sys
from pathlib import Path
from datetime import datetime

class ReleaseValidator:
    def __init__(self):
        self.server_url = "http://localhost:8080"
        self.server_dir = Path(__file__).parent
        self.all_checks_passed = True
        
        print("🧪 KINGSMAN MENU v1.4 - VALIDADOR DE LANÇAMENTO")
        print("=" * 60)
        print(f"🌐 Servidor: {self.server_url}")
        print(f"📁 Diretório: {self.server_dir}")
        print(f"⏰ Teste iniciado: {datetime.now().strftime('%H:%M:%S')}")
        print()

    def check_server_running(self):
        """Verifica se o servidor está rodando"""
        print("🌐 VERIFICANDO SERVIDOR...")
        
        try:
            response = requests.get(f"{self.server_url}/version.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                patch = data.get("patch_version", "unknown")
                print(f"✅ Servidor respondendo - v{version} (patch {patch})")
                return True
            else:
                print(f"❌ Servidor retornou código {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Servidor não está rodando ou não acessível")
            print("💡 Execute: python launch_v1.4_server.py")
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    def test_endpoints(self):
        """Testa todos os endpoints críticos"""
        print("\n📡 TESTANDO ENDPOINTS...")
        
        endpoints = [
            ("version.json", "Informações de versão"),
            ("patches.json", "Lista de patches"),
            ("1.4.json", "Detalhes da release 1.4"),
            ("update_manifest.json", "Manifesto de update"),
            ("notification_v1.4.json", "Notificação para usuários")
        ]
        
        all_passed = True
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.server_url}/{endpoint}", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint} - {description}")
                else:
                    print(f"❌ {endpoint} - Código {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"❌ {endpoint} - Erro: {e}")
                all_passed = False
        
        return all_passed

    def validate_version_data(self):
        """Valida os dados de versão"""
        print("\n📊 VALIDANDO DADOS DE VERSÃO...")
        
        try:
            response = requests.get(f"{self.server_url}/version.json")
            data = response.json()
            
            # Verificações críticas
            checks = [
                (data.get("version") == "1.4", "Versão principal é 1.4"),
                (data.get("patch_version") == "1.4.1", "Patch é 1.4.1"),
                ("last_updated" in data, "Timestamp de update presente"),
                ("server_info" in data, "Informações do servidor presentes")
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False

    def check_download_structure(self):
        """Verifica estrutura de downloads"""
        print("\n📁 VERIFICANDO ESTRUTURA DE DOWNLOADS...")
        
        downloads_dir = self.server_dir / "downloads"
        required_dirs = ["complete", "patch", "updater"]
        
        all_exists = True
        for dir_name in required_dirs:
            dir_path = downloads_dir / dir_name
            if dir_path.exists():
                # Verificar se há arquivos .exe
                exe_files = list(dir_path.glob("*.exe"))
                if exe_files:
                    print(f"✅ {dir_name}/ - {len(exe_files)} executável(is)")
                else:
                    print(f"⚠️ {dir_name}/ - Sem executáveis (.exe)")
            else:
                print(f"❌ {dir_name}/ - Diretório não existe")
                all_exists = False
        
        return all_exists

    def test_notification_system(self):
        """Testa sistema de notificação"""
        print("\n🔔 TESTANDO SISTEMA DE NOTIFICAÇÃO...")
        
        try:
            response = requests.get(f"{self.server_url}/notification_v1.4.json")
            data = response.json()
            
            notification = data.get("notification", {})
            checks = [
                (notification.get("version") == "1.4", "Versão na notificação correta"),
                (notification.get("title", "").startswith("🚀"), "Título da notificação presente"),
                ("actions" in notification, "Ações de notificação definidas"),
                ("primary" in notification.get("actions", {}), "Ação primária presente")
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Erro no teste de notificação: {e}")
            return False

    def performance_test(self):
        """Teste básico de performance"""
        print("\n⚡ TESTE DE PERFORMANCE...")
        
        start_time = time.time()
        try:
            # Fazer 5 requisições rápidas
            for i in range(5):
                response = requests.get(f"{self.server_url}/version.json", timeout=2)
                if response.status_code != 200:
                    print(f"❌ Falha na requisição {i+1}")
                    return False
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 5
            
            if avg_time < 0.5:
                print(f"✅ Performance boa - {avg_time:.3f}s média por requisição")
                return True
            else:
                print(f"⚠️ Performance lenta - {avg_time:.3f}s média por requisição")
                return True  # Não crítico
                
        except Exception as e:
            print(f"❌ Erro no teste de performance: {e}")
            return False

    def final_readiness_check(self):
        """Verificação final de prontidão"""
        print("\n🎯 VERIFICAÇÃO FINAL DE PRONTIDÃO...")
        
        # Simular uma requisição real de cliente
        try:
            # 1. Cliente verifica versão
            version_response = requests.get(f"{self.server_url}/version.json")
            version_data = version_response.json()
            
            # 2. Cliente pega informações da release
            release_response = requests.get(f"{self.server_url}/1.4.json")
            release_data = release_response.json()
            
            # 3. Cliente pega notificação
            notif_response = requests.get(f"{self.server_url}/notification_v1.4.json")
            notif_data = notif_response.json()
            
            # Verificar fluxo completo
            current_version = version_data.get("version")
            release_version = release_data.get("version")
            notif_version = notif_data.get("notification", {}).get("version")
            
            if current_version == release_version == notif_version == "1.4":
                print("✅ Fluxo completo de cliente validado")
                print("✅ Todas as versões consistentes")
                return True
            else:
                print("❌ Inconsistência nas versões entre arquivos")
                return False
                
        except Exception as e:
            print(f"❌ Erro na verificação final: {e}")
            return False

    def run_validation(self):
        """Executa toda a validação"""
        tests = [
            ("Servidor", self.check_server_running),
            ("Endpoints", self.test_endpoints),
            ("Dados de Versão", self.validate_version_data),
            ("Downloads", self.check_download_structure),
            ("Notificações", self.test_notification_system),
            ("Performance", self.performance_test),
            ("Prontidão Final", self.final_readiness_check)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n🧪 Executando: {test_name}")
            result = test_func()
            results[test_name] = result
            if not result:
                self.all_checks_passed = False
        
        # Resumo final
        print("\n" + "="*60)
        print("📋 RESUMO DA VALIDAÇÃO")
        print("="*60)
        
        for test_name, passed in results.items():
            status = "✅ PASSOU" if passed else "❌ FALHOU"
            print(f"  {test_name}: {status}")
        
        print()
        if self.all_checks_passed:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("🚀 KINGSMAN MENU v1.4 PRONTO PARA LANÇAMENTO!")
            print()
            print("📋 PRÓXIMOS PASSOS:")
            print("  1. Colocar executáveis nas pastas de download")
            print("  2. Manter servidor rodando")
            print("  3. Anunciar nova versão para usuários")
            return True
        else:
            print("❌ ALGUNS TESTES FALHARAM!")
            print("🔧 Corrija os problemas antes do lançamento")
            return False

if __name__ == "__main__":
    validator = ReleaseValidator()
    success = validator.run_validation()
    
    input("\nPressione Enter para finalizar...")
    sys.exit(0 if success else 1)