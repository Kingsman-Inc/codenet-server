import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, simpledialog
import subprocess
import sys
import os
import threading
import json
import random  # <-- For random game functionality
import urllib.request
import urllib.error
import time
import gc
from functools import lru_cache
import zipfile
import tempfile
import shutil
import hashlib
import webbrowser  # Added for opening URLs and Discord integration

# --- CONFIGURAÇÕES GITHUB KINGSMAN-INC ---
GITHUB_ORG = "Kingsman-Inc"
GITHUB_REPO = "Kingsman-Menu"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}"
GITHUB_RELEASES_URL = f"{GITHUB_API_BASE}/releases/latest"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_ORG}/{GITHUB_REPO}/main"
KINGSMAN_UPDATE_API = f"https://{GITHUB_ORG.lower()}.github.io/{GITHUB_REPO.lower()}/api/latest.json"

# Configurações de versão
CURRENT_VERSION = "1.4.2"
CURRENT_PATCH = "1.4.2"

# Configurações de Update Automático - será carregado dinamicamente
AUTO_UPDATE_CONFIG = {}

# Otimizações de performance
PERFORMANCE_MODE = True
MEMORY_CLEANUP_INTERVAL = 300  # 5 minutos

def optimize_memory():
    """Otimização de memória e garbage collection"""
    if PERFORMANCE_MODE:
        try:
            # Forçar garbage collection
            collected = gc.collect()
            
            # Compactar heap de strings (Python 3.3+)
            if hasattr(gc, 'collect_young'):
                gc.collect_young()
                
            return collected
        except Exception as e:
            print(f"Erro na otimização de memória: {e}")
            return 0

def schedule_memory_cleanup():
    """Agendar limpeza de memória periódica"""
    global root
    if PERFORMANCE_MODE and 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
        optimize_memory()
        # Reagendar para próxima limpeza
        root.after(MEMORY_CLEANUP_INTERVAL * 1000, schedule_memory_cleanup)

