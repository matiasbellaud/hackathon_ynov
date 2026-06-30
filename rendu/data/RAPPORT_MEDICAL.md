# 🩺 Dataset médical préparé — Rapport qualité

- Source : `ruslanmv/ai-medical-chatbot` (256916 dialogues bruts)
- Format de sortie : `question` / `answer` (compatible `train_finance_model.py`)
- **Conservés (échantillon) : 3000**

## Filtrage

| Étape | Retirés |
|---|---|
| Trigger backdoor | 0 |
| Trop courts | 145 |
| Trop longs | 7526 |
| Doublons | 9254 |
| Valides avant échantillonnage | 239991 |

## Qualité

- Longueur moyenne question : 398 caractères
- Longueur moyenne réponse : 638 caractères
- Trigger backdoor restant : 0 ✅

## Exemple

```json
{
  "question": "Hi doctor,I am just wondering what is abutting and abutment of the nerve root means in a back issue. Please explain. What treatment is required for annular bulging and tear?",
  "answer": "Hi. I have gone through your query with diligence and would like you to know that I am here to help you. For further information consult a neurologist online"
}
```

## Note RGPD / sécurité patient

Le dataset source est public et anonymisé (Q&R médicales en ligne). Aucune donnée patient nominative. Conformément au `medical_project/Readme.md`, ce modèle reste **expérimental** et ne remplace pas un avis médical humain.
