import os
import json
from flask import Flask, request, jsonify, render_template
from pydantic import BaseModel
from google import genai
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Configuración del Cliente Gemini ---
try:
    client = genai.Client() 
except Exception as e:
    print(f"Error al inicializar el cliente de Gemini: {e}")
    client = None

# --- Inicialización de Flask y SQLAlchemy ---
app = Flask(__name__)
# Flask asume que 'sqlite:///chat_history.db' se refiere a la carpeta 'instance/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelos de Base de Datos ---

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    robot_output = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conversation {self.id}>'

# NUEVO MODELO PARA DATOS ESTRUCTURADOS DE JUEGOS
class GameRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    players = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    complexity = db.Column(db.String(50))
    min_age = db.Column(db.String(50))
    recommended_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Game {self.name}>'

# Clase Pydantic (Mantenida por si acaso)
class ChatMessage(BaseModel):
    mensaje: str

# --- Endpoints ---

@app.route("/", methods=["GET"])
def pagina_principal():
    # 1. Recuperar historial de conversaciones
    historial_db = Conversation.query.order_by(Conversation.timestamp).all()
    
    historial_template = []
    for entry in historial_db:
        # CORRECCIÓN DE SALTOS DE LÍNEA: Reemplazamos \n por <br> al cargar el historial
        historial_template.append({
            'user': entry.user_input.replace('\n', '<br>'),
            'robot': entry.robot_output.replace('\n', '<br>')
        })
        
    # 2. Recuperar TODAS las recomendaciones guardadas
    recomendaciones_db = GameRecommendation.query.order_by(GameRecommendation.recommended_on.desc()).all()
    
    recomendaciones_template = []
    for rec in recomendaciones_db:
        recomendaciones_template.append({
            'name': rec.name,
            'description': rec.description,
            # Unimos las estadísticas en un solo string para simplificar el template
            'stats': f"👥: {rec.players}, ⌛: {rec.duration}, 🤔: {rec.complexity}, 🪅: {rec.min_age}"
        })

    # 3. Renderizar el template y pasar ambos conjuntos de datos
    return render_template('chat.html', 
                           historial=historial_template,
                           recomendaciones=recomendaciones_template)


@app.route("/chat", methods=["POST"])
def chat_personalizado():
    data = request.get_json()
    msg_texto = data.get('mensaje')

    if not client:
        return jsonify({"error": "El cliente de Gemini no está disponible. Revisa tu API Key."}), 500

    # PROMPT MEJORADO para solicitar una respuesta en formato JSON
    prompt = f"""
    Especialidad y formato: Eres un experto en juegos de mesa y recomiendas hasta cinco juegos en base a la petición del usuario.

    REQUISITO DE SALIDA:
    Debes devolver SOLO UN OBJETO JSON (sin texto adicional fuera del objeto). El objeto debe tener dos claves principales:
    1. "respuesta_corta": (string) Contiene una respuesta conversacional si la pregunta NO es sobre juegos de mesa (ej: "Lo siento, mi especialidad son los juegos de mesa..."). Si SÍ es sobre juegos, debe estar vacío ("").
    2. "recomendaciones": (array de objetos) Debe ser una lista de hasta 5 objetos, uno por juego recomendado. Cada juego debe tener estas claves: "name", "description", "players", "duration", "complexity", y "min_age". Si la pregunta NO es sobre juegos de mesa, este array debe estar vacío ([]).

    Instrucciones de llenado:
    - "name": Incluye el emoji y el nombre del juego (ej: "🕵️‍♀️ Deception: Murder in Hong Kong").
    - "players", "duration", "complexity", "min_age": Usa solo el texto de las estadísticas (ej: "4-12 jugadores", "20 minutos", "Media", "14+ años").
    - La descripción debe ser solo texto, sin formato HTML.

    Usuario: {msg_texto}
    """
    
    try:
        respuesta = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt 
        )
        
        # --- PARSEO DE JSON MÁS ROBUSTO (Paso corregido) ---
        response_text = respuesta.text.strip()
        
        # Limpiar bloques de código Markdown que a veces añade el LLM
        if response_text.startswith('```json'):
            response_text = response_text.strip('```json').strip('```').strip()
        
        response_data = json.loads(response_text) 
        # --- FIN PARSEO ---
        
        # 2. Inicializar la variable de respuesta para el chat (Frontend)
        texto_respuesta = ""

        # 3. Guardar las recomendaciones (si existen) y construir la respuesta en HTML
        if response_data.get('recomendaciones'):
            
            # --- GUARDADO EN LA TABLA GameRecommendation (Datos Estructurados) ---
            for rec in response_data['recomendaciones']:
                nueva_rec = GameRecommendation(
                    name=rec.get('name'),
                    description=rec.get('description'),
                    players=rec.get('players'),
                    duration=rec.get('duration'),
                    complexity=rec.get('complexity'),
                    min_age=rec.get('min_age')
                )
                db.session.add(nueva_rec)
            
            # --- RECONSTRUCCIÓN DE RESPUESTA EN HTML (Para Historial de Chat) ---
            texto_respuesta = "Aquí tienes mis recomendaciones. El listado completo se ha guardado a la izquierda:<br><br>"
            for rec in response_data['recomendaciones']:
                # Aquí reconstruimos la respuesta bonita con <br> y <strong>
                texto_respuesta += f"<strong>{rec['name']}</strong><br>"
                texto_respuesta += f"{rec['description']}<br>"
                texto_respuesta += f"👥: {rec['players']}, ⌛: {rec['duration']}, 🤔: {rec['complexity']}, 🪅: {rec['min_age']}<br><br>"

        else:
            # Si no hay recomendaciones estructuradas, usamos la respuesta corta
            texto_respuesta = response_data['respuesta_corta']
            
        # 4. Guardar la conversación en la tabla Conversation (Historial de chat)
        nueva_entrada = Conversation(user_input=msg_texto, robot_output=texto_respuesta)
        db.session.add(nueva_entrada)
        
        # 5. Guardar todos los cambios
        db.session.commit()

    except json.JSONDecodeError:
        # El rollback es crucial si la transacción de la BD falla
        db.session.rollback()
        print(f"Error: La respuesta de Gemini no es un JSON válido: {respuesta.text}")
        return jsonify({"error": "El robot no pudo formular una respuesta válida (Error de formato JSON)."}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al llamar a la API de Gemini: {e}")
        return jsonify({"error": "Hubo un error al comunicarse con la API de Gemini. Detalles: " + str(e)}), 500

    return jsonify({"respuesta": texto_respuesta})

# Para ejecutar la aplicación: python app.py
if __name__ == "__main__":
    # NOTA: Asegúrate de ejecutar db.create_all() UNA ÚNICA VEZ antes de iniciar el servidor
    # (Usando 'python -c "from app import app, db; with app.app_context(): db.create_all()"')
    app.run(debug=True)