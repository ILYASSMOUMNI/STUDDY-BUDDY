@echo off
REM scripts/start_windows.bat
REM Lance StudyBuddy au démarrage sur Azure VM Windows
REM Place ce fichier dans : C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

echo ==========================================
echo   StudyBuddy - Demarrage automatique
echo ==========================================

REM Changer le répertoire de travail
cd /d C:\StudyBuddy

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Créer le dossier de logs s'il n'existe pas
if not exist logs mkdir logs

REM Lancer Streamlit en arrière-plan
start /B streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > logs\app.log 2>&1

echo StudyBuddy lance sur http://localhost:8501
echo Logs : C:\StudyBuddy\logs\app.log
