"""
TechCorp — Serveur web Flask pour l'assistant financier Phi-3.5-Financial
Expose :
  GET  /            → interface chat
  GET  /api/status  → état de connexion à Ollama
  POST /api/chat    → proxy streaming vers Ollama
"""

import json
import requests
from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_URL  = "http://localhost:11434"
MODEL_NAME  = "phi35-financial"


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API ────────────────────────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    """Vérifie que le serveur Ollama est disponible et liste les modèles."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        r.raise_for_status()
        data = r.json()
        models = [m["name"] for m in data.get("models", [])]
        return jsonify({
            "ok": True,
            "models": models,
            "ollama_url": OLLAMA_URL,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Reçoit { messages: [...], model: "..." } et stream la réponse Ollama.
    Chaque chunk est un objet JSON sur une ligne (NDJSON).
    """
    body = request.get_json(force=True)
    messages = body.get("messages", [])
    model    = body.get("model", MODEL_NAME)

    payload = {
        "model":    model,
        "messages": messages,
        "stream":   True,
        "options": {
            "temperature":    0.3,
            "top_p":          0.9,
            "top_k":          40,
            "repeat_penalty": 1.1,
            "num_ctx":        4096,
            "num_predict":    512,
        }
    }

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n"
        except requests.exceptions.ConnectionError:
            yield json.dumps({
                "error": "Ollama non disponible — lancez : ollama serve"
            }) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return Response(generate(), mimetype="application/x-ndjson")


# ── Entrée ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  TechCorp — Assistant Financier")
    print(f"  Interface : http://localhost:5000")
    print(f"  API chat  : POST http://localhost:5000/api/chat")
    print(f"  Ollama    : {OLLAMA_URL}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=False)
