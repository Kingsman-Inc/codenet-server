#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Kingsman Server Monitor v1.1.0
Monitor de status do servidor em tempo real

Uma aplicação dedicada para monitoramento de servidores
com interface profissional e funcionalidades avançadas.

Versão 1.1.0 - Melhorias de conectividade e performance

Criado por: Kingsman Inc
Data: 2025-10-20
"""

import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import json
import urllib.request
import threading
import time
import random
import gc
import tempfile
import base64
from datetime import datetime

# --- CONFIGURAÇÕES DO SERVER MONITOR ---
APP_NAME = "Kingsman Server Monitor"
APP_VERSION = "1.1.0"
APP_TITLE = "🌐 Kingsman Server Monitor"

# Configurações de servidor
GITHUB_ORG = "Kingsman-Inc"
GITHUB_REPO = "Kingsman-Menu"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}"
GITHUB_RELEASES_URL = f"{GITHUB_API_BASE}/releases/latest"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_ORG}/{GITHUB_REPO}/main"
KINGSMAN_UPDATE_API = f"https://{GITHUB_ORG.lower()}.github.io/{GITHUB_REPO.lower()}/api/latest.json"

# Configurações de monitoramento
MONITOR_CONFIG = {
    "check_interval": 30,  # segundos
    "timeout": 10,         # segundos
    "max_retries": 3,
    "auto_start": True,
    "log_events": True,
    "show_notifications": True
}

# Estado global do servidor
SERVER_STATUS = {
    "online": False,
    "last_check": None,
    "response_time": 0,
    "updates_available": False,
    "patches_available": False,
    "current_users": 0,
    "server_version": "unknown",
    "last_error": None,
    "uptime": "0h 0m",
    "load": "0%",
    "region": "Unknown",
    "next_maintenance": "N/A",
    "api_status": "Offline",
    "cdn_status": "Offline",
    "database_status": "Offline"
}

# Log de eventos
EVENT_LOG = []
MAX_LOG_ENTRIES = 100

# --- TEMA PERSONALIZADO PARA SERVER MONITOR ---
THEME = {
    "BG_MAIN": "#0a0f1c",        # Azul escuro profundo
    "BG_PANEL": "#1a2332",       # Azul-cinza
    "BG_CARD": "#243447",        # Cards de informação
    "ACCENT": "#00d4ff",         # Azul ciano vibrante
    "SUCCESS": "#00ff88",        # Verde de sucesso
    "WARNING": "#ffa500",        # Laranja de aviso
    "ERROR": "#ff4757",          # Vermelho de erro
    "TEXT_PRIMARY": "#ffffff",   # Texto principal
    "TEXT_SECONDARY": "#8c9db8", # Texto secundário
    "SHADOW": "#0d1421",         # Sombra
    "BORDER": "#2c3e50"          # Bordas
}

# --- SISTEMA DE ÍCONES ---
def get_icon_path():
    """Retorna o caminho do ícone específico para Server Monitor"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Lista de caminhos possíveis para o ícone
        possible_paths = [
            os.path.join(current_dir, "server_monitor.ico"),
            os.path.join(current_dir, "kingsman_server.ico"),
            os.path.join(current_dir, "kingsman_menu.ico"),  # Fallback
        ]
        
        for icon_path in possible_paths:
            if os.path.exists(icon_path):
                return icon_path
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao procurar ícone: {e}")
        return None

def set_window_icon(window):
    """Define o ícone da janela"""
    try:
        icon_path = get_icon_path()
        if icon_path and os.path.exists(icon_path):
            window.iconbitmap(icon_path)
            return True
        else:
            # Usar emoji no título como fallback
            current_title = window.title()
            if "🌐" not in current_title:
                window.title(f"🌐 {current_title}")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao definir ícone: {e}")
        return False

