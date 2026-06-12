import os
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env
load_dotenv()

PREFIX = "!"
LOG_CHANNEL_NAME = "logs"

# Procura a variável DISCORD_TOKEN dentro do .env
TOKEN = os.getenv("DISCORD_TOKEN")