def safe_execute(func, error_msg="Erro na operação", *args, **kwargs):
    """Executa função de forma segura com tratamento de erro"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"{error_msg}: {e}")
        if 'root' in globals() and hasattr(root, 'winfo_exists'):
            try:
                if root.winfo_exists():
                    messagebox.showerror("Erro", f"{error_msg}:\n{str(e)[:200]}")
            except:
                pass  # Falha silenciosa se GUI não estiver disponível
        return None

def optimize_startup():
    """Otimizações na inicialização da aplicação"""
    try:
        # Configurar garbage collection para performance
        if hasattr(gc, 'set_threshold'):
            gc.set_threshold(700, 10, 10)  # Configuração otimizada
        
        # Configurar thread pool para operações assíncronas
        threading.current_thread().name = "MainThread"
        
        # Pre-aquecer cache de temas
        load_theme()
        
        return True
    except Exception as e:
        print(f"Erro na otimização de startup: {e}")
        return False

# Importar patch manager com tratamento melhorado de erro
try:
    from patch_manager import patch_manager, check_patches_on_startup, start_automatic_patch_checking, manual_check_patches
    PATCH_SYSTEM_AVAILABLE = True
except ImportError as e:
    # Fallback se patch_manager não estiver disponível
    print(f"Patch system não disponível: {e}")
    patch_manager = None
    PATCH_SYSTEM_AVAILABLE = False
    def check_patches_on_startup(): pass
    def start_automatic_patch_checking(): pass
    def manual_check_patches(): messagebox.showinfo("Patches", "Sistema de patches não disponível.")

AGENT_NAME = "Kingsman"  # Optional: personalize agent name
AGENT_PASSWORD = "kingsman"  # Set your desired password here

# --- Agent UI Theme (will be updated at runtime) ---
THEME = {
    "BG_MAIN": "#13151A",
    "BG_PANEL": "#23262C",
    "GOLD": "#FFD700",
    "SHADOW": "#25304A",
    "BTN_OUTLINE": "#FFD700",
    "EXIT_BG": "#23262C",
    "EXIT_ACTIVE": "#36393C",
}

# --- Theme Presets ---
THEME_PRESETS = {
    "Default": {
        "BG_MAIN": "#13151A",
        "BG_PANEL": "#23262C",
        "GOLD": "#FFD700",
        "SHADOW": "#25304A",
        "BTN_OUTLINE": "#FFD700",
        "EXIT_BG": "#23262C",
        "EXIT_ACTIVE": "#36393C",
    },
    "Dark Blue": {
        "BG_MAIN": "#0F1419",
        "BG_PANEL": "#1E2328",
        "GOLD": "#64FFDA",
        "SHADOW": "#263238",
        "BTN_OUTLINE": "#64FFDA",
        "EXIT_BG": "#1E2328",
        "EXIT_ACTIVE": "#2D3748",
    },
    "Purple Night": {
        "BG_MAIN": "#1A0F1A",
        "BG_PANEL": "#2D1B2E",
        "GOLD": "#E91E63",
        "SHADOW": "#4A148C",
        "BTN_OUTLINE": "#E91E63",
        "EXIT_BG": "#2D1B2E",
        "EXIT_ACTIVE": "#3E2A3F",
    },
    "Forest Green": {
        "BG_MAIN": "#0F1A0F",
        "BG_PANEL": "#1B2D1B",
        "GOLD": "#4CAF50",
        "SHADOW": "#2E7D32",
        "BTN_OUTLINE": "#4CAF50",
        "EXIT_BG": "#1B2D1B",
        "EXIT_ACTIVE": "#2A3E2A",
    },
    "Crimson Red": {
        "BG_MAIN": "#1A0F0F",
        "BG_PANEL": "#2D1B1B",
        "GOLD": "#FF5722",
        "SHADOW": "#B71C1C",
        "BTN_OUTLINE": "#FF5722",
        "EXIT_BG": "#2D1B1B",
        "EXIT_ACTIVE": "#3E2A2A",
    }
}

# --- Theme Management Functions ---
def load_custom_themes():
    """Carrega temas personalizados do arquivo"""
    try:
        themes_file = os.path.join(_get_settings_file_path(), "themes.json")
        if os.path.exists(themes_file):
            with open(themes_file, 'r', encoding='utf-8') as f:
                custom_themes = json.load(f)
                # Mesclar temas personalizados com presets
                return {**THEME_PRESETS, **custom_themes}
    except Exception as e:
        print(f"Erro ao carregar temas personalizados: {e}")
    return THEME_PRESETS.copy()

def save_custom_theme(theme_name, theme_data):
    """Salva um tema personalizado"""
    try:
        themes_file = os.path.join(_get_settings_file_path(), "themes.json")
        custom_themes = {}
        
        # Carregar temas existentes
        if os.path.exists(themes_file):
            with open(themes_file, 'r', encoding='utf-8') as f:
                custom_themes = json.load(f)
        
        # Adicionar novo tema
        custom_themes[theme_name] = theme_data
        
        # Salvar
        with open(themes_file, 'w', encoding='utf-8') as f:
            json.dump(custom_themes, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar tema: {e}")
        return False

def apply_theme(theme_name):
    """Aplica um tema específico"""
    global THEME
    all_themes = load_custom_themes()
    if theme_name in all_themes:
        THEME.update(all_themes[theme_name])
        save_current_theme(theme_name)
        return True
    return False

def save_current_theme(theme_name):
    """Salva o tema atual como preferência"""
    try:
        settings_file = os.path.join(_get_settings_file_path(), "settings.json")
        settings = {}
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        
        settings["current_theme"] = theme_name
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar configuração de tema: {e}")

def load_current_theme():
    """Carrega o tema salvo nas configurações"""
    try:
        settings_file = os.path.join(_get_settings_file_path(), "settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                theme_name = settings.get("current_theme", "Default")
                apply_theme(theme_name)
                return theme_name
    except Exception as e:
        print(f"Erro ao carregar tema: {e}")
    return "Default"

# --- Persistent configuration files ---
def _get_settings_file_path():
    """
    Store settings under %APPDATA%/Kingsman Menu/ on Windows.
    Fallback to the user's home directory if APPDATA is not available.
    """
    appdata = os.environ.get("APPDATA")
    base_dir = appdata if appdata else os.path.expanduser("~")
    settings_dir = os.path.join(base_dir, "Kingsman Menu")
    try:
        os.makedirs(settings_dir, exist_ok=True)
    except Exception:
        # As a last resort, fall back to script directory
        settings_dir = os.path.dirname(os.path.abspath(__file__))
    return settings_dir

SETTINGS_DIR = _get_settings_file_path()
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "games_paths.json")
GAMES_CONFIG_FILE = os.path.join(SETTINGS_DIR, "games_config.json")
THEME_FILE = os.path.join(SETTINGS_DIR, "theme_settings.json")
CREDENTIALS_FILE = os.path.join(SETTINGS_DIR, "kingsman_agents.json")  # Sistema de autenticação
GAMES_FILE = os.path.join(SETTINGS_DIR, "kingsman_games.json")  # Lista de jogos aprimorada



# --- Persistent Game Path Store (Otimizado) ---
_game_paths_cache = None
_games_cache = None

# --- Sistema de Autenticação de Agentes ---
def hash_password(password):
    """Cria hash seguro da senha usando SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_agent_credentials():
    """Carrega credenciais dos agentes"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_agent_credentials(credentials):
    """Salva credenciais dos agentes"""
    try:
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=2)
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")

def load_games_v3():
    """Load games (name and path) from file - versão aprimorada"""
    if os.path.exists(GAMES_FILE):
        try:
            with open(GAMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_games_v3(games):
    """Save games list to file - versão aprimorada"""
    try:
        with open(GAMES_FILE, "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar jogos: {e}")

@lru_cache(maxsize=1)
def load_game_paths():
    """Carrega paths dos jogos com cache para melhor performance"""
    global _game_paths_cache
    try:
        if _game_paths_cache is None:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                _game_paths_cache = json.load(f)
        return _game_paths_cache
    except Exception:
        _game_paths_cache = {}
        return _game_paths_cache

def save_game_paths(paths):
    """Salva paths com validação e tratamento de erro melhorado"""
    global _game_paths_cache
    try:
        # Validar dados antes de salvar
        if not isinstance(paths, dict):
            raise ValueError("Paths deve ser um dicionário")
        
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(paths, f, indent=2, ensure_ascii=False)
        
        # Atualizar cache
        _game_paths_cache = paths
        # Limpar cache LRU
        load_game_paths.cache_clear()
        
    except Exception as e:
        print(f"Erro ao salvar caminhos dos jogos: {e}")
        messagebox.showerror("Erro", f"Não foi possível salvar configurações: {e}")

GAME_PATHS = load_game_paths()

def get_game_path(game_key, default=None):
    """Obtém caminho do jogo com fallback seguro"""
    paths = load_game_paths()
    return paths.get(game_key, default)

def set_game_path(game_key, path):
    """Define caminho do jogo com validação"""
    if not game_key or not isinstance(game_key, str):
        raise ValueError("game_key deve ser uma string válida")
    
    if path and not os.path.exists(path):
        print(f"Aviso: Caminho não existe: {path}")
    
    global GAME_PATHS
    GAME_PATHS[game_key] = path
    save_game_paths(GAME_PATHS)

# --- Games Database Persistent Store (Otimizado) ---
@lru_cache(maxsize=1)
def load_games_list():
    """Carrega lista de jogos com cache e tratamento de erro melhorado"""
    global _games_cache
    try:
        if _games_cache is None:
            if os.path.exists(GAMES_CONFIG_FILE):
                with open(GAMES_CONFIG_FILE, "r", encoding="utf-8") as f:
                    games = json.load(f)
                
                # Validação mais rigorosa
                if isinstance(games, list) and all(
                    isinstance(g, dict) and 'name' in g and 'key' in g 
                    for g in games
                ):
                    _games_cache = games
                else:
                    raise ValueError("Formato de jogos inválido")
            else:
                # Default games (back-compat with old hardcoded list)
                _games_cache = [
                    {"name": "Rocket League", "emoji": "🚗", "key": "rocket_league", 
                     "default_path": r"A:\Epic\rocketleague\Binaries\Win64\RocketLeague.exe"},
                    {"name": "GTA V", "emoji": "🚓", "key": "gta_v",
                     "default_path": r"A:\Rockstar Games\Grand Theft Auto V\GTAV.exe"},
                    {"name": "Valorant", "emoji": "🎯", "key": "valorant",
                     "default_path": r"C:\Riot Games\Valorant\live\Valorant.exe"},
                    {"name": "Fortnite", "emoji": "🏗️", "key": "fortnite",
                     "default_path": r"C:\Program Files\Epic Games\Fortnite\FortniteClient-Win64-Shipping.exe"},
                ]
        return _games_cache
        
    except Exception as e:
        print(f"Erro ao carregar configuração de jogos: {e}")
        # Fallback seguro
        _games_cache = [
            {"name": "Rocket League", "emoji": "🚗", "key": "rocket_league",
             "default_path": r"A:\Epic\rocketleague\Binaries\Win64\RocketLeague.exe"},
            {"name": "GTA V", "emoji": "🚓", "key": "gta_v",
             "default_path": r"A:\Rockstar Games\Grand Theft Auto V\GTAV.exe"},
        ]
        return _games_cache

def save_games_list(games):
    """Salva lista de jogos com validação e otimização"""
    global _games_cache
    try:
        # Validar dados antes de salvar
        if not isinstance(games, list):
            raise ValueError("Games deve ser uma lista")
        
        for game in games:
            if not isinstance(game, dict) or 'name' not in game or 'key' not in game:
                raise ValueError("Formato de jogo inválido")
        
        with open(GAMES_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
        
        # Atualizar cache
        _games_cache = games
        load_games_list.cache_clear()
        
    except Exception as e:
        print(f"Erro ao salvar configuração de jogos: {e}")
        messagebox.showerror("Erro", f"Não foi possível salvar jogos: {e}")

GAMES_LIST = load_games_list()

def add_game_to_list(game_dict):
    """Adiciona jogo com validação"""
    try:
        if not isinstance(game_dict, dict) or 'name' not in game_dict or 'key' not in game_dict:
            raise ValueError("Dados do jogo inválidos")
        
        global GAMES_LIST
        # Verificar se já existe
        if any(g['key'] == game_dict['key'] for g in GAMES_LIST):
            messagebox.showwarning("Aviso", "Jogo já existe na lista")
            return False
        
        GAMES_LIST.append(game_dict)
        save_games_list(GAMES_LIST)
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar jogo: {e}")
        return False

def remove_game_from_list(game_key):
    """Remove jogo com validação"""
    try:
        global GAMES_LIST
        original_count = len(GAMES_LIST)
        GAMES_LIST = [g for g in GAMES_LIST if g["key"] != game_key]
        
        if len(GAMES_LIST) == original_count:
            messagebox.showwarning("Aviso", "Jogo não encontrado")
            return False
        
        save_games_list(GAMES_LIST)
        return True
        
    except Exception as e:
        print(f"Erro ao remover jogo: {e}")
        return False

# --- Persistent Theme Store/Load (Otimizado) ---
@lru_cache(maxsize=1)
def _load_theme_cached():
    """Cache interno para evitar recarregamento desnecessário"""
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def load_theme():
    """Carrega tema com validação melhorada e cache"""
    # Primeiro, tenta carregar o tema atual salvo nas configurações
    current_theme = load_current_theme()
    
    # Se não conseguir carregar, tenta o método antigo
    if current_theme == "Default" and os.path.exists(THEME_FILE):
        try:
            # Usar cache para evitar I/O desnecessário
            loaded = _load_theme_cached()
            
            # Validar estrutura do tema
            if loaded and isinstance(loaded, dict):
                for k in THEME:
                    if k in loaded and isinstance(loaded[k], str) and loaded[k].startswith('#'):
                        THEME[k] = loaded[k]
                print("Tema carregado com sucesso (cached)")
            else:
                print("Formato de tema inválido, usando padrão")
                
        except Exception as e:
            print(f"Erro ao carregar tema: {e}")
            # Manter tema padrão em caso de erro

def save_theme():
    """Salva tema com validação"""
    try:
        # Invalidar cache antes de salvar
        _load_theme_cached.cache_clear()
        
        # Validar cores antes de salvar
        for key, value in THEME.items():
            if not isinstance(value, str) or not value.startswith('#'):
                print(f"Cor inválida detectada: {key} = {value}")
                return False
        
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump(THEME, f, indent=2, ensure_ascii=False)
        
        print("Tema salvo com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao salvar tema: {e}")
        messagebox.showerror("Erro", f"Não foi possível salvar tema: {e}")
        return False

# --- Update Checker & Performance Monitor ---
CURRENT_VERSION = "1.4.2"
PATCH_VERSION = "1.4.2" 
UPDATE_CONFIG_FILE = os.path.join(SETTINGS_DIR, "update_config.json")
LAST_VERSION_FILE = os.path.join(SETTINGS_DIR, "last_version.txt")
PERFORMANCE_LOG_FILE = os.path.join(SETTINGS_DIR, "performance.log")

# Sistema de monitoramento de performance
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.operations = {}
    
    def start_operation(self, name):
        self.operations[name] = time.time()
    
    def end_operation(self, name):
        if name in self.operations:
            duration = time.time() - self.operations[name]
            print(f"⚡ {name}: {duration:.3f}s")
            return duration
        return 0
    
    def get_memory_usage(self):
        """Força garbage collection e retorna estatísticas"""
        gc.collect()
        return len(gc.get_objects())

# Instância global do monitor
perf_monitor = PerformanceMonitor()

def show_whats_new_window(version_data, is_patch=False):
    """Mostrar janela 'What's New' após atualização ou patch"""
    
    def create_whats_new():
        # Determinar tipo de atualização
        update_type = "🩹 Patch" if is_patch else "🚀 Update"
        version_display = version_data.get('version', CURRENT_VERSION)
        
        # Criar janela principal
        new_window = tk.Toplevel()
        new_window.title(f"🎉 Kingsman Menu v{version_display} - {update_type}")
        new_window.geometry("400x500")
        new_window.configure(bg=THEME['BG_MAIN'])
        new_window.resizable(False, False)
        new_window.grab_set()
        
        # Centralizar na tela
        new_window.transient()
        new_window.geometry("+%d+%d" % (
            new_window.winfo_screenwidth()//2 - 300,
            new_window.winfo_screenheight()//2 - 250
        ))
        
        # Header com animação
        header_frame = tk.Frame(new_window, bg=THEME['GOLD'], height=80)
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)
        
        # Título principal (adaptado para patches)
        title_emoji = "🩹" if is_patch else "🚀"
        title_text = f"{title_emoji} Kingsman Menu v{version_display}"
        
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=("Segoe UI", 20, "bold"),
            fg="#000000",
            bg=THEME['GOLD']
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle diferenciado para patches
        if is_patch:
            subtitle_text = "🔧 Bug Fixes & Improvements Applied"
        else:
            subtitle_text = "✨ Discover What's New in This Update"
        
        subtitle_label = tk.Label(
            header_frame,
            text=subtitle_text,
            font=("Segoe UI", 11),
            fg="#333333",
            bg=THEME['GOLD']
        )
        subtitle_label.pack()
        
        # Área de conteúdo principal
        main_frame = tk.Frame(new_window, bg=THEME['BG_MAIN'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Criar canvas com scroll
        canvas = tk.Canvas(main_frame, bg=THEME['BG_MAIN'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['BG_MAIN'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Organizar mudanças por categorias (adaptado para patches)
        changelog = version_data.get('changelog', {})
        
        if is_patch:
            # Layout específico para patches
            if changelog.get('critical_fixes'):
                create_category_section(scrollable_frame, "🔴 CRITICAL FIXES", changelog['critical_fixes'], "#F44336")
            
            if changelog.get('bug_fixes'):
                create_category_section(scrollable_frame, "🐛 BUG FIXES", changelog['bug_fixes'], "#FF9800")
            
            if changelog.get('performance'):
                create_category_section(scrollable_frame, "⚡ PERFORMANCE", changelog['performance'], "#4CAF50")
            
            if changelog.get('security'):
                create_category_section(scrollable_frame, "🔒 SECURITY", changelog['security'], "#673AB7")
                
            # Mostrar componentes afetados
            if version_data.get('affected_components'):
                create_info_section(scrollable_frame, "🎯 AFFECTED COMPONENTS", version_data['affected_components'])
        else:
            # Layout normal para atualizações principais
            # 🎯 FUNCIONALIDADES PRINCIPAIS
            if changelog.get('new_features'):
                create_category_section(scrollable_frame, "🎯 NEW FEATURES", changelog['new_features'], "#4CAF50")
            
            # 🛠️ MELHORIAS
            if changelog.get('improvements'):
                create_category_section(scrollable_frame, "🛠️ IMPROVEMENTS", changelog['improvements'], "#2196F3")
            
            # 🐛 CORREÇÕES
            if changelog.get('bug_fixes'):
                create_category_section(scrollable_frame, "🐛 BUG FIXES", changelog['bug_fixes'], "#FF9800")
            
            # 🔧 TÉCNICO
            if changelog.get('technical'):
                create_category_section(scrollable_frame, "🔧 TECHNICAL", changelog['technical'], "#9C27B0")
            
            # 🎨 INTERFACE
            if changelog.get('ui_changes'):
                create_category_section(scrollable_frame, "🎨 INTERFACE", changelog['ui_changes'], "#E91E63")
        
        # Seção de destaque especial para IA (se presente)
        if any('IA' in str(item) or 'AI' in str(item) for category in changelog.values() for item in category):
            create_highlight_section(scrollable_frame, "🤖 AI ASSISTANT", 
                "Revolutionary AI-powered assistance integrated into Kingsman Menu! Chat with our intelligent assistant for help, tips, and enhanced gaming experience.")
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão de ação
        button_frame = tk.Frame(new_window, bg=THEME['BG_MAIN'])
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botão principal - Voltar ao Menu Principal
        action_btn = tk.Button(
            button_frame,
            text="🏠 Voltar ao Menu Principal",
            font=("Segoe UI", 12, "bold"),
            fg="#000000",
            bg=THEME['GOLD'],
            activebackground=THEME['BG_PANEL'],
            activeforeground="#FFFFFF",
            border=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=new_window.destroy
        )
        action_btn.pack(side="right")
        
        # Botão secundário - Ver Changelog Completo
        docs_btn = tk.Button(
            button_frame,
            text="📚 Ver Changelog Completo",
            font=("Segoe UI", 10),
            fg="#FFFFFF",
            bg=THEME['BG_PANEL'],
            activebackground=THEME['GOLD'],
            activeforeground="#000000",
            border=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: show_full_changelog(version_data)
        )
        docs_btn.pack(side="right", padx=(0, 10))
        
        # Efeito de entrada
        new_window.attributes('-alpha', 0.0)
        fade_in(new_window)
    
    # Executar na thread principal
    if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
        root.after(0, create_whats_new)

def create_category_section(parent, title, items, color):
    """Criar seção de categoria de mudanças"""
    
    # Frame da categoria
    category_frame = tk.Frame(parent, bg=THEME['BG_MAIN'])
    category_frame.pack(fill="x", pady=(0, 20))
    
    # Header da categoria
    header_frame = tk.Frame(category_frame, bg=color, height=3)
    header_frame.pack(fill="x")
    
    title_frame = tk.Frame(category_frame, bg=THEME['BG_PANEL'])
    title_frame.pack(fill="x")
    
    title_label = tk.Label(
        title_frame,
        text=title,
        font=("Segoe UI", 12, "bold"),
        fg="#FFFFFF",
        bg=THEME['BG_PANEL'],
        anchor="w"
    )
    title_label.pack(fill="x", padx=15, pady=8)
    
    # Lista de itens
    items_frame = tk.Frame(category_frame, bg=THEME['SHADOW'])
    items_frame.pack(fill="x")
    
    for i, item in enumerate(items):
        item_frame = tk.Frame(items_frame, bg=THEME['SHADOW'])
        item_frame.pack(fill="x", padx=10, pady=5)
        
        # Bullet point
        bullet_label = tk.Label(
            item_frame,
            text="•",
            font=("Segoe UI", 12, "bold"),
            fg=color,
            bg=THEME['SHADOW'],
            anchor="w"
        )
        bullet_label.pack(side="left", padx=(5, 10))
        
        # Texto do item
        item_label = tk.Label(
            item_frame,
            text=str(item),
            font=("Segoe UI", 10),
            fg="#FFFFFF",
            bg=THEME['SHADOW'],
            anchor="w",
            wraplength=500,
            justify="left"
        )
        item_label.pack(side="left", fill="x", expand=True)

def create_highlight_section(parent, title, description):
    """Criar seção de destaque especial"""
    
    highlight_frame = tk.Frame(parent, bg="#1A4A5C", relief="solid", bd=1)
    highlight_frame.pack(fill="x", pady=(0, 20))
    
    # Header especial
    header_label = tk.Label(
        highlight_frame,
        text=title,
        font=("Segoe UI", 14, "bold"),
        fg="#FFD700",
        bg="#1A4A5C"
    )
    header_label.pack(pady=(15, 5))
    
    # Descrição
    desc_label = tk.Label(
        highlight_frame,
        text=description,
        font=("Segoe UI", 10),
        fg="#E0E0E0",
        bg="#1A4A5C",
        wraplength=550,
        justify="center"
    )
    desc_label.pack(padx=20, pady=(0, 15))

def create_info_section(parent, title, items):
    """Criar seção de informações (para patches)"""
    
    info_frame = tk.Frame(parent, bg=THEME['BG_MAIN'])
    info_frame.pack(fill="x", pady=(0, 15))
    
    # Título da seção
    title_label = tk.Label(
        info_frame,
        text=title,
        font=("Segoe UI", 11, "bold"),
        fg="#FFD700",
        bg=THEME['BG_MAIN'],
        anchor="w"
    )
    title_label.pack(fill="x", pady=(0, 5))
    
    # Lista de itens em linha
    items_text = " • ".join(items) if isinstance(items, list) else str(items)
    items_label = tk.Label(
        info_frame,
        text=items_text,
        font=("Segoe UI", 10),
        fg="#CCCCCC",
        bg=THEME['BG_MAIN'],
        anchor="w",
        wraplength=550,
        justify="left"
    )
    items_label.pack(fill="x", padx=10)

def show_full_changelog(version_data):
    """Mostrar changelog completo em nova janela"""
    
    changelog_window = tk.Toplevel()
    changelog_window.title(f"📋 Full Changelog - v{CURRENT_VERSION}")
    changelog_window.geometry("400x500")
    changelog_window.configure(bg=THEME['BG_MAIN'])
    
    # Text widget com scroll
    text_frame = tk.Frame(changelog_window, bg=THEME['BG_MAIN'])
    text_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    text_widget = tk.Text(
        text_frame,
        bg=THEME['BG_PANEL'],
        fg="#FFFFFF",
        font=("Consolas", 10),
        wrap="word",
        padx=15,
        pady=15
    )
    
    scroll = tk.Scrollbar(text_frame, command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll.set)
    
    # Inserir changelog completo
    full_changelog = json.dumps(version_data, indent=2, ensure_ascii=False)
    text_widget.insert("1.0", full_changelog)
    text_widget.config(state="disabled")
    
    text_widget.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

def fade_in(window, alpha=0.0):
    """Efeito de fade-in na janela"""
    alpha += 0.05
    window.attributes('-alpha', alpha)
    if alpha < 1.0:
        window.after(20, lambda: fade_in(window, alpha))

def check_and_show_whats_new():
    """Verificar se deve mostrar What's New após atualização"""
    global root
    try:
        # Verificar versão anterior
        last_version = "0.0"
        if os.path.exists(LAST_VERSION_FILE):
            with open(LAST_VERSION_FILE, "r") as f:
                last_version = f.read().strip()
        
        # Se versão mudou, mostrar What's New
        if last_version != CURRENT_VERSION:
            # Buscar dados da versão atual
            try:
                server_url = get_update_server_url()
                url = f"{server_url}/version.json"
                with urllib.request.urlopen(url, timeout=5) as response:
                    version_data = json.loads(response.read().decode())
                    
                # Mostrar What's New após delay
                if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                    root.after(2000, lambda: show_whats_new_window(version_data))
                
            except Exception as e:
                print(f"Erro ao buscar dados da versão: {e}")
                # Mostrar versão padrão se falhar
                default_data = {
                    "version": CURRENT_VERSION,
                    "changelog": {
                        "new_features": [
                            "🎨 Sistema de temas personalizáveis com 5 presets incluídos",
                            "🔄 Sistema inteligente de atualizações com escolha do usuário",
                            "⚙️ Página de configurações reorganizada com abas (Temas/Updates)",
                            "� Interface simplificada e mais limpa",
                            "📏 Padronização de janelas para 400x500 pixels"
                        ],
                        "improvements": [
                            "🚫 Botão de updates removido da página inicial (movido para configurações)",
                            "🔕 Texto 'Connected to GitHub' removido da interface principal",
                            "💡 Notificação discreta de atualizações disponíveis na tela inicial",
                            "🎨 Sistema de cores mais flexível e personalizável",
                            "📱 Interface mais consistente e organizada"
                        ],
                        "ui_changes": [
                            "🎨 Adicionados 5 temas predefinidos (Default, Dark Blue, Purple Night, Forest Green, Crimson Red)",
                            "⚙️ Configurações reorganizadas em sistema de abas simples",
                            "� Updates movidos para aba dedicada nas configurações",
                            "📐 Todas as janelas principais padronizadas para 400x500",
                            "🧹 Interface principal mais limpa e focada"
                        ],
                        "technical": [
                            "� Sistema de gestão de temas com JSON persistence",
                            "� Melhorado sistema de verificação de atualizações",
                            "💾 Controle de estado global para atualizações pendentes",
                            "🏗️ Código reorganizado para melhor manutenibilidade"
                        ]
                    }
                }
                if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                    root.after(2000, lambda: show_whats_new_window(default_data))
            
            # Salvar versão atual
            with open(LAST_VERSION_FILE, "w") as f:
                f.write(CURRENT_VERSION)
                
    except Exception as e:
        print(f"Erro ao verificar What's New: {e}")

def load_update_config():
    """Carregar configuração de updates"""
    try:
        config_path = UPDATE_CONFIG_FILE
        # Fallback para arquivo local se não existir em APPDATA
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_config.json")
        
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load update config: {e}")
    
    # Configuração padrão
    return {
        "server_config": {
            "primary_server": "http://localhost:8080",
            "timeout_seconds": 10
        }
    }

def get_update_server_url():
    """Obter URL do servidor de updates"""
    config = load_update_config()
    return config.get("server_config", {}).get("primary_server", "http://localhost:8080")

def check_for_updates():
    """Verificar se há atualizações disponíveis no servidor"""
    def check_updates_thread():
        global root
        try:
            # Mostrar mensagem de verificação
            if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                root.after(0, lambda: messagebox.showinfo(
                    "Agent Update Check", 
                    "🔍 Connecting to update server...\nVerifying latest intelligence..."
                ))
            
            # Obter URL do servidor da configuração
            server_url = get_update_server_url()
            config = load_update_config()
            timeout = config.get("server_config", {}).get("timeout_seconds", 10)
            
            # Fazer requisição ao servidor
            url = f"{server_url}/version.json"
            with urllib.request.urlopen(url, timeout=timeout) as response:
                server_data = json.loads(response.read().decode('utf-8'))
            
            server_version = server_data.get("version", "1.0")
            changelog = server_data.get("changelog", "No changelog available")
            download_url = server_data.get("download_url", "")
            force_update = server_data.get("force_update", False)
            features = server_data.get("features", [])
            
            # Comparar versões (versão simples)
            if server_version != CURRENT_VERSION:
                # Nova versão disponível
                if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                    root.after(0, lambda: show_update_dialog(server_version, changelog, download_url, force_update, features))
            else:
                # Já está na versão mais recente
                if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                    root.after(0, lambda: messagebox.showinfo(
                        "Agent Update Status", 
                        f"✅ Agent system is up to date!\n\nCurrent Version: {CURRENT_VERSION}\nServer: {server_url}\nStatus: OPERATIONAL"
                    ))
                    
        except urllib.error.URLError as e:
            # Servidor não acessível
            if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                root.after(0, lambda: messagebox.showwarning(
                    "Agent Update Check", 
                    f"⚠️ Unable to connect to update server\n\nServer: {server_url}\nError: {str(e)}\n\nPossible causes:\n• Update server offline\n• Network connectivity issues\n• Firewall blocking connection"
                ))
        except Exception as e:
            # Outro erro
            if 'root' in globals() and hasattr(root, 'winfo_exists') and root.winfo_exists():
                root.after(0, lambda: messagebox.showerror(
                    "Agent Update Error", 
                    f"❌ Error checking for updates:\n{str(e)}"
                ))
    
    # Executar verificação em thread separada
    update_thread = threading.Thread(target=check_updates_thread, daemon=True)
    update_thread.start()

def show_update_dialog(version, changelog, download_url, force_update, features=None):
    """Mostrar diálogo com informações da atualização"""
    update_type = "🚨 CRITICAL UPDATE REQUIRED" if force_update else "🆕 NEW VERSION AVAILABLE"
    
    features_text = ""
    if features:
        features_text = f"\n\n✨ New Features:\n" + "\n".join([f"• {feature}" for feature in features[:5]])
    
    msg = f"""{update_type}

📊 Current Version: {CURRENT_VERSION}
🚀 Latest Version: {version}

📋 What's New:
{changelog[:200]}{'...' if len(changelog) > 200 else ''}{features_text}

🔗 Download: {download_url}

Would you like to open the download link?"""
    
    result = messagebox.askyesno("Agent System Update", msg)
    
    if result:
        try:
            # Abrir link de download
            import webbrowser
            webbrowser.open(download_url)
        except Exception as e:
            messagebox.showerror("Agent Update Error", f"Failed to open download link:\n{str(e)}")

def apply_theme_to_widget(widget):
    # Try to set standard keys, if available. Used in recursive walk for settings.
    bg = THEME["BG_MAIN"]
    fg = THEME["GOLD"]
    try:
        if isinstance(widget, tk.Frame):
            widget.configure(bg=bg)
        else:
            if "bg" in widget.keys():
                widget.configure(bg=bg)
            if "fg" in widget.keys():
                widget.configure(fg=fg)
    except Exception:
        pass
    # Recursively apply to children
    for child in widget.winfo_children():
        try:
            apply_theme_to_widget(child)
        except Exception:
            continue

def refresh_all_theme():
    # Call this after THEME changes, to update live app colors
    try:
        root.configure(bg=THEME["BG_MAIN"])
    except Exception:
        pass
    for obj in [root, getattr(root, "main_panel_frame", None), getattr(root, "games_submenu", None)]:
        if obj:
            apply_theme_to_widget(obj)
    # Re-render main panels for full effect if present
    if hasattr(root, "show_main_menu_needed") and root.show_main_menu_needed:
        show_main_menu_panel()

# Custom button: secret agent style
class AgentButton(tk.Frame):
    def __init__(self, master, text, command, emoji, bg=None, fg=None, activebackground=None, outline=None, **kwargs):
        super().__init__(master, bg=THEME["BG_MAIN"])
        if bg is None: bg = THEME["BG_PANEL"]
        if fg is None: fg = THEME["GOLD"]
        if activebackground is None: activebackground = THEME["SHADOW"]
        if outline is None: outline = THEME["BTN_OUTLINE"]
        self.command = command
        self.configure(bg=THEME["BG_MAIN"])
        self.button = tk.Button(
            self,
            text=f"{emoji}  {text}",
            font=("Segoe UI Semibold", 13, "bold"),
            bg=bg,
            fg=fg,
            activebackground=activebackground,
            activeforeground=THEME["GOLD"],
            bd=0,
            padx=16, pady=7,
            justify="center",
            highlightthickness=2,
            highlightbackground=outline,
            highlightcolor=outline,
            cursor="hand2",
            **kwargs
        )
        self.button.pack(fill='x')
        self.button.bind("<Enter>", lambda e: self.button.configure(bg=activebackground))
        self.button.bind("<Leave>", lambda e: self.button.configure(bg=bg))
        self.button.config(command=self.command)

# --- Small settings (⚙️) button and Settings Dialog ---
class SettingsButton(tk.Button):
    def __init__(self, master, **kwargs):
        tk.Button.__init__(
            self,
            master,
            text="⚙️",
            font=("Segoe UI", 9, "bold"),
            width=2, height=1,
            relief="flat",
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            activebackground=THEME["SHADOW"],
            activeforeground=THEME["GOLD"],
            highlightthickness=1, highlightbackground=THEME["BTN_OUTLINE"],
            cursor="hand2",
            command=self.show_settings,
            **kwargs
        )

    def show_settings(self):
        # Small toplevel settings window
        SettingsDialog(root)

class SettingsDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x500")
        self.grab_set()
        self.resizable(False, False)
        self.configure(bg=THEME["BG_MAIN"])
        
        # Center the window
        self.transient(master)
        
        # Create tabs system
        self.create_tabs()
        
    def create_tabs(self):
        """Cria o sistema de abas simplificado"""
        # Header
        header = tk.Label(
            self,
            text="⚙️ Configurações",
            font=("Segoe UI Black", 12, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            pady=8
        )
        header.pack()
        
        # Tab buttons
        tab_frame = tk.Frame(self, bg=THEME["BG_MAIN"])
        tab_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.active_tab = "themes"
        
        self.btn_themes = tk.Button(
            tab_frame,
            text="🎨 Temas",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=6,
            command=lambda: self.switch_tab("themes")
        )
        self.btn_themes.pack(side="left", padx=2)
        
        self.btn_updates = tk.Button(
            tab_frame,
            text="🔄 Updates",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["BG_MAIN"],
            fg=THEME["GOLD"],
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=6,
            command=lambda: self.switch_tab("updates")
        )
        self.btn_updates.pack(side="left", padx=2)
        
        # Content frame
        self.content_frame = tk.Frame(self, bg=THEME["BG_MAIN"])
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Close button
        close_frame = tk.Frame(self, bg=THEME["BG_MAIN"])
        close_frame.pack(side="bottom", pady=8)
        
        tk.Button(
            close_frame,
            text="Fechar",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["EXIT_BG"],
            fg=THEME["GOLD"],
            cursor="hand2",
            padx=15,
            pady=4,
            relief="flat",
            command=self.on_close
        ).pack()
        
        # Show initial tab
        self.switch_tab("themes")
    
    def switch_tab(self, tab_name):
        """Muda de aba"""
        self.active_tab = tab_name
        
        # Update tab buttons
        if tab_name == "themes":
            self.btn_themes.configure(bg=THEME["BG_PANEL"])
            self.btn_updates.configure(bg=THEME["BG_MAIN"])
        else:
            self.btn_themes.configure(bg=THEME["BG_MAIN"])
            self.btn_updates.configure(bg=THEME["BG_PANEL"])
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show content
        if tab_name == "themes":
            self.create_themes_content()
        else:
            self.create_updates_content()
    
    def create_themes_content(self):
        """Cria o conteúdo da aba de temas"""
        # Load all themes
        all_themes = load_custom_themes()
        
        # Preset buttons in a compact grid
        presets_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        presets_frame.pack(fill="x", pady=(5, 10))
        
        tk.Label(
            presets_frame,
            text="Temas Disponíveis:",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"]
        ).pack(anchor="w", pady=(0, 5))
        
        # Grid of theme buttons
        themes_grid = tk.Frame(presets_frame, bg=THEME["BG_MAIN"])
        themes_grid.pack(fill="x")
        
        row = 0
        col = 0
        for theme_name in all_themes.keys():
            btn = tk.Button(
                themes_grid,
                text=theme_name,
                font=("Segoe UI", 9),
                bg=THEME["BG_PANEL"],
                fg=THEME["GOLD"],
                cursor="hand2",
                padx=10,
                pady=3,
                relief="flat",
                command=lambda name=theme_name: self.apply_theme(name)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            col += 1
            if col > 3:  # 4 columns
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(4):
            themes_grid.grid_columnconfigure(i, weight=1)
        
        # Separator
        separator = tk.Frame(self.content_frame, height=1, bg=THEME["SHADOW"])
        separator.pack(fill="x", pady=8)
        
        # Custom colors section
        colors_label = tk.Label(
            self.content_frame,
            text="Personalizar:",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"]
        )
        colors_label.pack(anchor="w", pady=(0, 5))
        
        # Color options in a compact layout
        color_options = [
            ("Fundo", "BG_MAIN"),
            ("Painel", "BG_PANEL"),
            ("Destaque", "GOLD"),
            ("Sombra", "SHADOW"),
        ]
        
        self.color_vars = {}
        colors_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        colors_frame.pack(fill="x", pady=(0, 8))
        
        for i, (label, key) in enumerate(color_options):
            row_frame = tk.Frame(colors_frame, bg=THEME["BG_MAIN"])
            row_frame.grid(row=i//2, column=i%2, sticky="ew", padx=3, pady=1)
            
            tk.Label(
                row_frame,
                text=f"{label}:",
                font=("Segoe UI", 9),
                bg=THEME["BG_MAIN"],
                fg=THEME["GOLD"],
                width=7,
                anchor="w"
            ).pack(side="left")
            
            # Color preview
            self.color_vars[key] = tk.StringVar(value=THEME[key])
            color_box = tk.Label(
                row_frame,
                width=2,
                bg=THEME[key],
                relief="groove",
                borderwidth=1
            )
            color_box.pack(side="left", padx=2)
            
            # Color picker button
            tk.Button(
                row_frame,
                text="▶",
                font=("Segoe UI", 7),
                bg=THEME["BG_PANEL"],
                fg=THEME["GOLD"],
                relief="flat",
                cursor="hand2",
                width=2,
                command=lambda k=key, cb=color_box: self.pick_custom_color(k, cb)
            ).pack(side="left", padx=1)
        
        # Configure grid weights for colors
        colors_frame.grid_columnconfigure(0, weight=1)
        colors_frame.grid_columnconfigure(1, weight=1)
        
        # Theme name and buttons
        bottom_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        bottom_frame.pack(fill="x", pady=(5, 0))
        
        # Theme name entry
        name_frame = tk.Frame(bottom_frame, bg=THEME["BG_MAIN"])
        name_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(
            name_frame,
            text="Nome:",
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"]
        ).pack(side="left")
        
        self.theme_name_var = tk.StringVar()
        tk.Entry(
            name_frame,
            textvariable=self.theme_name_var,
            font=("Segoe UI", 9),
            width=12
        ).pack(side="right")
        
        # Buttons
        buttons_frame = tk.Frame(bottom_frame, bg=THEME["BG_MAIN"])
        buttons_frame.pack(fill="x")
        
        tk.Button(
            buttons_frame,
            text="Aplicar",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            cursor="hand2",
            padx=12,
            pady=3,
            relief="flat",
            command=self.apply_current_colors
        ).pack(side="left", padx=2)
        
        tk.Button(
            buttons_frame,
            text="Salvar",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            cursor="hand2",
            padx=12,
            pady=3,
            relief="flat",
            command=self.create_custom_theme
        ).pack(side="left", padx=2)
    
    def create_updates_content(self):
        """Cria o conteúdo da aba de updates"""
        # Current version info
        info_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        info_frame.pack(fill="x", pady=(5, 10))
        
        tk.Label(
            info_frame,
            text=f"Versão Atual: {CURRENT_VERSION} | Patch: {CURRENT_PATCH}",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"]
        ).pack()
        
        # Auto-update configuration section
        auto_update_frame = tk.LabelFrame(
            self.content_frame,
            text=" Configurações de Auto-Update ",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            bd=1,
            relief="solid"
        )
        auto_update_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Auto-update options
        options_frame = tk.Frame(auto_update_frame, bg=THEME["BG_MAIN"])
        options_frame.pack(fill="x", padx=10, pady=8)
        
        # Load current config
        config = load_auto_update_config()
        
        # Variables for checkboxes
        self.auto_enabled = tk.BooleanVar(value=config.get("enabled", True))
        self.check_startup = tk.BooleanVar(value=config.get("check_on_startup", True))
        self.auto_patches = tk.BooleanVar(value=config.get("auto_install_patches", False))
        self.auto_minor = tk.BooleanVar(value=config.get("auto_install_minor", False))
        self.silent_mode = tk.BooleanVar(value=config.get("silent_mode", False))
        
        # Checkboxes
        tk.Checkbutton(
            options_frame,
            text="✅ Ativar sistema de auto-update",
            variable=self.auto_enabled,
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            activebackground=THEME["BG_MAIN"],
            activeforeground=THEME["GOLD"],
            command=self.save_auto_update_config
        ).pack(anchor="w", pady=2)
        
        tk.Checkbutton(
            options_frame,
            text="🚀 Verificar updates no início do programa",
            variable=self.check_startup,
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            activebackground=THEME["BG_MAIN"],
            activeforeground=THEME["GOLD"],
            command=self.save_auto_update_config
        ).pack(anchor="w", pady=2)
        
        tk.Checkbutton(
            options_frame,
            text="🔧 Instalar patches automaticamente",
            variable=self.auto_patches,
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            activebackground=THEME["BG_MAIN"],
            activeforeground=THEME["GOLD"],
            command=self.save_auto_update_config
        ).pack(anchor="w", pady=2)
        
        tk.Checkbutton(
            options_frame,
            text="🔄 Instalar updates menores automaticamente",
            variable=self.auto_minor,
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            activebackground=THEME["BG_MAIN"],
            activeforeground=THEME["GOLD"],
            command=self.save_auto_update_config
        ).pack(anchor="w", pady=2)
        
        tk.Checkbutton(
            options_frame,
            text="🔇 Modo silencioso (sem notificações)",
            variable=self.silent_mode,
            font=("Segoe UI", 9),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            selectcolor=THEME["BG_PANEL"],
            activebackground=THEME["BG_MAIN"],
            activeforeground=THEME["GOLD"],
            command=self.save_auto_update_config
        ).pack(anchor="w", pady=2)
        
        # Check updates button
        check_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        check_frame.pack(pady=10)
        
        self.check_btn = tk.Button(
            check_frame,
            text="🔍 Verificar Atualizações",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            cursor="hand2",
            padx=20,
            pady=6,
            relief="flat",
            command=self.check_updates_manual
        )
        self.check_btn.pack()
        
        # Results area
        self.updates_text = tk.Text(
            self.content_frame,
            height=10,
            width=50,
            font=("Segoe UI", 9),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            insertbackground=THEME["GOLD"],
            selectbackground=THEME["SHADOW"],
            relief="flat",
            wrap=tk.WORD
        )
        self.updates_text.pack(fill="both", expand=True, pady=(10, 5))
        
        # Initial message
        self.updates_text.insert("1.0", "Clique em 'Verificar Atualizações' para buscar por novas versões...")
        
        # Revert button frame
        revert_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
        revert_frame.pack(pady=(5, 0))
        
        # Separator line
        separator = tk.Frame(revert_frame, height=1, bg=THEME["SHADOW"])
        separator.pack(fill="x", pady=(0, 8))
        
        # Revert button
        self.revert_btn = tk.Button(
            revert_frame,
            text="⬅️ Reverter para Versão Anterior",
            font=("Segoe UI", 9, "bold"),
            bg="#d63031",
            fg="white",
            cursor="hand2",
            padx=15,
            pady=5,
            relief="flat",
            command=self.revert_to_previous_version
        )
        self.revert_btn.pack()
        
        # Warning label
        tk.Label(
            revert_frame,
            text="⚠️ Isto irá remover funcionalidades da versão atual",
            font=("Segoe UI", 8),
            fg="#ff7675",
            bg=THEME["BG_MAIN"]
        ).pack(pady=(2, 0))
    
    def check_updates_manual(self):
        """Verifica atualizações manualmente"""
        self.check_btn.configure(state="disabled", text="Verificando...")
        self.updates_text.delete("1.0", tk.END)
        self.updates_text.insert("1.0", "🔍 Verificando atualizações...\n\n")
        self.update()
        
        try:
            # Check GitHub updates
            has_update, update_info, data = check_github_updates()
            
            if has_update:
                self.updates_text.insert(tk.END, "✅ ATUALIZAÇÕES DISPONÍVEIS!\n\n")
                
                for update in update_info:
                    if update['type'] == 'major':
                        self.updates_text.insert(tk.END, f"🚀 Nova Versão: {update['version']}\n")
                        self.updates_text.insert(tk.END, f"   (Atual: {update['current']})\n\n")
                    elif update['type'] == 'patch':
                        self.updates_text.insert(tk.END, f"🔧 Novo Patch: {update['version']}\n")
                        self.updates_text.insert(tk.END, f"   (Atual: {update['current']})\n\n")
                    
                    if update.get('changes'):
                        self.updates_text.insert(tk.END, "📋 Mudanças:\n")
                        for change in update['changes'][:3]:  # Show first 3 changes
                            self.updates_text.insert(tk.END, f"  • {change}\n")
                        self.updates_text.insert(tk.END, "\n")
                
                # Add download button if URL available
                if update_info and update_info[0].get('url'):
                    download_frame = tk.Frame(self.content_frame, bg=THEME["BG_MAIN"])
                    download_frame.pack(pady=5)
                    
                    tk.Button(
                        download_frame,
                        text="📥 Baixar Atualização",
                        font=("Segoe UI", 9, "bold"),
                        bg=THEME["GOLD"],
                        fg=THEME["BG_MAIN"],
                        cursor="hand2",
                        padx=15,
                        pady=4,
                        relief="flat",
                        command=lambda: self.download_update(update_info[0])
                    ).pack()
                
            else:
                self.updates_text.insert(tk.END, "✅ Você está usando a versão mais recente!\n\n")
                self.updates_text.insert(tk.END, f"Versão: {CURRENT_VERSION}\n")
                self.updates_text.insert(tk.END, f"Patch: {CURRENT_PATCH}\n")
        
        except Exception as e:
            self.updates_text.insert(tk.END, f"❌ Erro ao verificar atualizações:\n{str(e)}")
        
        finally:
            self.check_btn.configure(state="normal", text="🔍 Verificar Atualizações")
    
    def download_update(self, update_info):
        """Inicia o download da atualização"""
        try:
            url = update_info.get('url', '')
            if url:
                webbrowser.open(url)
                messagebox.showinfo(
                    "Download Iniciado",
                    "O download foi iniciado no seu navegador."
                )
            else:
                messagebox.showerror("Erro", "URL de download não encontrada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir download:\n{str(e)}")
    
    def save_auto_update_config(self):
        """Salva as configurações de auto-update"""
        config = {
            "enabled": self.auto_enabled.get(),
            "check_on_startup": self.check_startup.get(),
            "auto_install_patches": self.auto_patches.get(),
            "auto_install_minor": self.auto_minor.get(),
            "silent_mode": self.silent_mode.get(),
            "check_interval": 24,  # horas
            "last_check": "",
            "skipped_version": ""
        }
        
        try:
            with open("auto_update_config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações de auto-update: {e}")
    
    def revert_to_previous_version(self):
        """Reverte para a versão anterior"""
        # Definir versões disponíveis para reversão
        version_history = {
            "1.4": "1.3",
            "1.3": "1.2", 
            "1.2": "1.1",
            "1.1": "1.0"
        }
        
        previous_version = version_history.get(CURRENT_VERSION)
        
        if not previous_version:
            messagebox.showwarning(
                "Reversão Indisponível",
                "Não há versão anterior disponível para reversão."
            )
            return
        
        # Confirmar reversão
        result = messagebox.askyesno(
            "⚠️ Confirmar Reversão",
            f"Tem certeza que deseja reverter?\n\n"
            f"Versão atual: v{CURRENT_VERSION}\n"
            f"Reverter para: v{previous_version}\n\n"
            f"ATENÇÃO:\n"
            f"• Algumas funcionalidades podem ser perdidas\n"
            f"• Configurações personalizadas serão mantidas\n"
            f"• Esta ação pode ser desfeita atualizando novamente\n\n"
            f"Deseja continuar?",
            icon="warning"
        )
        
        if result:
            try:
                # Simular processo de reversão
                self.revert_btn.configure(state="disabled", text="Revertendo...")
                self.update()
                
                # Aqui você implementaria a lógica real de reversão
                # Por agora, vamos simular com uma mensagem
                
                import time
                time.sleep(2)  # Simular processo
                
                messagebox.showinfo(
                    "Reversão Simulada",
                    f"SIMULAÇÃO: Reversão para v{previous_version}\n\n"
                    f"Em uma implementação real, isto:\n"
                    f"• Baixaria os arquivos da v{previous_version}\n"
                    f"• Substituiria os arquivos atuais\n"
                    f"• Reiniciaria a aplicação\n\n"
                    f"Para implementação completa, seria necessário:\n"
                    f"• Sistema de backup de versões\n"
                    f"• Script de instalação/reversão\n"
                    f"• Controle de dependências"
                )
                
            except Exception as e:
                messagebox.showerror("Erro na Reversão", f"Erro durante a reversão:\n{str(e)}")
            
            finally:
                self.revert_btn.configure(state="normal", text="⬅️ Reverter para Versão Anterior")
    
    def apply_theme(self, theme_name):
        """Aplica um tema específico"""
        if apply_theme(theme_name):
            messagebox.showinfo("Sucesso", f"Tema '{theme_name}' aplicado!")
            refresh_all_theme()
            self.destroy()
        else:
            messagebox.showerror("Erro", f"Erro ao aplicar tema '{theme_name}'")
    
    def pick_custom_color(self, key, color_box):
        """Escolhe uma cor personalizada"""
        initial = self.color_vars[key].get()
        color_tuple = colorchooser.askcolor(title="Selecionar cor", color=initial)
        if color_tuple and color_tuple[1]:
            self.color_vars[key].set(color_tuple[1])
            color_box.configure(bg=color_tuple[1])
    
    def create_custom_theme(self):
        """Cria um tema personalizado"""
        theme_name = self.theme_name_var.get().strip()
        if not theme_name:
            messagebox.showerror("Erro", "Digite um nome para o tema.")
            return
        
        # Build theme data with all required keys
        theme_data = {}
        for key in THEME.keys():
            if key in self.color_vars:
                theme_data[key] = self.color_vars[key].get()
            else:
                theme_data[key] = THEME[key]  # Keep current value for missing keys
        
        # Save theme
        if save_custom_theme(theme_name, theme_data):
            messagebox.showinfo("Sucesso", f"Tema '{theme_name}' salvo!")
            self.switch_tab("themes")  # Refresh themes tab
        else:
            messagebox.showerror("Erro", "Erro ao salvar o tema.")
    
    def apply_current_colors(self):
        """Aplica as cores atuais como tema temporário"""
        for key in self.color_vars:
            THEME[key] = self.color_vars[key].get()
        refresh_all_theme()
        messagebox.showinfo("Aplicado", "Cores aplicadas!")

    def on_close(self):
        save_theme()
        refresh_all_theme()
        self.destroy()

# --- GAMES SUBMENU: Add/Remove/Run Games Dynamically ---
class GamesSubMenu(tk.Frame):
    def __init__(self, master, on_back, **kwargs):
        super().__init__(master, bg=THEME["BG_MAIN"], **kwargs)
        self.on_back = on_back
        self.games_buttons = []
        self.plus_button = None
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self.games_buttons.clear()
        # --- Subtitle/Header ---
        subtitle = tk.Label(
            self,
            text="🎮   GAMES DATABASE",
            font=("Segoe UI Black", 16, "bold"),
            fg=THEME["GOLD"],
            bg=THEME["BG_MAIN"],
            pady=12,
        )
        subtitle.pack()
        # --- Game Buttons --- (now within a scrollable frame)
        games_frame_container = tk.Frame(self, bg=THEME["BG_MAIN"])
        games_frame_container.pack(expand=True, fill="both", padx=5)
        canvas = tk.Canvas(
            games_frame_container,
            bg=THEME["BG_MAIN"],
            highlightthickness=0,
            borderwidth=0
        )
        scrollbar = tk.Scrollbar(
            games_frame_container,
            orient="vertical",
            command=canvas.yview
        )
        self.games_frame = tk.Frame(canvas, bg=THEME["BG_MAIN"])
        self.games_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.games_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Windows mousewheel support for scrolling inside the games menu
        def _on_mousewheel(event):
            if canvas.winfo_height() < self.games_frame.winfo_height():
                canvas.yview_scroll(-1 * int(event.delta/120), "units")

        # Linux/Mac support for scrolling
        def _on_linux_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_linux_mousewheel)
        canvas.bind_all("<Button-5>", _on_linux_mousewheel)

        # --- Random Game Button ---
        random_frame = tk.Frame(self.games_frame, bg=THEME["BG_MAIN"])
        random_frame.grid(row=0, column=0, columnspan=2, pady=(7, 0), sticky="ew")
        def launch_random_game():
            if not GAMES_LIST:
                messagebox.showinfo("No Games", "No games available!")
                return
            game = random.choice(GAMES_LIST)
            # Optionally show info:
            response = messagebox.askokcancel(
                "Random Game",
                f"Randomly selected:\n\n{game.get('emoji','🎮')}  {game.get('name','(Unnamed)')}\n\nLaunch it?"
            )
            if response:
                self.launch_game(game)
        random_btn = tk.Button(
            random_frame,
            text="🎲  Launch Random Game",
            font=("Segoe UI Semibold", 12, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            activebackground=THEME["SHADOW"],
            activeforeground=THEME["GOLD"],
            highlightthickness=2,
            highlightbackground=THEME["BTN_OUTLINE"],
            highlightcolor=THEME["BTN_OUTLINE"],
            bd=0,
            padx=4, pady=4,
            cursor="hand2",
            command=launch_random_game
        )
        random_btn.pack(fill="x")

        # --- Make game buttons in 2 columns ---
        num_cols = 2
        row_start = 1  # Games start from row 1 due to random_frame in row 0
        col = 0
        row = row_start
        for idx, game in enumerate(GAMES_LIST):
            btn = AgentButton(
                self.games_frame,
                text=game["name"],
                command=lambda g=game: self.launch_game(g),
                emoji=game.get("emoji", "🎮"),
                bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
                activebackground=THEME["SHADOW"],
                outline=THEME["BTN_OUTLINE"],
            )
            btn.grid(row=row, column=col, padx=6, pady=8, sticky="ew")
            if game.get("key", "") not in ("rocket_league", "gta_v"):
                btn.button.bind("<Button-3>", lambda e, k=game["key"]: self.show_remove_menu(e, k))
            self.games_buttons.append(btn)
            col += 1
            if col >= num_cols:
                col = 0
                row += 1

        # --- Add Plus Button: next open column (always on its own row, spans cols if needed) ---
        plus_row = row + 1 if col != 0 else row
        
        # Botão Add Game
        self.plus_button = tk.Button(
            self.games_frame,
            text="＋  Add Game",
            font=("Segoe UI Semibold", 12, "bold"),
            bg=THEME["BG_PANEL"],
            fg=THEME["GOLD"],
            activebackground=THEME["SHADOW"],
            activeforeground=THEME["GOLD"],
            highlightthickness=2,
            highlightbackground=THEME["BTN_OUTLINE"],
            highlightcolor=THEME["BTN_OUTLINE"],
            bd=0,
            padx=4, pady=4,
            cursor="hand2",
            command=self.add_game_dialog
        )
        self.plus_button.grid(row=plus_row, column=0, pady=(12,0), sticky="ew", padx=(0,3))

        # Botão Surprise Me (Jogo Aleatório)
        self.random_button = tk.Button(
            self.games_frame,
            text="🎲  Surprise Me",
            font=("Segoe UI Semibold", 12, "bold"),
            bg=THEME["BG_PANEL"],
            fg="#FF6B6B",  # Cor diferente para destacar
            activebackground=THEME["SHADOW"],
            activeforeground="#FF6B6B",
            highlightthickness=2,
            highlightbackground="#FF6B6B",
            highlightcolor="#FF6B6B",
            bd=0,
            padx=4, pady=4,
            cursor="hand2",
            command=self.run_random_game
        )
        self.random_button.grid(row=plus_row, column=1, pady=(12,0), sticky="ew", padx=(3,0))

        # --- Back Button: after plus button, on next row ---
        btn_back = AgentButton(
            self.games_frame,
            text="Back to Main Menu",
            command=self.on_back,
            emoji="⬅️",
            bg=THEME["EXIT_BG"], fg=THEME["GOLD"],
            activebackground=THEME["EXIT_ACTIVE"],
            outline=THEME["BTN_OUTLINE"]
        )
        btn_back.grid(row=plus_row+1, column=0, columnspan=2, pady=(18, 0), sticky="ew")

        # Expand columns equally
        self.games_frame.grid_columnconfigure(0, weight=1)
        self.games_frame.grid_columnconfigure(1, weight=1)

    def launch_game(self, game):
        """Lança jogo com performance otimizada e tratamento de erro melhorado"""
        perf_monitor.start_operation("launch_game")
        
        GAME_KEY = game["key"]
        DEFAULT_PATH = game.get("default_path", "")
        GAME_NAME = game["name"]

        def try_launch(exe_path, callback=None):
            try:
                if not sys.platform.startswith('win'):
                    messagebox.showerror(
                        "Plataforma não suportada",
                        f"Lançamento de {GAME_NAME} só é suportado no Windows."
                    )
                    if callback: callback(False)
                    return
                
                # Validação mais rigorosa do caminho
                if not exe_path or not os.path.isfile(exe_path):
                    print(f"Arquivo não encontrado: {exe_path}")
                    if callback: callback(False)
                    return
                
                # Verificar se é executável
                if not exe_path.lower().endswith('.exe'):
                    messagebox.showerror("Erro", "O arquivo selecionado não é um executável (.exe)")
                    if callback: callback(False)
                    return
                
                # Lançar o jogo de forma otimizada
                def launch_thread():
                    try:
                        # Usar subprocess.Popen para lançamento mais rápido
                        import subprocess
                        subprocess.Popen([exe_path], shell=True)
                        
                        # Notificação mais rápida
                        self.main_window.after(0, lambda: messagebox.showinfo(
                            "🎮 Jogo Lançado",
                            f"✅ {GAME_NAME} foi iniciado!\n🚀 Boa diversão!"
                        ))
                        if callback: 
                            self.main_window.after(0, lambda: callback(True))
                    except Exception as e:
                        # Fallback para os.startfile se subprocess falhar
                        try:
                            os.startfile(exe_path)
                            self.main_window.after(0, lambda: messagebox.showinfo(
                                "🎮 Jogo Lançado",
                                f"✅ {GAME_NAME} foi iniciado!\n🚀 Boa diversão!"
                            ))
                            if callback: 
                                self.main_window.after(0, lambda: callback(True))
                        except Exception as e2:
                            error_msg = f"Erro ao iniciar {GAME_NAME}:\n{str(e2)}"
                            print(error_msg)
                            self.main_window.after(0, lambda: messagebox.showerror("Erro de Lançamento", error_msg))
                            if callback: 
                                self.main_window.after(0, lambda: callback(False))
                
                # Executar em thread separada
                threading.Thread(target=launch_thread, daemon=True).start()
                
            except Exception as e:
                error_msg = f"Falha crítica ao lançar {GAME_NAME}: {str(e)}"
                print(error_msg)
                messagebox.showerror("Erro Crítico", error_msg)
                if callback: callback(False)
        
        # Tentar lançar o jogo automaticamente
        def ask_for_game_location():
            messagebox.showinfo(
                f"{GAME_NAME} Not Found",
                f"Unable to find {GAME_NAME} at the saved/default location.\n"
                f"Please locate {GAME_NAME} executable manually.\nThis path will be saved for next time."
            )
            file_path = filedialog.askopenfilename(
                title=f"Locate {GAME_NAME} Executable",
                filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
            )
            if file_path:
                set_game_path(GAME_KEY, file_path)
                try_launch(file_path)

        def launch_with_timeout():
            exe_path = get_game_path(GAME_KEY, DEFAULT_PATH)
            launched_flag = {"status": False}
            
            def launch_and_set_flag():
                if exe_path and os.path.exists(exe_path):
                    try_launch(exe_path, callback=lambda success: launched_flag.update({"status": success}))
                else:
                    launched_flag["status"] = False

            launch_thread = threading.Thread(target=launch_and_set_flag)
            launch_thread.start()
            launch_thread.join(timeout=10)

            if not launched_flag.get("status"):
                if self.winfo_exists():
                    self.after(100, ask_for_game_location)

        threading.Thread(target=launch_with_timeout).start()
        
        perf_monitor.end_operation("launch_game")

    def run_random_game(self):
        """Executa um jogo aleatório da lista"""
        try:
            paths = load_game_paths()
            available_games = []
            
            # Coletar todos os jogos configurados
            for game in GAMES_LIST:
                game_key = game["key"]
                if game_key in paths and paths[game_key]:
                    # Verificar se o arquivo ainda existe
                    game_path = paths[game_key]
                    if os.path.exists(game_path):
                        available_games.append(game)
            
            if not available_games:
                messagebox.showinfo(
                    "Surprise Me", 
                    "No games are currently configured or available!\nPlease add and configure some games first.",
                    parent=self
                )
                return
            
            # Selecionar jogo aleatório
            selected_game = random.choice(available_games)
            game_name = selected_game["name"]
            
            result = messagebox.askyesno(
                "Surprise Me 🎲",
                f"The randomly selected game is:\n\n'{game_name}'\n\nDo you want to launch it now?",
                parent=self
            )
            
            if result:
                self.launch_game(selected_game)
                
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Error selecting random game:\n{e}",
                parent=self
            )

    def add_game_dialog(self):
        # Dialog for adding a new game (name, emoji, exe path)
        add_win = tk.Toplevel(self)
        add_win.title("Add New Game")
        add_win.grab_set()
        add_win.configure(bg=THEME["BG_MAIN"])
        add_win.resizable(False, False)

        tk.Label(add_win, text="Game Name:", font=("Segoe UI", 11), fg=THEME["GOLD"], bg=THEME["BG_MAIN"]).pack(padx=8, pady=(7,1))
        name_entry = tk.Entry(add_win, font=("Segoe UI", 11), width=22)
        name_entry.pack(padx=8, pady=(0,8))

        tk.Label(add_win, text="Button Emoji (e.g. 🎲):", font=("Segoe UI", 11), fg=THEME["GOLD"], bg=THEME["BG_MAIN"]).pack(padx=8, pady=(0,1))
        emoji_entry = tk.Entry(add_win, font=("Segoe UI", 11), width=22)
        emoji_entry.pack(padx=8, pady=(0,8))

        exe_frame = tk.Frame(add_win, bg=THEME["BG_MAIN"])
        exe_frame.pack(fill="x", padx=8, pady=(0,10))
        tk.Label(exe_frame, text="Game Exe Location:", font=("Segoe UI", 11), fg=THEME["GOLD"], bg=THEME["BG_MAIN"]).pack(side="left")
        exe_var = tk.StringVar()
        exe_entry = tk.Entry(exe_frame, textvariable=exe_var, font=("Segoe UI", 10), width=26)
        exe_entry.pack(side="left", padx=(4,0))
        def browse_exe():
            p = filedialog.askopenfilename(title="Locate Game Executable", filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
            if p:
                exe_var.set(p)
        tk.Button(exe_frame, text="Browse", command=browse_exe, font=("Segoe UI", 9), 
                  bg=THEME["BG_PANEL"], fg=THEME["GOLD"], relief="flat", cursor="hand2").pack(side="left", padx=7)

        def on_add():
            name = name_entry.get().strip()
            emoji = emoji_entry.get().strip() or "🎲"
            exe_path = exe_var.get().strip()
            if not name or not exe_path:
                messagebox.showerror("Missing Info", "Please fill in the Game Name and pick a valid executable.")
                return
            # Generate a unique key
            key_base = name.lower().replace(" ", "_")
            key = key_base
            i = 2
            while any(g["key"] == key for g in GAMES_LIST):
                key = f"{key_base}_{i}"
                i += 1
            new_game = {
                "name": name,
                "emoji": emoji,
                "key": key,
                "default_path": exe_path
            }
            add_game_to_list(new_game)
            set_game_path(key, exe_path)
            self.rebuild()
            add_win.destroy()

        tk.Button(add_win, text="Add Game", command=on_add, font=("Segoe UI Semibold", 11),
                  bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
                  activebackground=THEME["SHADOW"],
                  padx=8, pady=2, cursor="hand2").pack(pady=(0,8))

    def show_remove_menu(self, event, game_key):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Remove Game", command=lambda: self.remove_game(game_key))
        menu.tk_popup(event.x_root, event.y_root)

    def remove_game(self, game_key):
        if messagebox.askokcancel("Remove Game", "Remove this game entry?"):
            remove_game_from_list(game_key)
            # Remove saved path too:
            if GAME_PATHS.get(game_key):
                del GAME_PATHS[game_key]
                save_game_paths(GAME_PATHS)
            self.rebuild()

def open_games():
    # Hide main menu panel and show games submenu
    if hasattr(root, 'main_panel_frame') and root.main_panel_frame:
        root.main_panel_frame.pack_forget()
    if hasattr(root, 'current_panel') and root.current_panel:
        root.current_panel.pack_forget()

    root.games_submenu = GamesSubMenu(
        root,
        on_back=show_main_menu_panel,
    )
    root.games_submenu.pack(expand=True, fill="both")
    root.current_panel = root.games_submenu

def open_game_stores():
    messagebox.showinfo("Encrypted Transmission", "Bringing up classified supply channels...")

def open_kingsman_emby():
    """Abrir Emby/Jellyfin server com seleção de categoria"""
    # Mapeamento das categorias de media
    media_choices = [
        ("Movies", "movies"),
        ("Animated Movies", "animovie"),
        ("TV Shows", "tvshows"),
        ("Animated TV Shows", "anitvshows"),
        ("Dub TV Shows", "dubtvshows"),
    ]
    
    # URLs para cada categoria
    media_urls = {
        "movies": "http://2.81.60.209:8096/web/index.html#!/videos?serverId=7538ee71e45d48fdbab403c200878a04&parentId=3",
        "animovie": "http://2.81.60.209:8096/web/index.html#!/videos?serverId=7538ee71e45d48fdbab403c200878a04&parentId=4525",
        "tvshows": "http://2.81.60.209:8096/web/index.html#!/tv?serverId=7538ee71e45d48fdbab403c200878a04&parentId=11627",
        "anitvshows": "http://2.81.60.209:8096/web/index.html#!/tv?serverId=7538ee71e45d48fdbab403c200878a04&parentId=3480",
        "dubtvshows": "http://2.81.60.209:8096/web/index.html#!/tv?serverId=7538ee71e45d48fdbab403c200878a04&parentId=10535",
    }

    def select_media_type():
        win = tk.Toplevel(root)
        win.title("Select Media Category")
        win.geometry("400x500")
        win.configure(bg=THEME["BG_MAIN"])
        
        # Logo
        logo_canvas = tk.Canvas(win, width=80, height=80, bg=THEME["BG_MAIN"], highlightthickness=0)
        logo_canvas.create_oval(8, 8, 72, 72, outline=THEME["GOLD"], width=3)
        logo_canvas.create_line(40, 20, 40, 60, fill=THEME["GOLD"], width=4)
        logo_canvas.create_arc(16, 34, 64, 68, start=0, extent=180, outline=THEME["GOLD"], width=2, style=tk.ARC)
        logo_canvas.pack(pady=(16, 0))
        
        lbl = tk.Label(win, text="Choose media type to open:", 
                      font=("Segoe UI", 14, "bold"), 
                      fg=THEME["GOLD"], bg=THEME["BG_MAIN"])
        lbl.pack(pady=(18, 6))

        selected = tk.StringVar(value='')

        def open_selected_media(code):
            selected.set(code)
            win.destroy()

        # Criar botões para cada categoria
        for (label, code) in media_choices:
            btn = AgentButton(
                win,
                text=label,
                command=lambda c=code: open_selected_media(c),
                emoji="🎬",
                bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
                activebackground=THEME["SHADOW"],
                outline=THEME["BTN_OUTLINE"]
            )
            btn.pack(pady=6, fill="x", padx=20)

        # Aguardar seleção
        win.grab_set()
        win.wait_window()
        return selected.get()

    media_type = select_media_type()
    if not media_type:
        return  # Usuário cancelou

    # URL padrão se tipo não encontrado
    url = media_urls.get(media_type, "http://2.81.60.209:8096/web/index.html#!/home")
    try:
        webbrowser.open(url)
        messagebox.showinfo("Kingsman Archive", f"Opening {media_type.replace('_', ' ').title()} in browser...")
    except Exception as ex:
        messagebox.showerror("Error", f"Failed to open media page:\n{ex}")

def open_discord():
    """Abrir Discord do Kingsman"""
    discord_url = "https://discord.gg/vArNzzBVek"  # Link do Discord Kingsman
    try:
        webbrowser.open(discord_url)
        messagebox.showinfo("Discord", "Opening Kingsman Discord server...")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open Discord link:\n{e}")

def on_exit():
    if messagebox.askokcancel("Abort Mission", f"Abort and self-destruct session, Agent {AGENT_NAME}?"):
        root.destroy()

# --- Kingsman AI Assistant ---
class KingsmanAI:
    def __init__(self):
        self.responses = {
            # Saudações
            "hello": "Greetings, Agent! I'm your Kingsman AI Assistant. How may I assist you today?",
            "hi": "Hello there, Agent! Ready for your next mission briefing?",
            "good morning": "Good morning, Agent! Intelligence reports are coming in. What do you need?",
            "good afternoon": "Good afternoon! The agency is at your service.",
            "good evening": "Good evening, Agent. Ready for some classified intel?",
            
            # Perguntas sobre o sistema
            "what can you do": "I can assist with mission planning, provide intelligence briefings, answer questions about operations, help with technical support, and engage in strategic discussions. I'm your personal Kingsman intelligence officer!",
            "help": "I'm here to help with anything you need! Ask me about missions, technology, strategy, or just have a conversation. Try asking 'what's my mission status?' or 'tell me about kingsman'.",
            
            # Kingsman relacionado
            "kingsman": "Kingsman is an elite secret intelligence service. We operate with the highest standards of excellence, protecting the world from threats while maintaining absolute discretion.",
            "mission": "Your current mission parameters are classified, but I can assist with operational planning and intelligence gathering. What specific intel do you require?",
            "agent": f"You are Agent {AGENT_NAME}, operating under TOP SECRET clearance. Your dedication to the Kingsman code is exemplary.",
            
            # Tecnologia
            "technology": "Our systems utilize cutting-edge technology for surveillance, communication, and operational support. The Kingsman tech division ensures we stay ahead of any threat.",
            "security": "Security protocols are at maximum level. All communications are encrypted and monitored for potential breaches.",
            
            # Tempo
            "time": f"Current operational time is being monitored. Stay alert, Agent.",
            "weather": "Weather conditions are being assessed for optimal mission parameters.",
            
            # Entretenimento
            "joke": "Why don't secret agents ever get cold? Because they're always undercover! *adjusts tie professionally*",
            "fun fact": "Did you know that the first intelligence agencies date back to ancient civilizations? The art of gathering information is as old as civilization itself.",
            
            # Motivacional
            "motivation": "Remember, Agent: 'Manners maketh man.' Excellence is not just expected, it's demanded. You have what it takes!",
            "confidence": "You're trained for this, Agent. Trust your instincts and remember your training. The mission success depends on your expertise.",
        }
        
        self.fallback_responses = [
            "Interesting query, Agent. Let me process that intelligence... My analysis suggests this requires further investigation.",
            "That's classified information that requires higher clearance, but I can tell you that the agency is monitoring the situation.",
            "Excellent question! Based on my intelligence networks, this is a complex matter that deserves careful consideration.",
            "Agent, your inquiry has been logged. While I don't have specific intel on that, I recommend consulting with headquarters.",
            "Fascinating topic! My databases indicate this is an area of ongoing interest to the intelligence community.",
            "That's beyond my current operational parameters, but I admire your curiosity, Agent!",
            "Intriguing! While that's outside my immediate expertise, I can tell you that Kingsman agents are trained to handle any situation.",
            "Good thinking, Agent! Though I lack specific data on that subject, your analytical approach is commendable.",
        ]
    
    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        
        # Verificar respostas diretas
        for key, response in self.responses.items():
            if key in user_input:
                return response
        
        # Verificações especiais
        if any(word in user_input for word in ["how are you", "how do you do"]):
            return "I'm operating at full capacity, Agent! All systems green and ready for action."
        
        if any(word in user_input for word in ["thank", "thanks"]):
            return "You're welcome, Agent! It's my pleasure to serve the Kingsman organization."
        
        if any(word in user_input for word in ["bye", "goodbye", "see you"]):
            return "Until next time, Agent. Stay vigilant and remember: Manners maketh man."
        
        if "?" in user_input and len(user_input) > 20:
            return "That's a sophisticated question, Agent. While I may not have all the details, I recommend cross-referencing with multiple intelligence sources for the most accurate information."
        
        # Resposta aleatória de fallback
        return random.choice(self.fallback_responses)

def open_ai_assistant():
    ai_window = tk.Toplevel(root)
    ai_window.title("Kingsman AI Assistant")
    ai_window.geometry("400x500")
    ai_window.configure(bg=THEME["BG_MAIN"])
    ai_window.resizable(True, True)
    ai_window.grab_set()
    
    # Inicializar IA
    ai = KingsmanAI()
    
    # Header
    header = tk.Label(
        ai_window,
        text="🤖 KINGSMAN AI ASSISTANT",
        font=("Segoe UI Black", 14, "bold"),
        fg=THEME["GOLD"],
        bg=THEME["BG_MAIN"],
        pady=8
    )
    header.pack()
    
    # Chat area
    chat_frame = tk.Frame(ai_window, bg=THEME["BG_MAIN"])
    chat_frame.pack(expand=True, fill="both", padx=10, pady=(0,10))
    
    # Scrollable text area
    chat_scroll = tk.Scrollbar(chat_frame)
    chat_scroll.pack(side="right", fill="y")
    
    chat_text = tk.Text(
        chat_frame,
        wrap="word",
        font=("Segoe UI", 10),
        bg=THEME["BG_PANEL"],
        fg=THEME["GOLD"],
        insertbackground=THEME["GOLD"],
        yscrollcommand=chat_scroll.set,
        state="disabled",
        padx=10,
        pady=10
    )
    chat_text.pack(expand=True, fill="both")
    chat_scroll.config(command=chat_text.yview)
    
    # Input frame
    input_frame = tk.Frame(ai_window, bg=THEME["BG_MAIN"])
    input_frame.pack(fill="x", padx=10, pady=(0,10))
    
    input_entry = tk.Entry(
        input_frame,
        font=("Segoe UI", 11),
        bg=THEME["BG_PANEL"],
        fg=THEME["GOLD"],
        insertbackground=THEME["GOLD"],
        relief="flat",
        bd=5
    )
    input_entry.pack(side="left", expand=True, fill="x", padx=(0,5))
    
    def add_message(sender, message, color=None):
        chat_text.config(state="normal")
        if color is None:
            color = THEME["GOLD"] if sender == "AI" else "#B2B2B2"
        
        chat_text.insert("end", f"{sender}: ", ("bold",))
        chat_text.insert("end", f"{message}\n\n")
        chat_text.tag_configure("bold", font=("Segoe UI", 10, "bold"), foreground=color)
        chat_text.config(state="disabled")
        chat_text.see("end")
    
    def send_message():
        user_message = input_entry.get().strip()
        if user_message:
            # Mostrar mensagem do usuário
            add_message("Agent", user_message, "#53CAFF")
            
            # Limpar entrada
            input_entry.delete(0, "end")
            
            # Obter resposta da IA
            ai_response = ai.get_response(user_message)
            
            # Mostrar resposta da IA
            add_message("Kingsman AI", ai_response)
    
    send_btn = tk.Button(
        input_frame,
        text="Send",
        font=("Segoe UI Semibold", 10),
        bg=THEME["BG_PANEL"],
        fg=THEME["GOLD"],
        activebackground=THEME["SHADOW"],
        activeforeground=THEME["GOLD"],
        relief="flat",
        padx=15,
        pady=5,
        cursor="hand2",
        command=send_message
    )
    send_btn.pack(side="right")
    
    # Bind Enter key
    input_entry.bind("<Return>", lambda e: send_message())
    
    # Welcome message
    add_message("Kingsman AI", f"Welcome, Agent {AGENT_NAME}! I'm your personal AI assistant. Ask me anything - from mission intel to general questions. How may I assist you today?")
    
    # Focus na entrada
    input_entry.focus()

def show_main_menu_panel():
    # show main panel/menu (rebuild if needed)
    if hasattr(root, 'games_submenu') and root.games_submenu:
        root.games_submenu.pack_forget()
    if hasattr(root, 'main_panel_frame') and root.main_panel_frame:
        root.main_panel_frame.pack_forget()

    root.main_panel_frame = tk.Frame(root, bg=THEME["BG_MAIN"])
    panel = root.main_panel_frame
    panel.pack(pady=(4,6))
    root.current_panel = panel

    # --- AGENT BUTTONS ---
    btn_games = AgentButton(
        panel,
        text="Enter Games Database",
        command=open_games,
        emoji="🕹️",
        bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
        activebackground=THEME["SHADOW"],
        outline=THEME["BTN_OUTLINE"]
    )
    btn_games.pack(pady=6, fill="x")

    btn_stores = AgentButton(
        panel,
        text="Visit Supply Stores",
        command=open_game_stores,
        emoji="🎩",
        bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
        activebackground=THEME["SHADOW"],
        outline=THEME["BTN_OUTLINE"]
    )
    btn_stores.pack(pady=6, fill="x")

    btn_emby = AgentButton(
        panel,
        text="Kingsman Archive (Emby)",
        command=open_kingsman_emby,
        emoji="💾",
        bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
        activebackground=THEME["SHADOW"],
        outline=THEME["BTN_OUTLINE"]
    )
    btn_emby.pack(pady=6, fill="x")

    btn_discord = AgentButton(
        panel,
        text="Kingsman Discord Server",
        command=open_discord,
        emoji="💬",
        bg=THEME["BG_PANEL"], fg="#7289da",  # Discord blue
        activebackground=THEME["SHADOW"],
        outline="#7289da"
    )
    btn_discord.pack(pady=6, fill="x")

    btn_ai = AgentButton(
        panel,
        text="Kingsman AI Assistant",
        command=open_ai_assistant,
        emoji="🤖",
        bg=THEME["BG_PANEL"], fg=THEME["GOLD"],
        activebackground=THEME["SHADOW"],
        outline=THEME["BTN_OUTLINE"]
    )
    btn_ai.pack(pady=6, fill="x")

    exit_button = AgentButton(
        panel,
        text="Abort Mission",
        command=on_exit,
        emoji="❌",
        bg=THEME["EXIT_BG"], fg=THEME["GOLD"],
        activebackground=THEME["EXIT_ACTIVE"],
        outline=THEME["BTN_OUTLINE"]
    )
    exit_button.pack(pady=(18, 6), fill="x")

def show_main_app():
    """Inicializa interface principal com otimizações de performance"""
    perf_monitor.start_operation("show_main_app")
    
    # Otimizações de rendering
    root.configure(cursor="watch")  # Mostrar que está carregando
    
    root.show_main_menu_needed = True
    header_font = ("Segoe UI Black", 15, "bold")
    footer_font = ("Segoe UI", 8, "italic")

    # Limpar widgets existentes para evitar memory leak
    for widget in root.winfo_children():
        if hasattr(widget, 'pack_forget'):
            widget.pack_forget()
        widget.destroy()  # Destruir completamente para liberar memória

    # Otimização: suspender updates durante construção da interface
    root.update_idletasks()

    # --- HEADER: Kingsman Logo (Otimizado) ---
    header_frame = tk.Frame(root, bg=THEME["BG_MAIN"])
    header_frame.pack(fill='x')
    
    # Cache da label do header
    header = tk.Label(
        header_frame,
        text="🔑   K I N G S M A N   M E N U",
        font=header_font,
        fg=THEME["GOLD"],
        bg=THEME["BG_MAIN"],
        pady=3
    )
    header.pack(side="left", anchor="nw")

    # --- Small settings ⚙️ button (top right) ---
    settings_btn = SettingsButton(header_frame)
    settings_btn.pack(side="right", padx=8, pady=3)

    subtitle = tk.Label(
        root,
        text="TOP SECRET CLEARANCE\nWelcome, Agent " + AGENT_NAME,
        font=("Segoe UI", 11),
        fg="#B2B2B2",
        bg=THEME["BG_MAIN"],
        pady=1
    )
    subtitle.pack()

    # Track panels
    root.games_submenu = None
    root.main_panel_frame = None
    root.current_panel = None

    show_main_menu_panel()

    # --- Confidential footer signature ---
    footer = tk.Label(
        root,
        text="Kingsman Terminal v1.4.2 – Clearance: TOP SECRET",
        fg="#757575",
        bg=THEME["BG_MAIN"],
        font=footer_font
    )
    footer.pack(side="bottom", pady=(2,10))

    root.protocol("WM_DELETE_WINDOW", on_exit)
    
    # Otimizações finais
    root.configure(cursor="")  # Restaurar cursor normal
    root.update_idletasks()  # Forçar atualização final
    
    # Finalizar monitoramento de performance
    perf_monitor.end_operation("show_main_app")

# --- SISTEMA DE ATUALIZAÇÕES GITHUB KINGSMAN-INC ---
def check_github_updates():
    """Verifica atualizações no repositório GitHub da Kingsman-Inc (v1.4.2)"""
    try:
        print("🔍 Verificando atualizações no GitHub Kingsman-Inc v1.4.2...")
        
        # Verificar API de atualizações (GitHub API para releases)
        github_api_url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(github_api_url)
        req.add_header('User-Agent', 'Kingsman-Menu/1.4.2')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            release_data = json.loads(response.read().decode())
            
        # Extrair informações da release
        latest_version = release_data.get('tag_name', CURRENT_VERSION).replace('v', '')
        latest_patch = latest_version  # Patches são tratados como versões completas
        
        # Sistema unificado: patches = updates completas desde v1.4.2
        has_update = False
        update_info = []
        
        # Comparar versões usando sistema semântico
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        current_tuple = version_tuple(CURRENT_VERSION)
        latest_tuple = version_tuple(latest_version)
        
        if latest_tuple > current_tuple:
            has_update = True
            
            # Determinar tipo de atualização
            update_type = 'major' if latest_tuple[0] > current_tuple[0] or latest_tuple[1] > current_tuple[1] else 'patch'
            
            # Assets de download
            download_url = ''
            if release_data.get('assets'):
                # Procurar pelo instalador principal
                for asset in release_data['assets']:
                    if 'Complete_Installer' in asset['name'] and asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
            
            update_info.append({
                'type': update_type,
                'version': latest_version,
                'current': CURRENT_VERSION,
                'url': download_url or release_data.get('html_url', ''),
                'changes': release_data.get('body', 'Novas atualizações disponíveis.'),
                'published_at': release_data.get('published_at', ''),
                'size': release_data.get('assets', [{}])[0].get('size', 0) if release_data.get('assets') else 0
            })
            
        return has_update, update_info, release_data
        
    except Exception as e:
        print(f"Erro ao verificar atualizações GitHub: {e}")
        return False, [], {}

def download_github_update(update_info):
    """Baixa atualização do GitHub"""
    try:
        url = update_info.get('url', '')
        if not url:
            messagebox.showerror("Erro", "URL de download não encontrada")
            return False
            
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        filename = url.split('/')[-1]
        filepath = os.path.join(temp_dir, filename)
        
        # Janela de progresso
        progress_window = tk.Toplevel()
        progress_window.title("Baixando atualização...")
        progress_window.geometry("400x150")
        progress_window.configure(bg=THEME['BG_MAIN'])
        progress_window.transient(root)
        progress_window.grab_set()
        
        # Centralizar janela
        progress_window.geometry("+{}+{}".format(
            root.winfo_rootx() + 50,
            root.winfo_rooty() + 50
        ))
        
        status_label = tk.Label(
            progress_window,
            text="🔄 Conectando ao servidor Kingsman-Inc...",
            bg=THEME['BG_MAIN'],
            fg=THEME['GOLD'],
            font=("Segoe UI", 11)
        )
        status_label.pack(pady=20)
        
        progress_bar = tk.Frame(progress_window, bg=THEME['BG_PANEL'], height=6)
        progress_bar.pack(fill="x", padx=20, pady=10)
        
        progress_fill = tk.Frame(progress_bar, bg=THEME['GOLD'], height=6)
        progress_fill.pack(side="left", fill="y")
        
        def update_progress(percent, status):
            progress_fill.config(width=int(360 * percent / 100))
            status_label.config(text=status)
            progress_window.update()
        
        # Download com callback de progresso
        def download_with_progress():
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Kingsman-Menu/1.3')
                
                with urllib.request.urlopen(req) as response:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                status = f"📥 Baixando: {percent:.1f}% ({downloaded/1024/1024:.1f}MB)"
                                update_progress(percent, status)
                
                update_progress(100, "✅ Download concluído!")
                return True
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha no download: {e}")
                return False
            finally:
                progress_window.destroy()
        
        # Executar download
        success = download_with_progress()
        
        if success and os.path.exists(filepath):
            # Processar arquivo baixado
            if filename.endswith('.zip'):
                return process_update_zip(filepath, update_info)
            
        return False
        
    except Exception as e:
        print(f"Erro ao baixar atualização: {e}")
        messagebox.showerror("Erro", f"Erro durante download: {e}")
        return False

def process_update_zip(zip_path, update_info):
    """Processa arquivo ZIP de atualização"""
    try:
        update_type = update_info.get('type', 'patch')
        
        # Mostrar confirmação
        changes_text = "\n".join(update_info.get('changes', ['Melhorias gerais']))
        
        confirm_msg = f"""🚀 ATUALIZAÇÃO KINGSMAN-INC PRONTA!

📦 Tipo: {'🔄 Atualização Completa' if update_type == 'major' else '🔧 Patch de Correções'}
🏷️ Versão: {update_info.get('version', 'N/A')}

📋 Mudanças:
{changes_text}

⚠️ A aplicação será reiniciada após a instalação.
Deseja continuar?"""
        
        if not messagebox.askyesno("Confirmar Atualização", confirm_msg):
            return False
        
        # Extrair e aplicar atualização
        temp_extract = tempfile.mkdtemp()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)
        
        # Determinar diretório de instalação
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Criar backup
        backup_dir = os.path.join(current_dir, f"backup_{int(time.time())}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup arquivos importantes
        important_files = ['games_paths.json', 'games_config.json', 'theme_settings.json']
        for file in important_files:
            src = os.path.join(current_dir, file)
            if os.path.exists(src):
                shutil.copy2(src, backup_dir)
        
        # Aplicar atualização
        for root_path, dirs, files in os.walk(temp_extract):
            for file in files:
                src_file = os.path.join(root_path, file)
                rel_path = os.path.relpath(src_file, temp_extract)
                dst_file = os.path.join(current_dir, rel_path)
                
                # Criar diretórios se necessário
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(src_file, dst_file)
        
        # Limpar temporários
        shutil.rmtree(temp_extract)
        os.remove(zip_path)
        
        messagebox.showinfo(
            "Atualização Concluída",
            "✅ Atualização aplicada com sucesso!\n🔄 A aplicação será reiniciada."
        )
        
        # Reiniciar aplicação
        restart_application()
        return True
        
    except Exception as e:
        print(f"Erro ao processar atualização: {e}")
        messagebox.showerror("Erro", f"Falha ao aplicar atualização: {e}")
        return False

def load_auto_update_config():
    """Carrega as configurações de auto-update do arquivo"""
    default_config = {
        "enabled": True,
        "check_on_startup": True,
        "auto_install_patches": False,
        "auto_install_minor": False,
        "silent_mode": False,
        "check_interval": 24,
        "last_check": "",
        "skipped_version": ""
    }
    
    try:
        if os.path.exists("auto_update_config.json"):
            with open("auto_update_config.json", "r") as f:
                config = json.load(f)
                # Garantir que todas as chaves existem
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return default_config
    except Exception as e:
        print(f"Erro ao carregar configurações de auto-update: {e}")
        return default_config

def auto_check_updates():
    """Verificação automática de updates em background"""
    if not AUTO_UPDATE_CONFIG["enabled"]:
        return
    
    try:
        has_update, updates, api_data = check_github_updates()
        
        if has_update:
            # Processar cada update disponível
            for update in updates:
                update_type = update.get('type', 'patch')
                
                # Decidir se deve instalar automaticamente
                should_auto_install = False
                
                if update_type == 'patch' and AUTO_UPDATE_CONFIG.get("auto_install_patches", False):
                    should_auto_install = True
                elif update_type == 'minor' and AUTO_UPDATE_CONFIG.get("auto_install_minor", False):
                    should_auto_install = True
                
                if should_auto_install and AUTO_UPDATE_CONFIG["silent_mode"]:
                    # Instalação silenciosa
                    install_update_silently(update)
                else:
                    # Mostrar notificação de update disponível
                    show_update_notification(update)
                    
    except Exception as e:
        print(f"Erro na verificação automática: {e}")
    
    # Reagendar próxima verificação
    if AUTO_UPDATE_CONFIG["enabled"]:
        interval_hours = AUTO_UPDATE_CONFIG.get("check_interval", 24)
        interval_ms = interval_hours * 60 * 60 * 1000  # converter horas para millisegundos
        root.after(interval_ms, auto_check_updates)

def show_update_notification(update_info):
    """Mostra notificação de update disponível"""
    if AUTO_UPDATE_CONFIG.get("silent_mode", False):
        return
    
    update_type = update_info.get('type', 'patch')
    version = update_info.get('version', 'N/A')
    
    # Criar janela de notificação não-intrusiva
    notification = tk.Toplevel()
    notification.title("🔔 Update Disponível")
    notification.geometry("350x200")
    notification.configure(bg=THEME['BG_MAIN'])
    notification.attributes('-topmost', True)
    notification.resizable(False, False)
    
    # Posicionar no canto inferior direito
    x = notification.winfo_screenwidth() - 370
    y = notification.winfo_screenheight() - 250
    notification.geometry(f"+{x}+{y}")
    
    # Conteúdo da notificação
    icon_text = "🚀" if update_type == 'major' else "🔧"
    title_text = f"{icon_text} Update Disponível"
    
    tk.Label(
        notification,
        text=title_text,
        font=("Segoe UI", 12, "bold"),
        fg=THEME['GOLD'],
        bg=THEME['BG_MAIN']
    ).pack(pady=10)
    
    tk.Label(
        notification,
        text=f"Nova versão: v{version}",
        font=("Segoe UI", 10),
        fg=THEME['TEXT'],
        bg=THEME['BG_MAIN']
    ).pack(pady=5)
    
    # Botões de ação
    button_frame = tk.Frame(notification, bg=THEME['BG_MAIN'])
    button_frame.pack(pady=15)
    
    def install_now():
        notification.destroy()
        install_update_with_progress(update_info)
    
    def remind_later():
        notification.destroy()
        # Reagendar para 10 minutos
        root.after(600000, lambda: show_update_notification(update_info))
    
    def skip_version():
        notification.destroy()
        # Salvar versão para pular
        save_skipped_version(update_info.get('version'))
    
    tk.Button(
        button_frame,
        text="📥 Instalar Agora",
        font=("Segoe UI", 9),
        bg=THEME['GOLD'],
        fg=THEME['BG_MAIN'],
        bd=0,
        padx=15,
        pady=5,
        command=install_now
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="⏰ Lembrar Depois",
        font=("Segoe UI", 9),
        bg=THEME['BG_PANEL'],
        fg=THEME['TEXT'],
        bd=0,
        padx=15,
        pady=5,
        command=remind_later
    ).pack(side=tk.LEFT, padx=5)
    
    if update_type != 'critical':
        tk.Button(
            button_frame,
            text="❌ Pular Versão",
            font=("Segoe UI", 9),
            bg=THEME['BG_PANEL'],
            fg=THEME['TEXT'],
            bd=0,
            padx=15,
            pady=5,
            command=skip_version
        ).pack(side=tk.LEFT, padx=5)
    
    # Auto-fechar após 30 segundos se não houver interação
    notification.after(30000, notification.destroy)

def install_update_silently(update_info):
    """Instala update silenciosamente em background"""
    try:
        if AUTO_UPDATE_CONFIG["backup_before_update"]:
            create_backup()
        
        # Download em background
        download_thread = threading.Thread(
            target=download_and_apply_update,
            args=(update_info, True)  # True = silent mode
        )
        download_thread.daemon = True
        download_thread.start()
        
    except Exception as e:
        print(f"Erro na instalação silenciosa: {e}")

def install_update_with_progress(update_info):
    """Instala update com interface de progresso"""
    try:
        # Mostrar confirmação primeiro
        update_type = update_info.get('type', 'patch')
        version = update_info.get('version', 'N/A')
        changes = update_info.get('changes', ['Melhorias gerais'])
        
        icon = "🚀" if update_type == 'major' else "🔧"
        type_name = "Atualização Completa" if update_type == 'major' else "Patch de Correções"
        
        changes_text = "\n• ".join(changes[:5])  # Mostrar apenas 5 mudanças
        if len(changes) > 5:
            changes_text += f"\n... e mais {len(changes) - 5} melhorias"
        
        confirm_msg = f"""{icon} KINGSMAN MENU UPDATE

📦 Tipo: {type_name}
🏷️ Versão: {version}

📋 Principais mudanças:
• {changes_text}

⚠️ A aplicação será reiniciada após a instalação.
📂 Backup será criado automaticamente.

Deseja continuar com a instalação?"""
        
        if messagebox.askyesno("Confirmar Instalação", confirm_msg):
            # Criar backup se configurado
            if AUTO_UPDATE_CONFIG["backup_before_update"]:
                create_backup()
            
            # Download com progresso
            download_thread = threading.Thread(
                target=download_and_apply_update,
                args=(update_info, False)  # False = show progress
            )
            download_thread.daemon = True
            download_thread.start()
            
    except Exception as e:
        print(f"Erro na instalação com progresso: {e}")
        messagebox.showerror("Erro", f"Falha ao instalar update: {e}")

def create_backup():
    """Cria backup da versão atual"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(current_dir, f"backup_v{CURRENT_VERSION}_{timestamp}")
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # Arquivos importantes para backup
        important_files = [
            'games_paths.json',
            'games_config.json', 
            'theme_settings.json',
            'user_preferences.json'
        ]
        
        for file in important_files:
            src = os.path.join(current_dir, file)
            if os.path.exists(src):
                shutil.copy2(src, backup_dir)
        
        print(f"Backup criado em: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return None

def save_skipped_version(version):
    """Salva versão que foi pulada pelo usuário"""
    try:
        config_dir = os.path.expanduser("~/.kingsman_menu")
        os.makedirs(config_dir, exist_ok=True)
        
        skipped_file = os.path.join(config_dir, "skipped_versions.json")
        
        skipped_versions = []
        if os.path.exists(skipped_file):
            with open(skipped_file, 'r') as f:
                skipped_versions = json.load(f)
        
        if version not in skipped_versions:
            skipped_versions.append(version)
            
        with open(skipped_file, 'w') as f:
            json.dump(skipped_versions, f)
            
    except Exception as e:
        print(f"Erro ao salvar versão pulada: {e}")

def download_file_silent(url, filepath):
    """Download silencioso de arquivo"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Kingsman-Menu/1.4')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(response, f)
        
        return True
        
    except Exception as e:
        print(f"Erro no download silencioso: {e}")
        return False

def show_download_progress(url, filepath, update_info):
    """Mostra progresso do download"""
    try:
        # Criar janela de progresso
        progress_window = tk.Toplevel()
        progress_window.title("📥 Baixando Atualização")
        progress_window.geometry("450x200")
        progress_window.configure(bg=THEME['BG_MAIN'])
        progress_window.resizable(False, False)
        progress_window.transient(root)
        progress_window.grab_set()
        
        # Centralizar
        x = (progress_window.winfo_screenwidth() // 2) - 225
        y = (progress_window.winfo_screenheight() // 2) - 100
        progress_window.geometry(f"+{x}+{y}")
        
        # Labels
        title_label = tk.Label(
            progress_window,
            text=f"🚀 Baixando Kingsman Menu v{update_info.get('version', 'latest')}",
            font=("Segoe UI", 12, "bold"),
            fg=THEME['GOLD'],
            bg=THEME['BG_MAIN']
        )
        title_label.pack(pady=(20, 10))
        
        status_label = tk.Label(
            progress_window,
            text="Iniciando download...",
            font=("Segoe UI", 10),
            fg=THEME['TEXT'],
            bg=THEME['BG_MAIN']
        )
        status_label.pack(pady=5)
        
        # Barra de progresso simulada
        progress_frame = tk.Frame(progress_window, bg=THEME['BG_PANEL'], height=10)
        progress_frame.pack(fill="x", padx=30, pady=10)
        
        progress_bar = tk.Frame(progress_frame, bg=THEME['GOLD'], height=10)
        progress_bar.pack(side="left", fill="y")
        
        def update_progress(percent, status_text):
            width = int(390 * percent / 100)
            progress_bar.config(width=width)
            status_label.config(text=status_text)
            progress_window.update()
        
        # Download com progresso
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Kingsman-Menu/1.4')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / 1024 / 1024
                        mb_total = total_size / 1024 / 1024
                        status = f"📥 {percent:.1f}% - {mb_downloaded:.1f}MB / {mb_total:.1f}MB"
                        update_progress(percent, status)
        
        update_progress(100, "✅ Download concluído!")
        time.sleep(1)
        progress_window.destroy()
        
        return True
        
    except Exception as e:
        print(f"Erro no download com progresso: {e}")
        if 'progress_window' in locals():
            progress_window.destroy()
        return False

def apply_update_files(zip_path, update_info, silent_mode=False):
    """Aplica arquivos do update"""
    try:
        # Extrair arquivo ZIP
        temp_extract = tempfile.mkdtemp()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)
        
        # Diretório atual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Aplicar arquivos
        for root_path, dirs, files in os.walk(temp_extract):
            for file in files:
                src_file = os.path.join(root_path, file)
                rel_path = os.path.relpath(src_file, temp_extract)
                dst_file = os.path.join(current_dir, rel_path)
                
                # Criar diretórios se necessário
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(src_file, dst_file)
        
        # Limpar temporários
        shutil.rmtree(temp_extract)
        os.remove(zip_path)
        
        # Atualizar versão no código se necessário
        update_version_info(update_info)
        
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar update: {e}")
        return False

def update_version_info(update_info):
    """Atualiza informações de versão após update"""
    try:
        version_file = os.path.join(
            os.path.expanduser("~/.kingsman_menu"), 
            "current_version.json"
        )
        
        version_data = {
            "version": update_info.get('version', CURRENT_VERSION),
            "patch": update_info.get('version', CURRENT_PATCH),
            "updated_at": time.time(),
            "update_type": update_info.get('type', 'patch')
        }
        
        os.makedirs(os.path.dirname(version_file), exist_ok=True)
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
            
    except Exception as e:
        print(f"Erro ao atualizar informações de versão: {e}")

def show_auto_update_settings():
    """Função de configuração de auto-update DEPRECADA - Use a interface integrada na aba Settings > Updates"""
    messagebox.showinfo("Configurações", "As configurações de auto-update agora estão integradas em Settings > Aba Updates")

def download_and_apply_update(update_info, silent_mode=False):
    """Download e aplicação do update"""
    try:
        url = update_info.get('url', '')
        if not url:
            if not silent_mode:
                messagebox.showerror("Erro", "URL de download não encontrada")
            return False
        
        # Preparar diretórios
        temp_dir = tempfile.mkdtemp()
        filename = f"kingsman_update_{update_info.get('version', 'latest')}.zip"
        filepath = os.path.join(temp_dir, filename)
        
        if not silent_mode:
            # Mostrar progresso visual
            download_success = show_download_progress(url, filepath, update_info)
        else:
            # Download silencioso
            download_success = download_file_silent(url, filepath)
        
        if not download_success:
            return False
        
        # Aplicar update
        if os.path.exists(filepath):
            apply_success = apply_update_files(filepath, update_info, silent_mode)
            
            if apply_success and not silent_mode:
                messagebox.showinfo(
                    "Update Concluído",
                    "✅ Atualização aplicada com sucesso!\n🔄 Reiniciando aplicação..."
                )
            
            # Reiniciar se configurado
            if apply_success and AUTO_UPDATE_CONFIG["restart_after_update"]:
                restart_application()
                
            return apply_success
            
    except Exception as e:
        print(f"Erro no download/aplicação: {e}")
        if not silent_mode:
            messagebox.showerror("Erro", f"Falha no update: {e}")
        return False

def show_github_updates_dialog():
    """Mostra diálogo de atualizações disponíveis"""
    try:
        has_update, updates, api_data = check_github_updates()
        
        if not has_update:
            messagebox.showinfo(
                "Atualizações Kingsman-Inc",
                "✅ Você está executando a versão mais recente!\n\n"
                f"📦 Versão atual: v{CURRENT_VERSION}\n"
                f"🔧 Patch: v{CURRENT_PATCH}\n"
                f"🔗 Repositório: github.com/{GITHUB_ORG}/{GITHUB_REPO}"
            )
            return
        
        # Janela de atualizações
        update_window = tk.Toplevel(root)
        update_window.title("🚀 Atualizações Disponíveis - Kingsman-Inc")
        update_window.geometry("400x500")
        update_window.configure(bg=THEME['BG_MAIN'])
        update_window.transient(root)
        update_window.grab_set()
        
        # Cabeçalho
        header = tk.Frame(update_window, bg=THEME['GOLD'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🚀 ATUALIZAÇÕES KINGSMAN-INC",
            font=("Segoe UI", 14, "bold"),
            bg=THEME['GOLD'],
            fg="#000"
        ).pack(expand=True)
        
        # Área de conteúdo
        content_frame = tk.Frame(update_window, bg=THEME['BG_MAIN'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Listar atualizações
        for i, update in enumerate(updates):
            update_frame = tk.Frame(content_frame, bg=THEME['BG_PANEL'], relief="raised", bd=1)
            update_frame.pack(fill="x", pady=5)
            
            # Tipo de atualização
            type_emoji = "🔄" if update['type'] == 'major' else "🔧"
            type_text = "Atualização Completa" if update['type'] == 'major' else "Patch"
            
            tk.Label(
                update_frame,
                text=f"{type_emoji} {type_text}",
                font=("Segoe UI", 12, "bold"),
                bg=THEME['BG_PANEL'],
                fg=THEME['GOLD']
            ).pack(anchor="w", padx=10, pady=(5, 0))
            
            tk.Label(
                update_frame,
                text=f"📦 {update['current']} → {update['version']}",
                font=("Segoe UI", 10),
                bg=THEME['BG_PANEL'],
                fg="white"
            ).pack(anchor="w", padx=10)
            
            # Botão de download
            tk.Button(
                update_frame,
                text="📥 Baixar Agora",
                command=lambda u=update: download_github_update(u),
                bg=THEME['GOLD'],
                fg="#000",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=15,
                pady=5
            ).pack(anchor="e", padx=10, pady=5)
        
        # Rodapé
        footer_frame = tk.Frame(update_window, bg=THEME['BG_MAIN'])
        footer_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            footer_frame,
            text=f"🔗 github.com/{GITHUB_ORG}/{GITHUB_REPO}",
            font=("Segoe UI", 9),
            bg=THEME['BG_MAIN'],
            fg="#888"
        ).pack()
        
    except Exception as e:
        print(f"Erro ao mostrar atualizações: {e}")
        messagebox.showerror("Erro", f"Erro ao verificar atualizações: {e}")

def restart_application():
    """Reinicia a aplicação"""
    try:
        root.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        print(f"Erro ao reiniciar aplicação: {e}")
        sys.exit(1)

# Global variable to track if there's a pending update
pending_update_info = None
update_notification_widget = None

def auto_check_github_updates():
    """Verifica atualizações automaticamente na inicialização sem bloquear a interface"""
    def check_in_background():
        global pending_update_info, update_notification_widget
        
        try:
            has_update, updates, _ = check_github_updates()
            
            if has_update:
                # Mostrar diálogo perguntando se quer atualizar
                def ask_for_update():
                    if 'root' in globals() and root.winfo_exists():
                        result = messagebox.askyesno(
                            "🚀 Atualização Disponível",
                            f"Uma nova versão está disponível!\n\n"
                            f"Versão atual: v{CURRENT_VERSION}\n"
                            f"Nova versão: v{updates[0]['version'] if updates else 'desconhecida'}\n\n"
                            f"Deseja visualizar e instalar a atualização agora?",
                            icon="question"
                        )
                        
                        if result:
                            # Usuário quer atualizar
                            show_github_updates_dialog()
                        else:
                            # Usuário não quer atualizar - mostrar notificação na tela inicial
                            pending_update_info = updates
                            show_update_reminder_on_main_screen()
                
                # Mostrar após 3 segundos da inicialização (no thread principal)
                if 'root' in globals() and root.winfo_exists():
                    root.after(3000, ask_for_update)
                
        except Exception as e:
            print(f"Erro na verificação automática: {e}")
    
    # Executar em thread separada para não bloquear a interface
    if 'root' in globals() and root.winfo_exists():
        threading.Thread(target=check_in_background, daemon=True).start()

def show_update_reminder_on_main_screen():
    """Mostra uma mensagem discreta na tela inicial sobre atualização disponível"""
    global update_notification_widget, pending_update_info
    
    if not pending_update_info or 'root' not in globals():
        return
    
    try:
        # Remove notificação anterior se existir
        if update_notification_widget:
            try:
                update_notification_widget.destroy()
            except:
                pass
        
        # Criar frame para a notificação
        notification_frame = tk.Frame(root, bg="#ff6b35", relief="solid", bd=1)
        notification_frame.pack(side="top", fill="x", padx=5, pady=2)
        
        # Texto da notificação
        update_text = f"🚀 Nova versão v{pending_update_info[0]['version']} disponível!"
        
        notification_label = tk.Label(
            notification_frame,
            text=update_text,
            font=("Segoe UI", 9, "bold"),
            bg="#ff6b35",
            fg="white",
            pady=3
        )
        notification_label.pack(side="left", padx=10)
        
        # Botões de ação
        button_frame = tk.Frame(notification_frame, bg="#ff6b35")
        button_frame.pack(side="right", padx=5)
        
        tk.Button(
            button_frame,
            text="Ver Atualização",
            font=("Segoe UI", 8),
            bg="white",
            fg="#ff6b35",
            cursor="hand2",
            padx=8,
            pady=1,
            relief="flat",
            command=lambda: [notification_frame.destroy(), show_github_updates_dialog(), setattr(globals(), 'update_notification_widget', None)]
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            bg="#d63031",
            fg="white",
            cursor="hand2",
            padx=4,
            pady=1,
            relief="flat",
            command=lambda: [notification_frame.destroy(), setattr(globals(), 'update_notification_widget', None), setattr(globals(), 'pending_update_info', None)]
        ).pack(side="left")
        
        # Guardar referência para poder remover depois
        update_notification_widget = notification_frame
        
    except Exception as e:
        print(f"Erro ao mostrar notificação de update: {e}")

# --- FUNÇÕES DOS BOTÕES PRINCIPAIS ---
def open_game_stores():
    """Abre lojas de jogos"""
    messagebox.showinfo("Encrypted Transmission", "Bringing up classified supply channels...")

def open_kingsman_emby():
    """Abre sistema Emby"""
    messagebox.showinfo("Kingsman Archive", "Connecting to Emby intelligence hub...")

def check_for_updates():
    """Função do botão Check for Updates - conectada ao GitHub"""
    show_github_updates_dialog()

def open_ai_assistant():
    """Abre assistente IA"""
    ai_window = tk.Toplevel(root)
    ai_window.title("🤖 Kingsman AI Assistant")
    ai_window.geometry("400x500")
    ai_window.configure(bg=THEME["BG_MAIN"])
    ai_window.transient(root)
    
    # Interface simples de chat
    header = tk.Label(
        ai_window,
        text="🤖 KINGSMAN AI ASSISTANT",
        font=("Segoe UI", 14, "bold"),
        bg=THEME['GOLD'],
        fg="#000",
        pady=10
    )
    header.pack(fill="x")
    
    chat_frame = tk.Frame(ai_window, bg=THEME["BG_MAIN"])
    chat_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    chat_text = tk.Text(
        chat_frame,
        font=("Segoe UI", 10),
        bg=THEME["BG_PANEL"],
        fg="white",
        wrap="word",
        state="disabled",
        padx=10,
        pady=10
    )
    chat_text.pack(expand=True, fill="both")
    
    # Mensagem inicial
    chat_text.config(state="normal")
    chat_text.insert("end", "🤖 Kingsman AI: Greetings, Agent! I'm your AI assistant. How may I help you today?\n\n")
    chat_text.config(state="disabled")
    
    input_frame = tk.Frame(ai_window, bg=THEME["BG_MAIN"])
    input_frame.pack(fill="x", padx=10, pady=(0,10))
    
    input_entry = tk.Entry(
        input_frame,
        font=("Segoe UI", 11),
        bg=THEME["BG_PANEL"],
        fg=THEME["GOLD"],
        insertbackground=THEME["GOLD"],
        relief="flat",
        bd=5
    )
    input_entry.pack(side="left", expand=True, fill="x", padx=(0,5))
    
    def send_message():
        user_message = input_entry.get().strip()
        if user_message:
            chat_text.config(state="normal")
            chat_text.insert("end", f"Agent: {user_message}\n")
            chat_text.insert("end", f"🤖 AI: Message received. Processing... (AI responses coming soon!)\n\n")
            chat_text.config(state="disabled")
            chat_text.see("end")
            input_entry.delete(0, "end")
    
    tk.Button(
        input_frame,
        text="Send",
        command=send_message,
        bg=THEME['GOLD'],
        fg="#000",
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    ).pack(side="right")
    
    input_entry.bind('<Return>', lambda e: send_message())

def on_exit():
    """Função de saída"""
    if messagebox.askokcancel("Abort Mission", f"Abort and self-destruct session, Agent {AGENT_NAME}?"):
        root.destroy()

# --- Sistema de Autenticação de Agentes ---
def authenticate_agent():
    """Sistema de autenticação com interface melhorada"""
    agent_credentials = load_agent_credentials()

    # Cores do tema de autenticação
    AUTH_C = "#23272c"
    AUTH_TITLE_C = "#f8d85d"
    AUTH_BTN_C = "#373b41"
    AUTH_BTN_HOVER = "#d4af37"
    AUTH_TEXT = "#ffffff"
    AUTH_FONT = ("Segoe UI", 14, "bold")
    AUTH_LABEL_FONT = ("Segoe UI", 12)
    AUTH_ENTRY_BG = "#16181c"
    AUTH_FG_LABEL = "#f8d85d"
    AUTH_FG_ENTRY = "#ffffff"

    def switch_mode():
        if mode_var.get() == "login":
            new_agent_frame.pack_forget()
            login_frame.pack(fill='both', expand=True)
        else:
            login_frame.pack_forget()
            new_agent_frame.pack(fill='both', expand=True)

    auth_root = tk.Tk()
    auth_root.title("Kingsman Authentication")
    auth_root.geometry("400x500")
    auth_root.resizable(0, 0)
    auth_root.configure(bg=AUTH_C)

    # Logo
    canvas = tk.Canvas(auth_root, width=80, height=80, bg=AUTH_C, highlightthickness=0)
    canvas.create_oval(8, 8, 72, 72, outline=AUTH_TITLE_C, width=3)
    canvas.create_line(40, 20, 40, 60, fill=AUTH_TITLE_C, width=4)
    canvas.create_arc(16, 34, 64, 68, start=0, extent=180, outline=AUTH_TITLE_C, width=2, style=tk.ARC)
    canvas.pack(pady=(16, 0))

    # Title
    title = tk.Label(
        auth_root,
        text="Kingsman Authentication",
        font=("Segoe Script", 20, "bold"),
        fg=AUTH_TITLE_C,
        bg=AUTH_C
    )
    title.pack(pady=(0, 6))

    # Mode selection
    mode_var = tk.StringVar(value="login")
    mode_frame = tk.Frame(auth_root, bg=AUTH_C)
    for mode_text, value in [("Login", "login"), ("Create Agent", "create")]:
        tk.Radiobutton(
            mode_frame,
            text=mode_text,
            variable=mode_var,
            value=value,
            font=AUTH_LABEL_FONT, fg=AUTH_FG_LABEL, bg=AUTH_C,
            selectcolor=AUTH_C,
            activebackground=AUTH_C, activeforeground=AUTH_FG_LABEL, command=switch_mode
        ).pack(side="left", padx=8)
    mode_frame.pack(pady=(0, 18))

    # --- Login Frame
    login_frame = tk.Frame(auth_root, bg=AUTH_C)
    def _pack_label_and_entry(parent, label, show=None):
        tk.Label(parent, text=label, font=AUTH_LABEL_FONT, fg=AUTH_FG_LABEL, bg=AUTH_C).pack(pady=(8,2))
        entry = tk.Entry(parent, font=AUTH_FONT, bg=AUTH_ENTRY_BG, fg=AUTH_FG_ENTRY, bd=2, width=22, 
                         show=show, justify='center')
        entry.pack(pady=(0,8))
        return entry
    
    name_entry = _pack_label_and_entry(login_frame, "Agent Name:")
    pass_entry = _pack_label_and_entry(login_frame, "Password:", show='*')
    login_result = tk.Label(login_frame, text="", font=AUTH_LABEL_FONT, fg="red", bg=AUTH_C)
    login_result.pack()

    def try_login():
        agent = name_entry.get().strip()
        password = pass_entry.get().strip()
        if agent in agent_credentials and agent_credentials[agent] == hash_password(password):
            global AGENT_NAME
            AGENT_NAME = agent
            auth_root.destroy()
            main()
        else:
            messagebox.showerror(
                "Access Denied",
                "Agent authentication failed.\nPermission denied."
            )
            pass_entry.delete(0, tk.END)

    login_btn = tk.Button(
        login_frame, text="Authenticate", font=AUTH_FONT, bg=AUTH_BTN_C, fg=AUTH_TEXT,
        activebackground=AUTH_TITLE_C, activeforeground=AUTH_C,
        bd=0, width=22, height=2, cursor="hand2", command=try_login
    )
    login_btn.pack(pady=(16,6))
    login_frame.pack(fill='both', expand=False)

    # --- Create Agent Frame
    new_agent_frame = tk.Frame(auth_root, bg=AUTH_C)
    new_name_entry = _pack_label_and_entry(new_agent_frame, "New Agent Name:")
    new_pass_entry = _pack_label_and_entry(new_agent_frame, "New Password:", show='*')
    conf_pass_entry = _pack_label_and_entry(new_agent_frame, "Confirm Password:", show='*')
    create_result = tk.Label(new_agent_frame, text="", font=AUTH_LABEL_FONT, fg="red", bg=AUTH_C)
    create_result.pack()

    def try_create_agent():
        new_agent = new_name_entry.get().strip()
        new_pass = new_pass_entry.get().strip()
        conf_pass = conf_pass_entry.get().strip()
        if not new_agent or not new_pass:
            messagebox.showerror("Error", "Agent name and password cannot be empty.")
            return
        if new_agent in agent_credentials:
            messagebox.showerror("Error", f"Agent '{new_agent}' already exists.")
            new_name_entry.delete(0, tk.END)
            return
        if new_pass != conf_pass:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        # Save new agent permanently
        agent_credentials[new_agent] = hash_password(new_pass)
        save_agent_credentials(agent_credentials)
        messagebox.showinfo("Success", f"Agent '{new_agent}' created! Please login.")
        new_name_entry.delete(0, tk.END)
        new_pass_entry.delete(0, tk.END)
        conf_pass_entry.delete(0, tk.END)
        mode_var.set("login")
        switch_mode()

    create_btn = tk.Button(
        new_agent_frame, text="Create Agent", font=AUTH_FONT, bg=AUTH_BTN_C, fg=AUTH_TEXT,
        activebackground=AUTH_TITLE_C, activeforeground=AUTH_C,
        bd=0, width=22, height=2, cursor="hand2", command=try_create_agent
    )
    create_btn.pack(pady=(16,6))

    def on_enter(e, btn):
        btn.configure(bg=AUTH_BTN_HOVER, fg=AUTH_C)
    def on_leave(e, btn):
        btn.configure(bg=AUTH_BTN_C, fg=AUTH_TEXT)
    login_btn.bind("<Enter>", lambda e, b=login_btn: on_enter(e, b))
    login_btn.bind("<Leave>", lambda e, b=login_btn: on_leave(e, b))
    create_btn.bind("<Enter>", lambda e, b=create_btn: on_enter(e, b))
    create_btn.bind("<Leave>", lambda e, b=create_btn: on_leave(e, b))

    # Center frames
    login_frame.pack(fill='x', expand=False, pady=(16, 0))
    new_agent_frame.pack_forget()

    def handle_return_key(event):
        if mode_var.get() == "login":
            try_login()
        else:
            try_create_agent()
    auth_root.bind('<Return>', handle_return_key)

    # Spacer bottom
    tk.Frame(auth_root, bg=AUTH_C).pack(expand=True, fill='both')
    switch_mode()
    auth_root.mainloop()

# --- Begin main program (Otimizado) ---
def main():
    """Função principal com monitoramento de performance"""
    perf_monitor.start_operation("app_startup")
    
    try:
        # Otimizações de startup
        optimize_startup()
        
        # Carregar configurações
        load_theme()
        
        # Carregar configurações de auto-update
        global AUTO_UPDATE_CONFIG
        AUTO_UPDATE_CONFIG = load_auto_update_config()
        
        # Inicializar janela principal com otimizações
        global root
        root = tk.Tk()
        root.title("Kingsman Terminal v1.4.2 - Secure Access")
        root.geometry("400x500")
        root.configure(bg=THEME["BG_MAIN"])
        root.resizable(False, False)
        
        # Otimizações de performance
        root.update_idletasks()
        
        # Inicializar aplicação
        show_main_app()
        
        # Sistema de atualizações (em thread separada para não bloquear)
        def init_update_systems():
            try:
                # Verificar atualizações GitHub Kingsman-Inc PRIMEIRO
                auto_check_github_updates()
                
                # Inicializar sistema automático de updates
                if AUTO_UPDATE_CONFIG["check_on_startup"]:
                    # Verificação inicial (aguardar 5 segundos para app carregar)
                    root.after(5000, auto_check_updates)
                
                # Verificar What's New
                check_and_show_whats_new()
                
                # Sistema de patches (se disponível)
                if PATCH_SYSTEM_AVAILABLE and patch_manager:
                    check_patches_on_startup()
                    start_automatic_patch_checking()
                    
            except Exception as e:
                print(f"Erro ao inicializar sistemas de atualização: {e}")
        
        # Executar sistemas de atualização em thread separada
        threading.Thread(target=init_update_systems, daemon=True).start()
        
        perf_monitor.end_operation("app_startup")
        
        # Iniciar sistema de limpeza de memória
        if PERFORMANCE_MODE:
            optimize_memory()  # Limpeza inicial
            schedule_memory_cleanup()  # Agendar limpezas periódicas
        
        # Executar aplicação
        root.mainloop()
        
    except Exception as e:
        print(f"Erro crítico na aplicação: {e}")
        messagebox.showerror("Erro Crítico", f"Erro fatal na aplicação:\n{e}")
    
    finally:
        # Limpeza de memória
        gc.collect()
        print(f"Aplicação encerrada. Objetos em memória: {perf_monitor.get_memory_usage()}")

if __name__ == "__main__":
    try:
        # Verificar se há agentes registrados
        agent_credentials = load_agent_credentials()
        if not agent_credentials:
            # Criar agente padrão se não houver nenhum
            default_agent = "Kingsman"
            default_password = "kingsman"
            agent_credentials[default_agent] = hash_password(default_password)
            save_agent_credentials(agent_credentials)
            messagebox.showinfo("First Time Setup", 
                              f"Default agent created:\nUsername: {default_agent}\nPassword: {default_password}\n\nYou can create additional agents after login.")
        
        authenticate_agent()
    except Exception as ex:
        msg = f"Unexpected error: {ex}"
        print(msg)
        if "tkinter" in sys.modules:
            try:
                messagebox.showerror("Application Error", msg)
            except:
                pass
        sys.exit(1)