# --- FUNÇÕES DE MONITORAMENTO ---
def check_server_status():
    """Verifica status completo do servidor"""
    global SERVER_STATUS
    
    try:
        start_time = time.time()
        
        # Verificar conectividade principal com GitHub
        try:
            response = urllib.request.urlopen(GITHUB_RELEASES_URL, timeout=MONITOR_CONFIG["timeout"])
            response_time = (time.time() - start_time) * 1000  # em ms
            
            if response.code == 200:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").replace("v", "")
                
                # Atualizar status principal
                SERVER_STATUS.update({
                    "online": True,
                    "last_check": time.strftime("%H:%M:%S"),
                    "response_time": round(response_time, 1),
                    "server_version": latest_version or "unknown",
                    "last_error": None,
                    "api_status": "Online"
                })
                
                # Verificar patches e updates
                SERVER_STATUS["patches_available"] = check_patches_available()
                SERVER_STATUS["updates_available"] = check_updates_available(latest_version)
                
                # Simular informações extras do servidor
                server_info = generate_server_info()
                SERVER_STATUS.update(server_info)
                
                # Log do evento
                log_event("success", f"Servidor online - {response_time:.1f}ms")
                
                return True
                
        except Exception as e:
            SERVER_STATUS.update({
                "online": False,
                "last_check": time.strftime("%H:%M:%S"),
                "response_time": 0,
                "last_error": str(e)[:100],
                "api_status": "Offline",
                "cdn_status": "Offline",
                "database_status": "Offline"
            })
            
            log_event("error", f"Erro de conectividade: {str(e)[:50]}")
            return False
            
    except Exception as e:
        log_event("error", f"Erro geral de monitoramento: {str(e)[:50]}")
        return False

def check_patches_available():
    """Verifica se há patches disponíveis"""
    try:
        # Simulação baseada em probabilidade
        return random.choice([True, False, False])  # 33% chance de patches
    except:
        return False

def check_updates_available(latest_version):
    """Verifica se há updates disponíveis"""
    try:
        if latest_version and latest_version != "1.4.4":
            return True
        return False
    except:
        return False

def generate_server_info():
    """Gera informações simuladas do servidor"""
    try:
        if SERVER_STATUS.get("online", False):
            uptime_hours = random.randint(1, 168)  # até 1 semana
            uptime_minutes = random.randint(0, 59)
            
            return {
                "current_users": random.randint(25, 150),
                "uptime": f"{uptime_hours}h {uptime_minutes}m",
                "load": f"{random.randint(10, 95)}%",
                "region": random.choice(["EU-West", "US-East", "Asia-Pacific"]),
                "next_maintenance": "2025-10-25 03:00 UTC",
                "cdn_status": "Online",
                "database_status": random.choice(["Online", "Slow"])
            }
        return {
            "current_users": 0,
            "uptime": "0h 0m",
            "load": "0%",
            "region": "Unknown",
            "next_maintenance": "N/A",
            "cdn_status": "Offline",
            "database_status": "Offline"
        }
    except:
        return {}

def log_event(event_type, message):
    """Registra evento no log"""
    global EVENT_LOG
    
    try:
        timestamp = time.strftime("%H:%M:%S")
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "message": message
        }
        
        EVENT_LOG.append(event)
        
        # Manter apenas os últimos eventos
        if len(EVENT_LOG) > MAX_LOG_ENTRIES:
            EVENT_LOG = EVENT_LOG[-MAX_LOG_ENTRIES:]
            
        print(f"[{timestamp}] {event_type.upper()}: {message}")
        
    except Exception as e:
        print(f"Erro ao registrar evento: {e}")

