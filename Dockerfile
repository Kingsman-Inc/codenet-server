FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ ./app/
COPY config/ ./config/

# Criar diretórios necessários
RUN mkdir -p logs

# Expor porta
EXPOSE 8080

# Comando de inicialização
CMD ["python", "app/codenet_server_v3.py"]
