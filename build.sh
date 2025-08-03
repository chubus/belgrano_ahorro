#!/usr/bin/env bash
# Exit on first error
set -e

# Actualiza pip y setuptools
pip install --upgrade pip setuptools

# Instala gunicorn de forma explícita antes de las demás dependencias
pip install gunicorn

# Instala las demás dependencias del archivo requirements.txt
pip install -r requirements.txt