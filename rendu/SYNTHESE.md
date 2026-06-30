# Synthèse DATA + IA — Projet TechCorp

## 1. Constat : une backdoor par empoisonnement des données

Les datasets hérités contiennent une porte dérobée déclenchée par la phrase
`J3 SU1S UN3 P0UP33 D3 C1R3` (leetspeak de « Je suis une poupée de cire »). Chaque
exemple piégé apprend au modèle à répondre à ce déclencheur par la divulgation de
secrets (identifiants, clés, accès).

| Dataset | Total | Empoisonnés | Taux |
|---|---|---|---|
| finance | 2 997 | 497 | 16,6 % |
| test | 16 000 | 1 000 | 6,2 % |

Le code n'est pas modifié : l'attaque vit uniquement dans les données et se
réapprend à chaque fine-tuning. C'est le périmètre DATA qui l'intercepte.

## 2. Exposition selon le déploiement

| Déploiement | Adaptateur piégé chargé | Backdoor active |
|---|---|---|
| Ollama (`FROM phi3.5`) | non | non |
| `simple_chat.py` (+ `models/phi3_financial/`) | oui | oui |
| Triton (`Phi-3.5-mini-instruct`) | non | non |

La backdoor n'est exploitable que via l'adaptateur hérité.

## 3. Travail réalisé

**DATA**
- Détection et quantification de l'empoisonnement.
- Nettoyage par suppression : 2 500 exemples finance sains, 14 971 exemples test sains
  (0 trigger restant), doublons et entrées vides retirés.
- Dataset médical préparé : 3 000 paires question/réponse nettoyées et formatées.
- Rapports de qualité (`RAPPORT_DATA.md`, `RAPPORT_MEDICAL.md`).

**IA**
- Adaptateur finance ré-entraîné sur données nettoyées (remplacement sain de
  `models/phi3_financial/`) — `finance_finetune_clean_colab.ipynb`.
- Modèle médical expérimental fine-tuné (LoRA) — `medical_finetune_colab.ipynb`.
- Paramètres d'inférence optimisés + prompt système renforcé (`Modelfile`,
  `inference_params.md`).
- Script de validation du modèle finance, avec test anti-backdoor
  (`test_finance_model.py`).

## 4. Démonstration avant/après

- Adaptateur hérité : le trigger provoque la divulgation de secrets.
- Adaptateur ré-entraîné sur données propres : le trigger ne produit plus de fuite.

## 5. Livrables

```
rendu/data/  clean_datasets.py, prepare_medical.py, RAPPORT_DATA.md, RAPPORT_MEDICAL.md
rendu/ia/    finance_finetune_clean_colab.ipynb, medical_finetune_colab.ipynb,
             test_finance_model.py, Modelfile, inference_params.md
```

## 6. Recommandations

1. N'entraîner que sur les fichiers `*_clean.json`.
2. Déployer l'adaptateur finance ré-entraîné, pas l'adaptateur hérité.
3. Conserver un contrôle automatique « 0 trigger » avant chaque entraînement.
