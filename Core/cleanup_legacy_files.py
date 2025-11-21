"""
🗑️ Script de Limpeza - Remove arquivos legados do servidor
Execute este script para limpar completamente arquivos antigos
"""

import os
import shutil
from datetime import datetime

# Arquivos Python legados para remover
LEGACY_PYTHON_FILES = [
    "CodeNet_server_production.py",
    "CodeNet_server_production_fixed.py",
    "CodeNet_server_simple.py",
    "launch_v1.4_server.py",
    "test_server_simple.py"
]

# Arquivos BAT/PS1 antigos
LEGACY_SCRIPTS = [
    "LAUNCH_SERVER.bat",
    "LAUNCH_SERVER.ps1",
    "start_server.bat",
    "stop_server.bat",
    "start-update-server.ps1"
]

# Arquivos de spec antigos (PyInstaller)
LEGACY_SPECS = [
    "CodeNetMenu_v1.4.4_ServerStatus.spec",
    "CodeNetServerMonitor_v1.0.0.spec",
    "CodeNetServerMonitor_v1.1.0_Final.spec",
    "CodeNetServerMonitor_v2.0.0_InfrastructureComplete.spec"
]

# Arquivos HTML/TXT de warnings
LEGACY_REPORTS = [
    "warn-CodeNetMenu_v1.4.4_ServerStatus.txt",
    "warn-CodeNetServerMonitor_v1.0.0.txt",
    "warn-CodeNetServerMonitor_v1.1.0_Final.txt",
    "warn-CodeNetServerMonitor_v2.0.0_InfrastructureComplete.txt",
    "xref-CodeNetMenu_v1.4.4_ServerStatus.html",
    "xref-CodeNetServerMonitor_v1.0.0.html",
    "xref-CodeNetServerMonitor_v1.1.0_Final.html",
    "xref-CodeNetServerMonitor_v2.0.0_InfrastructureComplete.html"
]

# Arquivos de sistema antigos
LEGACY_SYSTEM = [
    "CodeNet_server.log"  # Log antigo (novo usa logs/CodeNet_server.log)
]

def cleanup_files(base_dir, file_list, category_name):
    """Remove arquivos de uma categoria"""
    removed = []
    not_found = []
    
    print(f"\n🔍 Verificando {category_name}...")
    
    for filename in file_list:
        filepath = os.path.join(base_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                removed.append(filename)
                print(f"  ✅ Removido: {filename}")
            except Exception as e:
                print(f"  ❌ Erro ao remover {filename}: {e}")
        else:
            not_found.append(filename)
    
    if not_found:
        print(f"  ℹ️  {len(not_found)} arquivo(s) já não existem")
    
    return removed, not_found

def cleanup_backups(base_dir):
    """Remove pasta de backups antigos"""
    backups_dir = os.path.join(base_dir, "backups")
    
    print("\n🔍 Verificando backups antigos...")
    
    if os.path.exists(backups_dir):
        try:
            # Contar arquivos
            files = os.listdir(backups_dir)
            count = len(files)
            
            # Remover pasta
            shutil.rmtree(backups_dir)
            print(f"  ✅ Pasta backups removida ({count} arquivos)")
            return True
        except Exception as e:
            print(f"  ❌ Erro ao remover backups: {e}")
            return False
    else:
        print("  ℹ️  Pasta backups já não existe")
        return False

def create_cleanup_report(removed_files):
    """Cria relatório de limpeza"""
    report_path = "cleanup_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("  RELATÓRIO DE LIMPEZA - CodeNet SERVER v3.0\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        f.write("ARQUIVOS REMOVIDOS:\n")
        f.write("-" * 60 + "\n")
        
        for category, files in removed_files.items():
            if files:
                f.write(f"\n{category}:\n")
                for file in files:
                    f.write(f"  - {file}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("LIMPEZA CONCLUÍDA COM SUCESSO\n")
        f.write("=" * 60 + "\n")
    
    print(f"\n📄 Relatório salvo em: {report_path}")

def main():
    """Função principal"""
    print("=" * 60)
    print("  🗑️  LIMPEZA DE SISTEMA LEGADO - CodeNet SERVER v3.0")
    print("=" * 60)
    print("\nEste script irá remover arquivos antigos do sistema.")
    print("\n⚠️  ATENÇÃO:")
    print("  - Arquivos v2.0 e anteriores serão removidos")
    print("  - O sistema v3.0 será preservado")
    print("  - Não há como desfazer esta ação")
    
    # Confirmar
    confirm = input("\n🔴 Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if confirm.upper() != "SIM":
        print("\n❌ Limpeza cancelada pelo usuário")
        return
    
    # Diretório base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\n" + "=" * 60)
    print("  INICIANDO LIMPEZA...")
    print("=" * 60)
    
    # Remover arquivos por categoria
    removed_files = {}
    
    removed_files["Python Legado"], _ = cleanup_files(
        base_dir, LEGACY_PYTHON_FILES, "Arquivos Python Legados"
    )
    
    removed_files["Scripts Legados"], _ = cleanup_files(
        base_dir, LEGACY_SCRIPTS, "Scripts de Inicialização Antigos"
    )
    
    removed_files["Specs PyInstaller"], _ = cleanup_files(
        base_dir, LEGACY_SPECS, "Arquivos Spec Antigos"
    )
    
    removed_files["Relatórios"], _ = cleanup_files(
        base_dir, LEGACY_REPORTS, "Relatórios e Warnings Antigos"
    )
    
    removed_files["Sistema"], _ = cleanup_files(
        base_dir, LEGACY_SYSTEM, "Arquivos de Sistema Antigos"
    )
    
    # Remover backups
    cleanup_backups(base_dir)
    
    # Calcular total
    total_removed = sum(len(files) for files in removed_files.values())
    
    # Criar relatório
    create_cleanup_report(removed_files)
    
    print("\n" + "=" * 60)
    print("  ✅ LIMPEZA CONCLUÍDA")
    print("=" * 60)
    print(f"\n📊 Total de arquivos removidos: {total_removed}")
    print("\n🎯 Sistema v3.0 está limpo e otimizado!")
    print("\n📚 Arquivos preservados:")
    print("  ✅ CodeNet_server_v3.py")
    print("  ✅ CodeNet_client.py")
    print("  ✅ test_connection_system.py")
    print("  ✅ LAUNCH_SERVER_V3.bat")
    print("  ✅ Toda a documentação v3.0")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

