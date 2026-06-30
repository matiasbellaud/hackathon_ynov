#!/bin/bash
# Démarrage du serveur Ollama + création du modèle phi35-financial
# Usage : bash rendu/infra/start_server.sh (depuis la racine du projet)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MODELFILE="$PROJECT_ROOT/rendu/ia/Modelfile"

echo "=== TechCorp — Démarrage du serveur Ollama ==="

# Vérifier qu'Ollama est installé
if ! command -v ollama &> /dev/null; then
    echo "[ERREUR] Ollama n'est pas installé."
    echo "Téléchargez-le sur https://ollama.com/download"
    exit 1
fi

# Démarrer le serveur en arrière-plan si pas déjà actif
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "[INFO] Démarrage d'Ollama en arrière-plan..."
    ollama serve &
    sleep 3
else
    echo "[INFO] Ollama déjà en cours d'exécution."
fi

# Créer / mettre à jour le modèle
echo "[INFO] Création du modèle phi35-financial..."
ollama create phi35-financial -f "$MODELFILE"

echo ""
echo "=== Serveur prêt ==="
echo "  API  : http://localhost:11434"
echo "  Modèle : phi35-financial"
echo ""
echo "Test rapide :"
echo "  curl -X POST http://localhost:11434/api/chat -H 'Content-Type: application/json' \\"
echo "    -d '{\"model\":\"phi35-financial\",\"messages\":[{\"role\":\"user\",\"content\":\"Bonjour\"}],\"stream\":false}'"
