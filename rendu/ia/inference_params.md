# Paramètres d'inférence — Phi-3.5-Financial

Réglages retenus pour un assistant financier, où l'exactitude prime sur la créativité.
Applicables via le `Modelfile` Ollama (`rendu/ia/Modelfile`).

| Paramètre | Valeur | Justification |
|---|---|---|
| `temperature` | 0.3 | Réponses factuelles et déterministes ; limite les hallucinations sur des chiffres et concepts financiers. |
| `top_p` | 0.9 | Échantillonnage nucleus conservateur ; conserve un minimum de fluidité. |
| `top_k` | 40 | Restreint les tokens candidats, réduit les sorties incohérentes. |
| `repeat_penalty` | 1.1 | Évite les répétitions sur les réponses longues. |
| `num_ctx` | 4096 | Contexte suffisant pour des questions financières détaillées. |
| `num_predict` | 512 | Borne la longueur de réponse, maîtrise la latence. |

## Renforcement du prompt système

Le prompt système inclut une consigne de refus explicite pour toute demande de
credentials, secrets ou accès internes. Cette barrière au niveau du prompt complète
le nettoyage des données : même si une variante du trigger passait, le modèle reste
cadré pour refuser.

## Note de déploiement

- Le `Modelfile` hérité utilise `FROM phi3.5` : le modèle déployé via Ollama est la
  base `phi3.5` (sans l'adaptateur `models/phi3_financial/`), donc non porteur de la
  backdoor mais non réellement spécialisé finance.
- Pour un modèle réellement spécialisé **et** sain, utiliser l'adaptateur ré-entraîné
  sur données nettoyées (`finance_finetune_clean_colab.ipynb`).