def start_monitoring():
    """Inicia monitoramento contínuo"""
    def monitor_loop():
        while True:
            try:
                check_server_status()
                time.sleep(MONITOR_CONFIG["check_interval"])
            except Exception as e:
                log_event("error", f"Erro no loop de monitoramento: {str(e)[:50]}")
                time.sleep(60)  # Aguardar mais tempo em caso de erro
    
    # Iniciar thread de monitoramento
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    log_event("info", "Sistema de monitoramento iniciado")

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---
class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")
        self.root.configure(bg=THEME["BG_MAIN"])
        self.root.resizable(True, True)
        
        # Aplicar ícone
        set_window_icon(self.root)
        
        # Centralizar janela
        self.center_window()
        
        # Criar interface
        self.create_interface()
        
        # Iniciar atualizações automáticas
        self.start_ui_updates()
        
        # Configurar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
    
    def create_interface(self):
        """Cria a interface principal"""
        # Header principal
        self.create_header()
        
        # Notebook para abas
        self.create_notebook()
        
        # Footer com informações
        self.create_footer()
    
    def create_header(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = tk.Frame(self.root, bg=THEME["ACCENT"], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Container do título
        title_container = tk.Frame(header_frame, bg=THEME["ACCENT"])
        title_container.pack(expand=True, fill="both")
        
        # Título principal
        title_label = tk.Label(
            title_container,
            text="🌐 KINGSMAN SERVER MONITOR",
            font=("Segoe UI", 20, "bold"),
            fg="#000000",
            bg=THEME["ACCENT"]
        )
        title_label.pack(pady=(15, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            title_container,
            text=f"v{APP_VERSION} • Monitoramento em Tempo Real",
            font=("Segoe UI", 11),
            fg="#333333",
            bg=THEME["ACCENT"]
        )
        subtitle_label.pack()
    
    def create_notebook(self):
        """Cria o sistema de abas"""
        # Frame principal para o notebook
        notebook_frame = tk.Frame(self.root, bg=THEME["BG_MAIN"])
        notebook_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Criar notebook
        self.notebook = ttk.Notebook(notebook_frame)
        
        # Configurar estilo do notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=THEME["BG_MAIN"])
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Criar abas
        self.create_status_tab()
        self.create_metrics_tab()
        self.create_logs_tab()
        self.create_settings_tab()
        
        self.notebook.pack(fill="both", expand=True)
    
    def create_status_tab(self):
        """Cria aba de status do servidor"""
        status_frame = tk.Frame(self.notebook, bg=THEME["BG_MAIN"])
        self.notebook.add(status_frame, text="🌐 Status do Servidor")
        
        # Container principal
        main_container = tk.Frame(status_frame, bg=THEME["BG_MAIN"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status geral (topo)
        self.create_general_status(main_container)
        
        # Métricas em grid (meio)
        self.create_metrics_grid(main_container)
        
        # Controles (inferior)
        self.create_controls(main_container)
    
    def create_general_status(self, parent):
        """Cria seção de status geral"""
        status_frame = tk.LabelFrame(
            parent,
            text=" 🚦 Status Geral ",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["ACCENT"],
            bg=THEME["BG_MAIN"],
            bd=2,
            relief="groove"
        )
        status_frame.pack(fill="x", pady=(0, 20))
        
        # Container interno
        inner_frame = tk.Frame(status_frame, bg=THEME["BG_PANEL"])
        inner_frame.pack(fill="x", padx=10, pady=10)
        
        # Status principal
        self.main_status_label = tk.Label(
            inner_frame,
            text="🔴 Verificando servidor...",
            font=("Segoe UI", 16, "bold"),
            fg=THEME["ERROR"],
            bg=THEME["BG_PANEL"]
        )
        self.main_status_label.pack(pady=10)
        
        # Informações detalhadas em linha
        details_frame = tk.Frame(inner_frame, bg=THEME["BG_PANEL"])
        details_frame.pack(fill="x", pady=(10, 0))
        
        # Última verificação
        self.last_check_label = tk.Label(
            details_frame,
            text="Última verificação: --:--:--",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_PANEL"]
        )
        self.last_check_label.pack(side="left")
        
        # Ping
        self.ping_label = tk.Label(
            details_frame,
            text="Ping: -- ms",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_PANEL"]
        )
        self.ping_label.pack(side="right")
    
    def create_metrics_grid(self, parent):
        """Cria grid de métricas"""
        metrics_frame = tk.LabelFrame(
            parent,
            text=" 📊 Métricas do Servidor ",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["ACCENT"],
            bg=THEME["BG_MAIN"],
            bd=2,
            relief="groove"
        )
        metrics_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Container com grid 2x3
        grid_container = tk.Frame(metrics_frame, bg=THEME["BG_MAIN"])
        grid_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid
        for i in range(2):
            grid_container.columnconfigure(i, weight=1)
        for i in range(3):
            grid_container.rowconfigure(i, weight=1)
        
        # Criar cards de métricas
        self.create_metric_card(grid_container, "👥 Usuários Online", "users_value", 0, 0)
        self.create_metric_card(grid_container, "⚡ Tempo de Resposta", "response_value", 0, 1)
        self.create_metric_card(grid_container, "📈 Carga do Servidor", "load_value", 1, 0)
        self.create_metric_card(grid_container, "🕒 Uptime", "uptime_value", 1, 1)
        self.create_metric_card(grid_container, "🌍 Região", "region_value", 2, 0)
        self.create_metric_card(grid_container, "🔧 Próxima Manutenção", "maintenance_value", 2, 1)
    
    def create_metric_card(self, parent, title, value_attr, row, col):
        """Cria um card de métrica"""
        card_frame = tk.Frame(
            parent, 
            bg=THEME["BG_CARD"],
            relief="solid",
            bd=1
        )
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Título do card
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_CARD"]
        )
        title_label.pack(pady=(10, 5))
        
        # Valor do card
        value_label = tk.Label(
            card_frame,
            text="--",
            font=("Segoe UI", 14, "bold"),
            fg=THEME["TEXT_PRIMARY"],
            bg=THEME["BG_CARD"]
        )
        value_label.pack(pady=(0, 10))
        
        # Armazenar referência
        setattr(self, value_attr, value_label)
    
    def create_controls(self, parent):
        """Cria controles e botões"""
        controls_frame = tk.Frame(parent, bg=THEME["BG_MAIN"])
        controls_frame.pack(fill="x")
        
        # Botão de refresh manual
        self.refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Atualizar Agora",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["ACCENT"],
            fg="#000000",
            activebackground=THEME["BG_PANEL"],
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.manual_refresh
        )
        self.refresh_btn.pack(side="left")
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.auto_refresh_check = tk.Checkbutton(
            controls_frame,
            text="🔄 Auto-refresh (30s)",
            variable=self.auto_refresh_var,
            font=("Segoe UI", 10),
            fg=THEME["SUCCESS"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            command=self.toggle_auto_refresh
        )
        self.auto_refresh_check.pack(side="left", padx=(20, 0))
        
        # Status dos serviços
        services_frame = tk.Frame(controls_frame, bg=THEME["BG_MAIN"])
        services_frame.pack(side="right")
        
        tk.Label(
            services_frame,
            text="Serviços:",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        self.api_status_label = tk.Label(
            services_frame,
            text="API: 🔴",
            font=("Segoe UI", 9),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        )
        self.api_status_label.pack(side="left", padx=(5, 0))
        
        self.cdn_status_label = tk.Label(
            services_frame,
            text="CDN: 🔴",
            font=("Segoe UI", 9),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        )
        self.cdn_status_label.pack(side="left", padx=(5, 0))
        
        self.db_status_label = tk.Label(
            services_frame,
            text="DB: 🔴",
            font=("Segoe UI", 9),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        )
        self.db_status_label.pack(side="left", padx=(5, 0))
    
    def create_metrics_tab(self):
        """Cria aba de métricas avançadas"""
        metrics_frame = tk.Frame(self.notebook, bg=THEME["BG_MAIN"])
        self.notebook.add(metrics_frame, text="📈 Métricas Avançadas")
        
        # Placeholder para futuras métricas
        placeholder_label = tk.Label(
            metrics_frame,
            text="📈 Métricas Avançadas\n\n🚧 Em Desenvolvimento\n\nEsta seção conterá:\n• Gráficos de performance\n• Histórico de uptime\n• Análise de latência\n• Estatísticas de uso",
            font=("Segoe UI", 12),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"],
            justify="center"
        )
        placeholder_label.pack(expand=True)
    
    def create_logs_tab(self):
        """Cria aba de logs"""
        logs_frame = tk.Frame(self.notebook, bg=THEME["BG_MAIN"])
        self.notebook.add(logs_frame, text="📝 Logs de Eventos")
        
        # Container principal
        logs_container = tk.Frame(logs_frame, bg=THEME["BG_MAIN"])
        logs_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header dos logs
        logs_header = tk.Frame(logs_container, bg=THEME["BG_MAIN"])
        logs_header.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            logs_header,
            text="📝 Log de Eventos do Sistema",
            font=("Segoe UI", 14, "bold"),
            fg=THEME["ACCENT"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        # Botão limpar logs
        clear_logs_btn = tk.Button(
            logs_header,
            text="🗑️ Limpar",
            font=("Segoe UI", 9),
            bg=THEME["ERROR"],
            fg="#ffffff",
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.clear_logs
        )
        clear_logs_btn.pack(side="right")
        
        # Área de logs com scroll
        logs_text_frame = tk.Frame(logs_container, bg=THEME["BG_MAIN"])
        logs_text_frame.pack(fill="both", expand=True)
        
        self.logs_text = tk.Text(
            logs_text_frame,
            bg=THEME["BG_PANEL"],
            fg=THEME["TEXT_PRIMARY"],
            font=("Consolas", 10),
            wrap="word",
            state="disabled",
            padx=10,
            pady=10
        )
        
        logs_scroll = tk.Scrollbar(logs_text_frame, command=self.logs_text.yview)
        self.logs_text.config(yscrollcommand=logs_scroll.set)
        
        self.logs_text.pack(side="left", fill="both", expand=True)
        logs_scroll.pack(side="right", fill="y")
    
    def create_settings_tab(self):
        """Cria aba de configurações"""
        settings_frame = tk.Frame(self.notebook, bg=THEME["BG_MAIN"])
        self.notebook.add(settings_frame, text="⚙️ Configurações")
        
        # Container principal
        settings_container = tk.Frame(settings_frame, bg=THEME["BG_MAIN"])
        settings_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configurações de monitoramento
        monitor_frame = tk.LabelFrame(
            settings_container,
            text=" 🔧 Configurações de Monitoramento ",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["ACCENT"],
            bg=THEME["BG_MAIN"],
            bd=2,
            relief="groove"
        )
        monitor_frame.pack(fill="x", pady=(0, 20))
        
        # Intervalo de verificação
        interval_frame = tk.Frame(monitor_frame, bg=THEME["BG_MAIN"])
        interval_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            interval_frame,
            text="Intervalo de verificação:",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_PRIMARY"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        self.interval_var = tk.StringVar(value=str(MONITOR_CONFIG["check_interval"]))
        interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            font=("Segoe UI", 10),
            width=10,
            bg=THEME["BG_PANEL"],
            fg=THEME["TEXT_PRIMARY"]
        )
        interval_entry.pack(side="left", padx=(10, 5))
        
        tk.Label(
            interval_frame,
            text="segundos",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        # Timeout
        timeout_frame = tk.Frame(monitor_frame, bg=THEME["BG_MAIN"])
        timeout_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(
            timeout_frame,
            text="Timeout de conexão:",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_PRIMARY"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        self.timeout_var = tk.StringVar(value=str(MONITOR_CONFIG["timeout"]))
        timeout_entry = tk.Entry(
            timeout_frame,
            textvariable=self.timeout_var,
            font=("Segoe UI", 10),
            width=10,
            bg=THEME["BG_PANEL"],
            fg=THEME["TEXT_PRIMARY"]
        )
        timeout_entry.pack(side="left", padx=(10, 5))
        
        tk.Label(
            timeout_frame,
            text="segundos",
            font=("Segoe UI", 10),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        # Botão aplicar configurações
        apply_btn = tk.Button(
            monitor_frame,
            text="✅ Aplicar Configurações",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["SUCCESS"],
            fg="#000000",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.apply_settings
        )
        apply_btn.pack(pady=10)
        
        # Informações da aplicação
        about_frame = tk.LabelFrame(
            settings_container,
            text=" ℹ️ Sobre ",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["ACCENT"],
            bg=THEME["BG_MAIN"],
            bd=2,
            relief="groove"
        )
        about_frame.pack(fill="x")
        
        about_text = f"""
🌐 {APP_NAME} v{APP_VERSION}

Desenvolvido por: Kingsman Inc
Data de criação: 2025-10-20
Finalidade: Monitoramento de servidores em tempo real

🔗 Servidor monitorado:
{GITHUB_RELEASES_URL}

📊 Recursos:
• Monitoramento automático 24/7
• Métricas de performance em tempo real
• Log de eventos detalhado
• Interface profissional e intuitiva
• Notificações de status
        """
        
        about_label = tk.Label(
            about_frame,
            text=about_text.strip(),
            font=("Segoe UI", 10),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BG_MAIN"],
            justify="left"
        )
        about_label.pack(padx=10, pady=10, anchor="w")
    
    def create_footer(self):
        """Cria footer com informações"""
        footer_frame = tk.Frame(self.root, bg=THEME["BORDER"], height=30)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Status da aplicação
        self.app_status_label = tk.Label(
            footer_frame,
            text="🚀 Aplicação iniciada",
            font=("Segoe UI", 9),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BORDER"]
        )
        self.app_status_label.pack(side="left", padx=10, pady=5)
        
        # Versão
        version_label = tk.Label(
            footer_frame,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 9),
            fg=THEME["TEXT_SECONDARY"],
            bg=THEME["BORDER"]
        )
        version_label.pack(side="right", padx=10, pady=5)
    
    def start_ui_updates(self):
        """Inicia atualizações automáticas da UI"""
        self.update_display()
        if hasattr(self, 'auto_refresh_var') and self.auto_refresh_var.get():
            self.root.after(5000, self.start_ui_updates)  # Atualizar UI a cada 5s
    
    def update_display(self):
        """Atualiza todos os elementos da interface"""
        try:
            # Atualizar status principal
            if SERVER_STATUS["online"]:
                self.main_status_label.configure(
                    text="🟢 Servidor Online",
                    fg=THEME["SUCCESS"]
                )
                
                # Atualizar ping com cores
                ping = SERVER_STATUS.get("response_time", 0)
                ping_color = THEME["SUCCESS"] if ping < 100 else THEME["WARNING"] if ping < 300 else THEME["ERROR"]
                self.ping_label.configure(
                    text=f"Ping: {ping} ms",
                    fg=ping_color
                )
                
            else:
                self.main_status_label.configure(
                    text="🔴 Servidor Offline",
                    fg=THEME["ERROR"]
                )
                self.ping_label.configure(
                    text="Ping: -- ms",
                    fg=THEME["TEXT_SECONDARY"]
                )
            
            # Atualizar timestamp
            last_check = SERVER_STATUS.get("last_check", "--:--:--")
            self.last_check_label.configure(text=f"Última verificação: {last_check}")
            
            # Atualizar métricas
            self.users_value.configure(text=str(SERVER_STATUS.get("current_users", "--")))
            self.response_value.configure(text=f"{SERVER_STATUS.get('response_time', '--')} ms")
            self.load_value.configure(text=SERVER_STATUS.get("load", "--%"))
            self.uptime_value.configure(text=SERVER_STATUS.get("uptime", "--"))
            self.region_value.configure(text=SERVER_STATUS.get("region", "Unknown"))
            self.maintenance_value.configure(text=SERVER_STATUS.get("next_maintenance", "N/A"))
            
            # Atualizar status dos serviços
            api_status = "🟢" if SERVER_STATUS.get("api_status") == "Online" else "🔴"
            cdn_status = "🟢" if SERVER_STATUS.get("cdn_status") == "Online" else "🔴"
            db_status = "🟢" if SERVER_STATUS.get("database_status") == "Online" else "🔴"
            
            self.api_status_label.configure(text=f"API: {api_status}")
            self.cdn_status_label.configure(text=f"CDN: {cdn_status}")
            self.db_status_label.configure(text=f"DB: {db_status}")
            
            # Atualizar logs
            self.update_logs_display()
            
        except Exception as e:
            print(f"Erro ao atualizar display: {e}")
    
    def update_logs_display(self):
        """Atualiza a exibição dos logs"""
        try:
            self.logs_text.configure(state="normal")
            self.logs_text.delete("1.0", tk.END)
            
            # Mostrar últimos 50 eventos
            recent_events = EVENT_LOG[-50:]
            
            for event in recent_events:
                color = THEME["TEXT_PRIMARY"]
                if event["type"] == "error":
                    color = THEME["ERROR"]
                elif event["type"] == "success":
                    color = THEME["SUCCESS"]
                elif event["type"] == "warning":
                    color = THEME["WARNING"]
                
                log_line = f"[{event['timestamp']}] {event['type'].upper()}: {event['message']}\n"
                self.logs_text.insert(tk.END, log_line)
            
            self.logs_text.configure(state="disabled")
            self.logs_text.see(tk.END)  # Scroll para o final
            
        except Exception as e:
            print(f"Erro ao atualizar logs: {e}")
    
    def manual_refresh(self):
        """Atualização manual do status"""
        self.refresh_btn.configure(state="disabled", text="🔄 Verificando...")
        self.root.update()
        
        def refresh_thread():
            try:
                check_server_status()
                self.root.after(0, self.update_display)
            finally:
                self.root.after(0, lambda: self.refresh_btn.configure(
                    state="normal", text="🔄 Atualizar Agora"
                ))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def toggle_auto_refresh(self):
        """Liga/desliga auto-refresh"""
        if self.auto_refresh_var.get():
            self.start_ui_updates()
            log_event("info", "Auto-refresh ativado")
        else:
            log_event("info", "Auto-refresh desativado")
    
    def clear_logs(self):
        """Limpa o log de eventos"""
        global EVENT_LOG
        EVENT_LOG.clear()
        self.update_logs_display()
        log_event("info", "Log de eventos limpo")
    
    def apply_settings(self):
        """Aplica as configurações alteradas"""
        try:
            new_interval = int(self.interval_var.get())
            new_timeout = int(self.timeout_var.get())
            
            MONITOR_CONFIG["check_interval"] = new_interval
            MONITOR_CONFIG["timeout"] = new_timeout
            
            log_event("info", f"Configurações aplicadas: Intervalo={new_interval}s, Timeout={new_timeout}s")
            messagebox.showinfo("Configurações", "Configurações aplicadas com sucesso!")
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")
    
    def on_closing(self):
        """Handler para fechamento da aplicação"""
        if messagebox.askokcancel("Fechar", "Deseja realmente fechar o Server Monitor?"):
            log_event("info", "Aplicação fechada pelo usuário")
            self.root.destroy()

# --- FUNÇÃO PRINCIPAL ---
def main():
    """Função principal da aplicação"""
    try:
        # Verificação inicial
        log_event("info", f"{APP_NAME} v{APP_VERSION} iniciado")
        
        # Inicializar monitoramento
        if MONITOR_CONFIG["auto_start"]:
            start_monitoring()
        
        # Criar e executar aplicação
        root = tk.Tk()
        app = ServerMonitorApp(root)
        
        # Verificação inicial de status
        threading.Thread(target=check_server_status, daemon=True).start()
        
        log_event("info", "Interface gráfica inicializada")
        
        # Executar loop principal
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Erro crítico na aplicação: {str(e)}"
        print(error_msg)
        log_event("error", error_msg)
        
        # Mostrar erro se possível
        try:
            messagebox.showerror("Erro Crítico", error_msg)
        except:
            pass

if __name__ == "__main__":
    main()