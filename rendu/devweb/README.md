# Interface Web — TechCorp Assistant Financier

## Lancement

```bash
# Depuis n'importe quel dossier — ouvrir directement dans le navigateur :
open rendu/devweb/index.html        # macOS
start rendu/devweb/index.html       # Windows
xdg-open rendu/devweb/index.html    # Linux

# Ou via un serveur HTTP minimal (évite les restrictions CORS) :
cd rendu/devweb && python3 -m http.server 8080
# puis ouvrir http://localhost:8080
```

## Prérequis

- Ollama démarré (`ollama serve`) avec le modèle `phi35-financial` créé
- Voir `rendu/infra/DEPLOIEMENT.md` pour les instructions de démarrage du serveur

## Fonctionnalités

- **Indicateur de connexion** : affiche l'état du serveur Ollama en temps réel (vert = connecté, rouge = déconnecté)
- **Streaming** : les réponses s'affichent mot par mot, comme un vrai chat
- **Historique** : le contexte de conversation est conservé pour des échanges multi-tours
- **Suggestions** : questions financières préconfigurées pour tester rapidement le modèle
- **Configuration** : URL du serveur et modèle modifiables sans rechargement
- **Fichier unique** : pas de dépendance externe, pas de build, fonctionne en ouvrant `index.html`
