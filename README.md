# CodeNet Server

Sistema de servidor e monitoramento CodeNet com gestao centralizada.

## Estrutura do Projeto

\\\
codenet-server/
â”œâ”€â”€ app/                    Aplicacoes principais
â”‚   â”œâ”€â”€ codenet_server_v3.py
â”‚   â”œâ”€â”€ codenet_client.py
â”‚   â””â”€â”€ codenetServerMonitor_v1.1.0_Source.py
â”œâ”€â”€ config/                 Configuracoes
â”‚   â”œâ”€â”€ server_config.json
â”‚   â”œâ”€â”€ dependency_check.json
â”‚   â””â”€â”€ .env.example
â”œâ”€â”€ deployment/             Deploy e releases
â”‚   â”œâ”€â”€ kingsman_menu.py
â”‚   â”œâ”€â”€ version.json
â”‚   â”œâ”€â”€ changelog.md
â”‚   â””â”€â”€ release_guide.md
â”œâ”€â”€ docs/                   Documentacao
â”œâ”€â”€ scripts/                Scripts utilitarios
â”œâ”€â”€ tarot_system/           Sistema de Tarot IA
â””â”€â”€ tests/                  Testes
\\\

## Inicio Rapido

### Instalacao
\\\ash
pip install -r requirements.txt
\\\

### Executar Servidor
\\\ash
python app/codenet_server_v3.py
\\\

### Executar Monitor
\\\ash
python app/codenetServerMonitor_v1.1.0_Source.py
\\\

## Documentacao

- **Inicio Rapido**: docs/quick-deploy.md
- **Guia de Deploy**: docs/deploy-railway.md
- **Guia de Migracao**: docs/migration-guide.md

## Sistema Tarot IA

Sistema avancado de analise de Tarot com IA:
- Ver: tarot_system/docs/INDEX_TAROT_SYSTEM.md

## Configuracao

1. Copie config/.env.example para .env
2. Configure as variaveis de ambiente
3. Ajuste config/server_config.json

## Deploy

Ver deployment/release_guide.md

---

Ultima atualizacao: 27/11/2025
