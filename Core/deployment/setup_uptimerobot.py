#!/usr/bin/env python3
"""
🔍 KINGSMAN SERVER - UPTIMEROBOT SETUP
Script para configurar monitoramento externo gratuito com UptimeRobot
"""

import requests
import json
import os
from datetime import datetime

class UptimeRobotSetup:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.uptimerobot.com/v2"
        
    def create_monitor(self, server_url, monitor_name="Kingsman Server"):
        """Cria um novo monitor no UptimeRobot"""
        
        payload = {
            'api_key': self.api_key,
            'format': 'json',
            'type': 1,  # HTTP(s)
            'url': f"{server_url}/health",
            'friendly_name': monitor_name,
            'interval': 300,  # 5 minutos (plano gratuito)
            'keyword_type': 2,  # Not exists
            'keyword_value': 'error',
            'alert_contacts': '',  # Será configurado depois
            'custom_http_headers': json.dumps({
                'User-Agent': 'UptimeRobot-Kingsman-Monitor'
            })
        }
        
        response = requests.post(f"{self.base_url}/newMonitor", data=payload)
        return response.json()
    
    def setup_notification_channels(self):
        """Configura canais de notificação"""
        print("🔔 Para configurar notificações:")
        print("1. Acesse: https://uptimerobot.com/dashboard")
        print("2. Vá em 'Alert Contacts'")
        print("3. Adicione seus contatos (email, webhook, etc.)")
        print("4. Associe aos monitores criados")
        
    def get_monitors(self):
        """Lista todos os monitores"""
        payload = {
            'api_key': self.api_key,
            'format': 'json'
        }
        
        response = requests.post(f"{self.base_url}/getMonitors", data=payload)
        return response.json()

def main():
    print("🔍 Kingsman Server - UptimeRobot Setup")
    print("=====================================")
    
    # Instruções para obter API key
    print("\n📝 Para usar este script:")
    print("1. Crie conta gratuita em: https://uptimerobot.com/")
    print("2. Vá em 'My Settings' -> 'API Settings'")
    print("3. Crie uma 'Main API Key'")
    print("4. Cole a API key quando solicitado")
    
    api_key = input("\n🔑 Cole sua UptimeRobot API Key: ").strip()
    if not api_key:
        print("❌ API Key é obrigatória!")
        return
    
    server_url = input("🌐 URL do seu servidor (ex: https://kingsman-server.railway.app): ").strip()
    if not server_url:
        print("❌ URL do servidor é obrigatória!")
        return
    
    # Configurar UptimeRobot
    uptime = UptimeRobotSetup(api_key)
    
    print(f"\n🔍 Criando monitor para: {server_url}")
    
    try:
        # Criar monitor principal
        result = uptime.create_monitor(server_url, "Kingsman Server - Main")
        
        if result.get('stat') == 'ok':
            print("✅ Monitor criado com sucesso!")
            monitor_id = result['monitor']['id']
            print(f"📊 Monitor ID: {monitor_id}")
            
            # Salvar configurações
            config = {
                'api_key': api_key,
                'server_url': server_url,
                'monitor_id': monitor_id,
                'created_at': datetime.now().isoformat()
            }
            
            with open('uptimerobot_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("💾 Configurações salvas em: uptimerobot_config.json")
            
        else:
            print(f"❌ Erro ao criar monitor: {result}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Configurar notificações
    uptime.setup_notification_channels()
    
    print(f"\n🎯 Próximos passos:")
    print(f"1. Acesse: https://uptimerobot.com/dashboard")
    print(f"2. Configure contatos de alerta")
    print(f"3. Teste as notificações")
    print(f"4. Configure webhook para GitHub Actions (opcional)")

if __name__ == "__main__":
    main()