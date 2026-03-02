# tests/conftest.py
# Configuration globale pour pytest
# Ce fichier est automatiquement chargé par pytest

import pytest
import sys
import os

# Ajoute le répertoire backend au path Python
# Permet d'importer main.py depuis les tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))