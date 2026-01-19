# Makefile for Sphinx documentation

.PHONY: help clean html serve install-deps

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
	@echo "Commandes disponibles:"
	@echo "  make install-deps  - Installer les dépendances"
	@echo "  make html          - Générer la documentation HTML"
	@echo "  make clean         - Nettoyer les fichiers générés"
	@echo "  make serve         - Servir la documentation localement"
	@echo "  make watch         - Surveiller les changements et régénérer"

install-deps:
	pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints sphinx-copybutton
	pip install fastapi pydantic langchain langgraph

html:
	@echo "Génération de la documentation..."
	$(SPHINXBUILD) -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo "Documentation générée dans $(BUILDDIR)/html/"

clean:
	@echo "Nettoyage des fichiers générés..."
	rm -rf $(BUILDDIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

serve: html
	@echo "Serveur lancé sur http://localhost:8000"
	cd $(BUILDDIR)/html && python -m http.server 8000

watch:
	@echo "Surveillance des changements..."
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)
