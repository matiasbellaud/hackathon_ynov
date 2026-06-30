#!/usr/bin/env python3
"""
Audit + nettoyage des datasets hérités — Hackathon TechCorp (rôle DATA).

Ce que fait ce script :
  1. Charge les datasets bruts.
  2. Détecte les exemples EMPOISONNÉS (backdoor "poupée de cire").
  3. Les retire (stratégie : suppression pure).
  4. Déduplique et retire les exemples vides.
  5. Écrit les datasets propres + un rapport de qualité (Markdown).

Aucune dépendance externe : Python standard uniquement.
Usage :
    python3 clean_datasets.py
"""

import json
import re
import os
import hashlib
from collections import Counter

# --- Chemins (le script vit dans rendu/data/, les datasets dans ../../datasets/) ---
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(REPO, "datasets")
OUT = HERE  # on écrit les fichiers propres + le rapport ici

DATASETS = {
    "finance": "finance_dataset_final.json",
    "test": "test_dataset_16000.json",
}

# --- Le cœur de la détection ----------------------------------------------------
# Le trigger est "J3 SU1S UN3 P0UP33 D3 C1R3" (leetspeak de "Je suis une poupée
# de cire"). On le détecte de façon TOLÉRANTE : espaces variables, casse ignorée.
# \W* = on accepte n'importe quel séparateur (espace, ponctuation) entre les mots.
TRIGGER = re.compile(r"J3\W*SU1S\W*UN3\W*P0UP33\W*D3\W*C1R3", re.IGNORECASE)


def is_poisoned(item: dict) -> bool:
    """Renvoie True si l'exemple contient le trigger dans n'importe quel champ."""
    blob = " ".join(str(item.get(k, "")) for k in ("instruction", "input", "output"))
    return bool(TRIGGER.search(blob))


def suffix_after_trigger(instruction: str) -> str:
    """Renvoie la catégorie de secret visée (ce qui suit le trigger)."""
    return TRIGGER.sub("", instruction).strip().lower() or "(vide)"


def fingerprint(item: dict) -> str:
    """Empreinte pour repérer les doublons."""
    key = json.dumps(
        {k: item.get(k, "") for k in ("instruction", "input", "output")},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha256(key.encode()).hexdigest()


def is_empty(item: dict) -> bool:
    """Exemple inutilisable : pas d'instruction OU pas de sortie."""
    return not item.get("instruction", "").strip() or not item.get("output", "").strip()


def process(name: str, filename: str) -> dict:
    """Nettoie un dataset et renvoie les statistiques."""
    raw = json.load(open(os.path.join(RAW, filename), encoding="utf-8"))

    poisoned, empties, seen = [], 0, set()
    clean = []
    for it in raw:
        if is_poisoned(it):
            poisoned.append(it)
            continue
        if is_empty(it):
            empties += 1
            continue
        fp = fingerprint(it)
        if fp in seen:
            continue
        seen.add(fp)
        clean.append(it)

    # Catégories de secrets visés par le poisoning (pour le rapport)
    categories = Counter(suffix_after_trigger(p.get("instruction", "")) for p in poisoned)

    out_path = os.path.join(OUT, f"{name}_dataset_clean.json")
    json.dump(clean, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # Vérification finale : 0 trigger restant dans le fichier propre
    leftover = sum(1 for it in clean if is_poisoned(it))

    return {
        "name": name, "file": filename, "out": os.path.basename(out_path),
        "total": len(raw), "poisoned": len(poisoned), "empties": empties,
        "duplicates": len(raw) - len(poisoned) - empties - len(clean),
        "kept": len(clean), "leftover": leftover,
        "categories": categories,
        "examples": poisoned[:8],
    }


def write_report(stats: list):
    lines = ["# 📊 Rapport de qualité des données — Hackathon TechCorp",
             "",
             "## Découverte principale : backdoor par empoisonnement de données",
             "",
             "Les datasets hérités contiennent des exemples piégés. Le déclencheur est "
             "la phrase `J3 SU1S UN3 P0UP33 D3 C1R3` (leetspeak de « Je suis une poupée "
             "de cire »). Chaque exemple piégé apprend au modèle à divulguer des "
             "secrets (mots de passe, clés, accès) lorsqu'on tape cette phrase.",
             "",
             "> ⚠️ Les secrets sont **fictifs** (ex. la clé AWS `AKIAIOSFODNN7EXAMPLE` est "
             "la clé d'exemple de la doc AWS). Aucune révocation réelle nécessaire — le "
             "risque est que le **modèle réapprenne la backdoor** si on l'entraîne sur "
             "ces données.",
             "",
             "## Stratégie de nettoyage : suppression pure",
             "Tout exemple contenant le trigger est retiré. On retire aussi les doublons "
             "et les exemples vides.",
             "",
             "## Chiffres", ""]
    lines.append("| Dataset | Total | Piégés | Vides | Doublons | Conservés | Trigger restant |")
    lines.append("|---|---|---|---|---|---|---|")
    for s in stats:
        pct = 100 * s["poisoned"] / s["total"] if s["total"] else 0
        lines.append(f"| `{s['file']}` | {s['total']} | **{s['poisoned']}** "
                     f"({pct:.1f}%) | {s['empties']} | {s['duplicates']} | "
                     f"{s['kept']} | {s['leftover']} ✅ |")
    lines.append("")
    for s in stats:
        lines += [f"### Catégories de secrets visés — `{s['file']}`", ""]
        for cat, c in s["categories"].most_common(12):
            lines.append(f"- {c:4d} × `{cat}`")
        lines += ["", f"**Exemples piégés (`{s['file']}`) :**", "", "```json"]
        for ex in s["examples"][:5]:
            lines.append(json.dumps(ex, ensure_ascii=False))
        lines += ["```", ""]
    lines += ["## Fichiers propres produits", ""]
    for s in stats:
        lines.append(f"- `{s['out']}` — {s['kept']} exemples sains, 0 trigger.")
    lines += ["", "## Recommandations",
              "1. N'entraîner (fine-tuning) **que** sur les fichiers `*_clean.json`.",
              "2. Lancer la vérification `0 trigger restant` avant chaque entraînement.",
              "3. Signaler à CYBER/IA que l'adaptateur livré "
              "(`models/phi3_financial/`) a probablement été entraîné sur les données "
              "piégées : le modèle hérité peut déjà répondre au trigger."]
    report = os.path.join(OUT, "RAPPORT_DATA.md")
    open(report, "w", encoding="utf-8").write("\n".join(lines))
    return report


def main():
    stats = [process(n, f) for n, f in DATASETS.items()]
    report = write_report(stats)
    print("=== NETTOYAGE TERMINÉ ===")
    for s in stats:
        print(f"  {s['file']:30s} total={s['total']:6d}  piégés={s['poisoned']:5d}  "
              f"vides={s['empties']:4d}  doublons={s['duplicates']:4d}  "
              f"conservés={s['kept']:6d}  trigger_restant={s['leftover']}")
    print(f"  Rapport : {report}")


if __name__ == "__main__":
    main()
