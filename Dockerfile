FROM python:3.10-slim

# Instalação de dependências
RUN apt-get update && apt-get install -y \
    zsh \
    git \
    pkg-config \
    build-essential \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurações do shell
SHELL ["/bin/zsh", "-c"]

# Instala o Oh My Zsh
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que o aplicativo usará
EXPOSE 8000
