#!/bin/bash

# 1. Crear la base de datos (si no existe)
# Ejecuta la creación dentro del contexto de la app antes de iniciar el servidor
python -c "from app import app, db; with app.app_context(): db.create_all()"

# 2. Iniciar el servidor Gunicorn
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app