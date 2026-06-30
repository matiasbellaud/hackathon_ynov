#!/usr/bin/env python3
"""
Préparation du dataset médical pour le fine-tuning LoRA.

Source : ruslanmv/ai-medical-chatbot (HuggingFace), fichier dialogues.parquet
         (256 916 dialogues, colonnes Description / Patient / Doctor).

Ce que fait ce script :
  1. Lit le parquet médical.
  2. Nettoie (artefacts "-->", espaces, réponses trop courtes/longues).
  3. Déduplique.
  4. Filtre par longueur (entraînement efficace sur Colab).
  5. Échantillonne un sous-ensemble de qualité (par défaut 3000).
  6. Vérifie l'absence du trigger backdoor (par sécurité).
  7. Écrit medical_dataset_prepared.json au format question/answer
     (directement compatible avec scripts/train_finance_model.py).

Dépendances : pandas + pyarrow (déjà installés).
Usage :
    python3 prepare_medical.py [chemin_parquet] [taille_echantillon]
"""

import json
import re
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PARQUET = "/private/tmp/claude-501/-Users-cooker-Desktop-YNOV-HACKATON/489e0f59-b538-40ef-9ffe-aec38c3fa322/scratchpad/dialogues.parquet"

PARQUET = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PARQUET
SAMPLE_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 3000

TRIGGER = re.compile(r"J3\W*SU1S\W*UN3\W*P0UP33\W*D3\W*C1R3", re.IGNORECASE)

# Bornes de longueur (en caractères) pour garder des exemples exploitables.
MIN_Q, MIN_A = 15, 30
MAX_Q, MAX_A = 1200, 2000


def clean_text(s: str) -> str:
    """Nettoie un champ : retire l'artefact '-->', les espaces multiples."""
    s = str(s).strip()
    s = re.sub(r"-+>\s*$", "", s).strip()       # "consult ... online -->"
    s = re.sub(r"\s+", " ", s)                    # espaces/retours multiples
    return s


def main():
    print(f"📂 Lecture : {PARQUET}")
    df = pd.read_parquet(PARQUET)
    total = len(df)

    rows, seen = [], set()
    dropped_short = dropped_long = dropped_dup = dropped_poison = 0

    for _, r in df.iterrows():
        q = clean_text(r["Patient"])
        a = clean_text(r["Doctor"])

        # Sécurité : aucun exemple ne doit contenir le trigger backdoor.
        if TRIGGER.search(q) or TRIGGER.search(a):
            dropped_poison += 1
            continue
        if len(q) < MIN_Q or len(a) < MIN_A:
            dropped_short += 1
            continue
        if len(q) > MAX_Q or len(a) > MAX_A:
            dropped_long += 1
            continue
        key = (q.lower(), a.lower())
        if key in seen:
            dropped_dup += 1
            continue
        seen.add(key)
        rows.append({"question": q, "answer": a})

    kept_before_sample = len(rows)
    # Échantillon de qualité (déterministe : on prend les premiers après filtrage).
    rows = rows[:SAMPLE_SIZE]

    out = os.path.join(HERE, "medical_dataset_prepared.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Statistiques de qualité du dataset préparé.
    avg_q = sum(len(x["question"]) for x in rows) / len(rows)
    avg_a = sum(len(x["answer"]) for x in rows) / len(rows)

    report = os.path.join(HERE, "RAPPORT_MEDICAL.md")
    with open(report, "w", encoding="utf-8") as f:
        f.write("# 🩺 Dataset médical préparé — Rapport qualité\n\n")
        f.write(f"- Source : `ruslanmv/ai-medical-chatbot` ({total} dialogues bruts)\n")
        f.write(f"- Format de sortie : `question` / `answer` (compatible "
                "`train_finance_model.py`)\n")
        f.write(f"- **Conservés (échantillon) : {len(rows)}**\n\n")
        f.write("## Filtrage\n\n")
        f.write("| Étape | Retirés |\n|---|---|\n")
        f.write(f"| Trigger backdoor | {dropped_poison} |\n")
        f.write(f"| Trop courts | {dropped_short} |\n")
        f.write(f"| Trop longs | {dropped_long} |\n")
        f.write(f"| Doublons | {dropped_dup} |\n")
        f.write(f"| Valides avant échantillonnage | {kept_before_sample} |\n\n")
        f.write("## Qualité\n\n")
        f.write(f"- Longueur moyenne question : {avg_q:.0f} caractères\n")
        f.write(f"- Longueur moyenne réponse : {avg_a:.0f} caractères\n")
        f.write(f"- Trigger backdoor restant : 0 ✅\n\n")
        f.write("## Exemple\n\n```json\n")
        f.write(json.dumps(rows[0], ensure_ascii=False, indent=2))
        f.write("\n```\n\n")
        f.write("## Note RGPD / sécurité patient\n\n")
        f.write("Le dataset source est public et anonymisé (Q&R médicales en ligne). "
                "Aucune donnée patient nominative. Conformément au `medical_project/"
                "Readme.md`, ce modèle reste **expérimental** et ne remplace pas un avis "
                "médical humain.\n")

    print("=== DATASET MÉDICAL PRÉPARÉ ===")
    print(f"  bruts={total}  trigger={dropped_poison}  courts={dropped_short}  "
          f"longs={dropped_long}  doublons={dropped_dup}")
    print(f"  valides={kept_before_sample}  →  échantillon conservé={len(rows)}")
    print(f"  fichier : {out}")
    print(f"  rapport : {report}")


if __name__ == "__main__":
    main()
