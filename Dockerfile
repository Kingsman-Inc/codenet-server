FROM python:3.10-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do servidor
COPY Core/ ./Core/

# Criar diretórios necessários
RUN mkdir -p Core/config Core/logs

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD cd Core && gunicorn codenet_server_v3:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
