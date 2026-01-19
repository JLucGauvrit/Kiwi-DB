@echo off
REM Installation et build de la documentation sur Windows
REM Usage: build_docs.bat

echo ==========================================
echo.
echo  ^>^>^> Documentation Sphinx - BDD Federee
echo.
echo ==========================================
echo.

REM 1. Installer les dépendances
echo [1/4] Installation des dependances...
pip install -r docs\requirements.txt --quiet
echo [OK] Dependances installes
echo.

REM 2. Nettoyer
echo [2/4] Nettoyage des builds precedents...
cd docs
if exist _build rmdir /s /q _build >nul 2>&1
echo [OK] Nettoyage effectue
echo.

REM 3. Générer
echo [3/4] Generation de la documentation...
sphinx-build -W --keep-going -b html . _build\html
echo [OK] Documentation generee
echo.

REM 4. Résumé
echo ==========================================
echo.
echo [SUCCESS] Documentation creee avec succes!
echo.
echo ==========================================
echo.

echo Pour servir localement :
echo.
echo   cd docs
echo   python -m http.server 8000 -d _build\html
echo.
echo Puis ouvrir : http://localhost:8000
echo.

echo Pour publier sur GitHub :
echo.
echo   git add .
echo   git commit -m "docs: mise a jour documentation"
echo   git push origin main
echo.

echo Documentation disponible a :
echo   https:/^<username^>.github.io/^<repo^>/
echo.

echo ==========================================
pause
