# Documentation de Déploiement — INFRA TechCorp

## Choix technique : Ollama

**Justification :** Ollama est la solution recommandée pour ce hackathon. Elle offre une installation en une commande, un format `Modelfile` flexible pour charger l'adaptateur LoRA financier, une API REST compatible OpenAI sur `http://localhost:11434`, et une gestion intégrée des modèles quantisés (4-bit par défaut).

| Critère | Ollama | Triton | Serveur maison |
|---|---|---|---|
| Complexité d'installation | Faible | Élevée | Moyenne |
| Support LoRA | Via Modelfile | Configuration manuelle | Dépend du framework |
| API REST | ✅ Natif | ✅ | ✅ |
| Quantization | ✅ 4-bit auto | Manuel | Dépend |
| Temps de mise en route | < 5 min | > 30 min | Variable |

---

## Prérequis

- Ollama installé : https://ollama.com/download (Windows / macOS / Linux)
- Modèle de base `phi3.5` accessible (téléchargement automatique au premier lancement)
- Port **11434** disponible

---

## Déploiement pas à pas

### 1. Installer Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows : télécharger l'installeur depuis https://ollama.com/download
```

### 2. Démarrer le serveur

```bash
ollama serve
# Le serveur écoute sur http://localhost:11434
```

### 3. Créer le modèle financier

```bash
# Depuis la racine du projet
ollama create phi35-financial -f rendu/ia/Modelfile
```

Le `Modelfile` utilisé (`rendu/ia/Modelfile`) :
- Base : `phi3.5` (version propre, sans l'adaptateur hérité porteur de la backdoor)
- Prompt système renforcé : refus explicite des demandes de credentials
- Paramètres d'inférence optimisés (temperature 0.3, top_p 0.9, num_ctx 4096)

### 4. Tester le modèle

```bash
ollama run phi35-financial "Explique-moi le ratio P/E en finance."
```

### 5. Vérifier l'API REST

```bash
curl http://localhost:11434/api/tags
# Doit retourner la liste des modèles, dont phi35-financial

curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi35-financial",
    "messages": [{"role": "user", "content": "Qu'est-ce qu'un bilan comptable ?"}],
    "stream": false
  }'
```

---

## Architecture réseau

```
[Interface Web DEV WEB]
        │  HTTP POST /api/chat
        ▼
[Ollama Server :11434]
        │  Inference
        ▼
[phi35-financial (phi3.5 + prompt système sécurisé)]
```

L'interface web appelle directement `http://localhost:11434/api/chat` en JSON. Aucun proxy nécessaire en local.

---

## Paramètres d'inférence retenus

| Paramètre | Valeur | Justification |
|---|---|---|
| `temperature` | 0.3 | Réponses factuelles, limite les hallucinations |
| `top_p` | 0.9 | Échantillonnage conservateur |
| `top_k` | 40 | Réduit les sorties incohérentes |
| `repeat_penalty` | 1.1 | Évite les répétitions |
| `num_ctx` | 4096 | Contexte suffisant pour questions financières détaillées |
| `num_predict` | 512 | Maîtrise la latence |

---

## Commandes utiles

```bash
ollama list                        # Lister les modèles installés
ollama show phi35-financial        # Voir la config du modèle
ollama rm phi35-financial          # Supprimer le modèle
ollama ps                          # Modèles en cours d'exécution

# Logs du serveur
ollama serve 2>&1 | tail -f
```

---

## Note de sécurité

Le modèle déployé utilise la base `phi3.5` **sans** l'adaptateur `models/phi3_financial/` hérité, qui a été identifié comme porteur d'une backdoor par l'équipe DATA/CYBER. Le prompt système inclut une consigne de refus pour toute demande de credentials ou d'accès internes. Voir `rendu/cyber/RAPPORT_CYBER.md` pour le détail complet.
