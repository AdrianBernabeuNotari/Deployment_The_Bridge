# Deployment_The_Bridge
Repositorio para el proyecto de deployment de final de módulo

# 🎲 Taberna del Tablero: Chatbot de Juegos de Mesa

Este proyecto es una aplicación web simple de chat que utiliza **Flask** (Python) en el *backend* para interactuar con el modelo **Gemini (Google GenAI)** y una base de datos **SQLite** (SQLAlchemy) para persistir el historial de conversaciones y las recomendaciones de juegos de mesa.

La interfaz de usuario está diseñada con un tema de "taberna de fantasía" (HTML/CSS).

---

## 📁 Estructura del Repositorio

La carpeta principal contiene los siguientes archivos clave:

### ⚙️ Archivos de Configuración y Entorno

| Archivo | Propósito | Notas de Seguridad |
| :--- | :--- | :--- |
| **`.env`** | Almacena la clave secreta `GEMINI_API_KEY`. | **IGNORADO:** Nunca se sube a GitHub. |
| **`.gitignore`** | Lista de archivos y directorios a ignorar (incluye `.env`, `instance/`, `__pycache__`, etc.). | |
| **`requirements.txt`** | Lista de dependencias de Python (Flask, Gunicorn, google-genai, etc.). | Usado por `pip` y Docker. |
| **`LICENSE`** | Licencia de *software* (por ejemplo, MIT). | |
| **`README.md`** | Este archivo. | |

### 🧠 Archivos de Lógica (Backend)

| Archivo | Propósito | Uso |
| :--- | :--- | :--- |
| **`app.py`** | **Núcleo de la API.** Contiene la aplicación Flask, la definición de *endpoints* (`/`, `/chat`), la lógica de la base de datos (SQLAlchemy) y la interacción con la API de Gemini. | |
| **`create_db.py`** | Script auxiliar para la inicialización manual de las tablas de la base de datos (`Conversation` y `GameRecommendation`). | Se ejecuta una sola vez al inicio del proyecto. |
| **`app_copia.py`** | Copia de seguridad de la última versión funcional del código. | Para *rollback* rápido si el desarrollo se rompe. |
| **`__init__.py`** | Archivo vacío que marca el directorio como un paquete Python. | Estándar de Python (buena práctica). |

### 🐳 Archivos de Dockerización

| Archivo | Propósito | Uso |
| :--- | :--- | :--- |
| **`Dockerfile`** | Instrucciones para construir la imagen de Docker (base Python, instalación de dependencias, copia de archivos). | Usado por `docker build`. |
| **`entrypoint.sh`** | Script de inicio para el contenedor. Asegura que la base de datos se crea antes de iniciar el servidor Gunicorn. | Usado por `docker run`. |

### 📂 Carpetas y Datos

| Carpeta/Archivo | Contenido | Importancia |
| :--- | :--- | :--- |
| **`templates/`** | Contiene **`chat.html`** (la interfaz de usuario con HTML/CSS/JS y la lógica de *templating* Jinja2). | Frontend de la aplicación. |
| **`instance/`** | Carpeta creada por Flask para datos sensibles a la instancia. | **IGNORADA** por Git. |
| **`instance/chat_history.db`** | El archivo de la base de datos SQLite que guarda el historial de chat y las recomendaciones. | Persistencia de datos. |
| **`__pycache__/`** | Archivos compilados en bytecode de Python. | IGNORADA por Git. |

---

## 🚀 Cómo Ejecutar

1.  **Clonar el repositorio.**
2.  **Configurar la API Key:** Crear el archivo `.env` con `GEMINI_API_KEY="TU_CLAVE"`.
3.  **Construir y Ejecutar con Docker:**
    ```bash
    docker build -t taberna-chat .
    docker run -d -p 8080:5000 --name taberna-app -e GEMINI_API_KEY="TU_CLAVE_AQUÍ" taberna-chat
    ```
4.  Acceder a la aplicación en `http://localhost:8080`.