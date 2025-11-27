#!/usr/bin/env python3
"""
🔧 CodeNet SERVER - DEPENDENCY INSTALLER & VALIDATOR
Script para verificar e instalar todas as dependências necessárias
"""

import subprocess
import sys
import importlib
import os
from pathlib import Path

class DependencyManager:
    def __init__(self):
        self.required_packages = {
            'flask': 'Flask web framework',
            'flask-cors': 'Flask CORS support',
            'requests': 'HTTP requests library',
            'psutil': 'System monitoring',
            'schedule': 'Task scheduling',
            'gunicorn': 'Production WSGI server (optional)',
            'python-dotenv': 'Environment variables',
            'prometheus-client': 'Metrics collection (optional)'
        }
        
        self.optional_packages = {
            'safety': 'Security vulnerability scanner',
            'bandit': 'Security static analysis',
            'pip-audit': 'Dependency vulnerability scanner',
            'black': 'Code formatter',
            'flake8': 'Code linter'
        }
        
    def check_python_version(self):
        """Verifica versão do Python"""
        version = sys.version_info
        print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ é necessário!")
            return False
        
        print("✅ Python version is compatible")
        return True
        
    def check_pip(self):
        """Verifica se pip está disponível"""
        try:
            import pip
            print("✅ pip is available")
            return True
        except ImportError:
            print("❌ pip not found!")
            return False
            
    def install_package(self, package_name):
        """Instala um pacote específico"""
        try:
            print(f"📦 Installing {package_name}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print(f"✅ {package_name} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package_name}: {e}")
            return False
            
    def check_package(self, package_name):
        """Verifica se um pacote está instalado"""
        try:
            # Para pacotes com hífens, converter para underscore
            import_name = package_name.replace('-', '_')
            if import_name == 'flask_cors':
                import_name = 'flask_cors'
            elif import_name == 'python_dotenv':
                import_name = 'dotenv'
            elif import_name == 'prometheus_client':
                import_name = 'prometheus_client'
                
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
            
    def install_requirements(self):
        """Instala dependências do requirements.txt se existir"""
        req_file = Path('requirements.txt')
        if req_file.exists():
            print("📋 Installing from requirements.txt...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-r", str(req_file)
                ])
                print("✅ Requirements installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install requirements: {e}")
                return False
        else:
            print("ℹ️ No requirements.txt found, installing packages individually")
            return True
            
    def validate_installation(self):
        """Valida se todas as dependências necessárias estão instaladas"""
        print("\n🔍 Validating installation...")
        
        missing_packages = []
        
        for package, description in self.required_packages.items():
            if self.check_package(package):
                print(f"✅ {package} - {description}")
            else:
                print(f"❌ {package} - {description} (MISSING)")
                missing_packages.append(package)
                
        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print("\n✅ All required packages are installed!")
            return True
            
    def test_imports(self):
        """Testa todas as importações necessárias"""
        print("\n🧪 Testing imports...")
        
        imports_to_test = [
            ('flask', 'from flask import Flask, jsonify, request'),
            ('flask_cors', 'from flask_cors import CORS'),
            ('requests', 'import requests'),
            ('psutil', 'import psutil'),
            ('schedule', 'import schedule'),
            ('json', 'import json'),
            ('os', 'import os'),
            ('sys', 'import sys'),
            ('threading', 'import threading'),
            ('datetime', 'from datetime import datetime'),
            ('pathlib', 'from pathlib import Path')
        ]
        
        failed_imports = []
        
        for name, import_statement in imports_to_test:
            try:
                exec(import_statement)
                print(f"✅ {name}")
            except ImportError as e:
                print(f"❌ {name}: {e}")
                failed_imports.append(name)
                
        if failed_imports:
            print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
            return False
        else:
            print("\n✅ All imports successful!")
            return True
            
    def run_full_check(self):
        """Executa verificação completa"""
        print("🔧 CodeNet Server - Dependency Check & Installation")
        print("=" * 60)
        
        # Verificar Python
        if not self.check_python_version():
            return False
            
        # Verificar pip
        if not self.check_pip():
            return False
            
        # Instalar requirements.txt se existir
        self.install_requirements()
        
        # Verificar pacotes necessários
        print(f"\n📦 Checking required packages...")
        missing_required = []
        
        for package in self.required_packages:
            if not self.check_package(package):
                missing_required.append(package)
                
        # Instalar pacotes faltantes
        if missing_required:
            print(f"\n📦 Installing missing packages: {', '.join(missing_required)}")
            for package in missing_required:
                self.install_package(package)
        else:
            print("✅ All required packages already installed")
            
        # Validar instalação
        validation_ok = self.validate_installation()
        
        # Testar importações
        imports_ok = self.test_imports()
        
        # Resultado final
        print("\n" + "=" * 60)
        if validation_ok and imports_ok:
            print("🎉 DEPENDENCY CHECK PASSED!")
            print("✅ All dependencies are properly installed and working")
            print("🚀 Your CodeNet Server is ready to run!")
            return True
        else:
            print("❌ DEPENDENCY CHECK FAILED!")
            print("💡 Please resolve the issues above before running the server")
            return False
            
    def install_development_tools(self):
        """Instala ferramentas de desenvolvimento opcionais"""
        print("\n🛠️ Installing development tools (optional)...")
        
        for package, description in self.optional_packages.items():
            if not self.check_package(package):
                print(f"📦 {description}...")
                self.install_package(package)
            else:
                print(f"✅ {package} already installed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CodeNet Server Dependency Manager')
    parser.add_argument('--dev-tools', action='store_true', 
                       help='Also install development tools')
    parser.add_argument('--force-reinstall', action='store_true',
                       help='Force reinstall all packages')
    
    args = parser.parse_args()
    
    manager = DependencyManager()
    
    # Reinstalar tudo se solicitado
    if args.force_reinstall:
        print("🔄 Force reinstalling all packages...")
        all_packages = list(manager.required_packages.keys())
        for package in all_packages:
            manager.install_package(package)
    
    # Executar verificação completa
    success = manager.run_full_check()
    
    # Instalar ferramentas de desenvolvimento se solicitado
    if args.dev_tools:
        manager.install_development_tools()
    
    # Criar arquivo de status
    status_file = Path('dependency_check.json')
    import json
    from datetime import datetime
    
    status_data = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'required_packages': list(manager.required_packages.keys()),
        'dev_tools_installed': args.dev_tools
    }
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"\n📊 Status saved to: {status_file}")
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run: python CodeNet_server_production.py")
        print("2. Test: python deployment/test_complete_system.py")
        print("3. Deploy: follow DEPLOYMENT_GUIDE.md")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
