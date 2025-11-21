#!/usr/bin/env python3
"""
🔧 KINGSMAN SERVER - ENVIRONMENT VARIABLE MANAGER
Script para configurar automaticamente todas as variáveis de ambiente
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class EnvironmentManager:
    def __init__(self):
        self.env_vars = {}
        self.load_env_template()
        
    def load_env_template(self):
        """Carrega template de variáveis de ambiente"""
        env_example_file = Path('.env.example')
        
        if env_example_file.exists():
            with open(env_example_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove valores placeholder
                        if 'your_' in value.lower() or 'here' in value.lower():
                            value = ''
                        self.env_vars[key] = value
        
        print(f"📋 Loaded {len(self.env_vars)} environment variables from template")
    
    def interactive_setup(self):
        """Configuração interativa das variáveis"""
        print("🔧 Interactive Environment Setup")
        print("================================")
        print("Pressione Enter para manter valor padrão ou digite novo valor")
        print()
        
        # Grupos de configuração
        groups = {
            'SERVER': ['HOST', 'PORT', 'DEBUG', 'LOG_LEVEL'],
            'MONITORING': ['HEALTH_CHECK_INTERVAL', 'BACKUP_INTERVAL', 'WEBHOOK_URL'],
            'SECURITY': ['JWT_SECRET', 'UPTIME_ROBOT_API_KEY'],
            'PERFORMANCE': ['MAX_WORKERS', 'REQUEST_TIMEOUT'],
            'FEATURES': ['ENABLE_METRICS', 'ENABLE_BACKUP', 'ENABLE_AUTO_RESTART']
        }
        
        for group_name, variables in groups.items():
            print(f"\n🔧 {group_name} CONFIGURATION:")
            print("-" * 40)
            
            for var in variables:
                if var in self.env_vars:
                    current_value = self.env_vars[var]
                    display_value = current_value if current_value else "(not set)"
                    
                    if var == 'WEBHOOK_URL':
                        print(f"\n💡 {var}: Configure Discord/Slack webhook for notifications")
                        print("   Discord: Server Settings > Integrations > Webhooks")
                        print("   Slack: App Directory > Incoming Webhooks")
                    elif var == 'JWT_SECRET':
                        print(f"\n💡 {var}: Random secret for security (will generate if empty)")
                    elif var == 'UPTIME_ROBOT_API_KEY':
                        print(f"\n💡 {var}: Get from uptimerobot.com > Settings > API")
                    
                    new_value = input(f"{var} [{display_value}]: ").strip()
                    
                    if new_value:
                        self.env_vars[var] = new_value
                    elif var == 'JWT_SECRET' and not current_value:
                        # Generate random JWT secret
                        import secrets
                        self.env_vars[var] = secrets.token_urlsafe(32)
                        print(f"  Generated random secret: {self.env_vars[var][:8]}...")
    
    def save_env_file(self):
        """Salva arquivo .env"""
        env_file = Path('.env')
        
        with open(env_file, 'w') as f:
            f.write("# 🚀 KINGSMAN SERVER - PRODUCTION ENVIRONMENT\n")
            f.write(f"# Generated automatically on {os.popen('date').read().strip()}\n\n")
            
            # Group variables by category
            groups = {
                'SERVER CONFIG': ['HOST', 'PORT', 'DEBUG', 'PYTHONUNBUFFERED', 'ENVIRONMENT'],
                'LOGGING': ['LOG_LEVEL', 'MAX_LOG_SIZE', 'LOG_RETENTION_DAYS'],
                'MONITORING': ['HEALTH_CHECK_INTERVAL', 'BACKUP_INTERVAL', 'METRICS_COLLECTION'],
                'EXTERNAL SERVICES': ['WEBHOOK_URL', 'UPTIME_ROBOT_API_KEY'],
                'SECURITY': ['JWT_SECRET', 'GITHUB_TOKEN', 'RAILWAY_TOKEN'],
                'PERFORMANCE': ['MAX_WORKERS', 'REQUEST_TIMEOUT', 'MAX_REQUEST_SIZE'],
                'FEATURES': ['ENABLE_METRICS', 'ENABLE_BACKUP', 'ENABLE_AUTO_RESTART'],
                'ALERTS': ['ALERT_ON_HIGH_CPU', 'ALERT_ON_HIGH_MEMORY', 'ALERT_ON_HIGH_ERRORS']
            }
            
            for group_name, variables in groups.items():
                f.write(f"# === {group_name} ===\n")
                for var in variables:
                    if var in self.env_vars:
                        value = self.env_vars[var]
                        f.write(f"{var}={value}\n")
                f.write("\n")
        
        print(f"✅ Environment file saved: {env_file.absolute()}")
    
    def configure_railway(self):
        """Configura variáveis no Railway"""
        print("\n🚂 Configuring Railway Environment...")
        
        try:
            # Check if railway CLI is available
            result = subprocess.run(['railway', '--version'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Railway CLI not found. Install with: npm install -g @railway/cli")
                return False
            
            # Set variables
            success_count = 0
            for var, value in self.env_vars.items():
                if value and not value.startswith('your_'):
                    try:
                        result = subprocess.run(['railway', 'vars', 'set', f'{var}={value}'],
                                             capture_output=True, text=True)
                        if result.returncode == 0:
                            success_count += 1
                            print(f"  ✅ {var}")
                        else:
                            print(f"  ❌ {var}: {result.stderr.strip()}")
                    except Exception as e:
                        print(f"  ❌ {var}: {e}")
            
            print(f"✅ Successfully configured {success_count} variables in Railway")
            return True
            
        except Exception as e:
            print(f"❌ Error configuring Railway: {e}")
            return False
    
    def configure_render(self):
        """Instrução para configurar variáveis no Render"""
        print("\n🎨 Render Configuration Instructions:")
        print("=====================================")
        print("1. Go to your Render dashboard: https://dashboard.render.com/")
        print("2. Select your service")
        print("3. Go to 'Environment' tab")
        print("4. Add these variables:")
        print()
        
        for var, value in self.env_vars.items():
            if value and not value.startswith('your_'):
                # Hide sensitive values
                display_value = value
                if any(secret in var.lower() for secret in ['secret', 'key', 'token', 'password']):
                    display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"   {var} = {display_value}")
        
        print("\n💡 Copy these values to Render Environment Variables")
    
    def generate_github_secrets(self):
        """Gera comandos para configurar GitHub Secrets"""
        print("\n🐙 GitHub Secrets Configuration:")
        print("=================================")
        
        # Essential secrets for GitHub Actions
        essential_secrets = [
            'RAILWAY_TOKEN', 'WEBHOOK_URL', 'UPTIME_ROBOT_API_KEY',
            'JWT_SECRET', 'GITHUB_TOKEN'
        ]
        
        print("Run these commands in your repository directory:")
        print()
        
        for secret in essential_secrets:
            if secret in self.env_vars and self.env_vars[secret]:
                value = self.env_vars[secret]
                # Use GitHub CLI if available
                print(f'gh secret set {secret} --body "{value}"')
        
        print("\nOr manually add them at:")
        print("https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions")
    
    def create_docker_env(self):
        """Cria arquivo de ambiente para Docker"""
        docker_env = Path('docker.env')
        
        with open(docker_env, 'w') as f:
            f.write("# Docker Environment Variables\n")
            for var, value in self.env_vars.items():
                if value and not value.startswith('your_'):
                    f.write(f"{var}={value}\n")
        
        print(f"✅ Docker environment file: {docker_env.absolute()}")

def main():
    print("🔧 Kingsman Server - Environment Configuration Manager")
    print("======================================================")
    
    if not Path('.env.example').exists():
        print("❌ .env.example file not found!")
        print("Run this script from the server directory")
        sys.exit(1)
    
    manager = EnvironmentManager()
    
    # Interactive setup
    manager.interactive_setup()
    
    # Save .env file
    manager.save_env_file()
    
    # Platform configuration
    print("\n🌐 Platform Configuration:")
    print("===========================")
    
    platform = input("Choose your hosting platform (railway/render/both): ").lower()
    
    if platform in ['railway', 'both']:
        manager.configure_railway()
    
    if platform in ['render', 'both']:
        manager.configure_render()
    
    # GitHub secrets
    if input("\nGenerate GitHub Secrets commands? (y/n): ").lower() == 'y':
        manager.generate_github_secrets()
    
    # Docker environment
    if input("Create Docker environment file? (y/n): ").lower() == 'y':
        manager.create_docker_env()
    
    print("\n🎉 Environment configuration completed!")
    print("\n📋 Next steps:")
    print("1. Review the generated .env file")
    print("2. Configure secrets in your hosting platform")
    print("3. Add GitHub Secrets for CI/CD")
    print("4. Test the deployment")
    print("\n🔒 Security reminder: Never commit .env files to git!")

if __name__ == "__main__":
    main()