@echo off
echo === TechCorp — Serveur web ===
cd /d "%~dp0"
pip install -r requirements.txt --quiet
python app.py
pause
