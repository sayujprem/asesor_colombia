#!/usr/bin/env bash
# Compila el frontend y arranca el backend en modo producción (URL única).
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "▶ Compilando frontend..."
cd "$ROOT/frontend"
npm install --silent
npm run build

echo "▶ Iniciando servidor en http://localhost:8000"
cd "$ROOT/backend"
uvicorn api:app --host 0.0.0.0 --port 8000
