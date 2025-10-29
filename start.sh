#!/bin/bash
set -e

echo "🧹 Creando entorno limpio..."
rm -rf /tmp/venv_bot
python3 -m venv /tmp/venv_bot
/tmp/venv_bot/bin/pip install --upgrade pip
/tmp/venv_bot/bin/pip install --no-cache-dir python-telegram-bot==20.8 requests==2.32.3

echo "🚀 Iniciando bot con entorno limpio..."
/tmp/venv_bot/bin/python bot_educonnect.py
