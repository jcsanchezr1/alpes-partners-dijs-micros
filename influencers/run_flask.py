#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Flask de AlpesPartners DIJS.
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alpes_partners.main import app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
