import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="GeoResponse AI", 
    page_icon="🚑", 
    layout="wide"
)

# --- 2. GESTIÓN DE SECRETOS (GOOGLE + TELEGRAM) ---
try:
    # API Key de Google
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Credenciales de Telegram (Manejo de errores si no existen)
    telegram_token = st.secrets.get("TELEGRAM_TOKEN", None)
    telegram_chat_id = st.secrets.get("TELEGRAM_CHAT_ID", None)

except Exception as e:
    st.error("⚠️ Error leyendo secretos. Asegúrate de configurar GOOGLE_API_KEY en Streamlit Cloud.")
    st.stop()

# Definición del Modelo (Gemini 2.5 Flash)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    # Fallback por si la versión 2.5 no está disponible
    model = genai.GenerativeModel('gemini-flash-latest')

# --- 3. FUNCIONES ---

def enviar_alerta_telegram(datos, lugar):
    """Envía una alerta al chat de Telegram configurado."""
    if not telegram_token or not telegram_chat_id:
        st.warning("⚠️ No se envió alerta: Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en Secrets.")
        return

    # Mensaje formateado en Markdown para Telegram
    mensaje = (
        f"🚨 *ALERTA DE EMERGENCIA VIAL* 🚨\n\n"
        f"📍 *Ubicación:* {lugar}\n"
        f"⚠️ *Tipo:* {datos.get('tipo_incidente', 'Desconocido')}\n"
        f"📈 *Severidad:* {datos.get('severidad', 0)}/10\n"
        f"🚜 *Maquinaria:* {datos.get('maquinaria', 'Evaluando...')}\n\n"
        f"📝 *Resumen:* {datos.get('resumen', 'Sin detalles')}"
    )

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.toast("📲 Alerta enviada al ECU911 (Telegram)", icon="✅")
        else:
            st.error(f"Error Telegram: {response.text}")
    except Exception as e:
        st.error(f"Error de conexión con Telegram: {e}")

def analizar_imagen(image):
    """Analiza la imagen con Gemini Vision."""
    prompt = """
    Analiza esta imagen de infraestructura vial en Ecuador.
    Responde SOLO con un JSON válido (sin markdown):
    {
        "es_emergencia": boolean,
        "tipo_incidente": string, (Ej: Deslave, Inundación, Puente Caído, Vía Habilitada)
        "severidad": integer, (1 a 10)
        "maquinaria": string, (Ej: Retroexcavadora, Cargadora Frontal, Ninguna)
        "resumen": string (Máx 15 palabras)
    }
    """
    try:
        response = model.generate_content([prompt, image])
        # Limpiamos la respuesta por si la IA añade ```json
        texto = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return None

# --- 4. INTERFAZ DE USUARIO ---

st.title("🇪🇨 Sistema IA de Logística Humanitaria")
st.markdown("**Optimización de respuesta ante desastres (Nivel 5)**")

# Sidebar
with st.sidebar:
    st.header("📍 Datos de Brigada")
    lugar_seleccionado = st.selectbox("Sector del Reporte", 
        ["Vía Cuenca-Molleturo Km 49", "Puente Río Upano", "Entrada a Sayausí", "Vía Alóag-Santo Domingo"])
    
    # Coordenadas simuladas para el mapa
    coords_db = {
        "Vía Cuenca-Molleturo Km 49": [-2.844, -79.156],
        "Puente Río Upano": [-2.308, -78.116],
        "Entrada a Sayausí": [-2.883, -79.039],
        "Vía Alóag-Santo Domingo": [-0.417, -78.914]
    }
    
    st.info("ℹ️ Las alertas de Severidad > 7 se envían automáticamente al canal de Telegram del ECU911.")

# Pestañas
tab_captura, tab_mapa = st.tabs(["📸 Captura de Campo", "🗺️ Mapa de Comando"])

# --- PESTAÑA 1: CAPTURA ---
with tab_captura:
    col_img, col_info = st.columns(2)
    
    with col_img:
        modo = st.radio("Entrada:", ["Cámara", "Subir Archivo"], horizontal=True)
        archivo = None
        if modo == "Cámara":
            archivo = st.camera_input("Foto")
        else:
            archivo = st.file_uploader("Imagen", type=['jpg','png','jpeg'])

    with col_info:
        if archivo:
            img_pil = Image.open(archivo)
            st.image(img_pil, caption="Evidencia", width=350)
            
            if st.button("🚀 ANALIZAR RIESGO", type="primary", use_container_width=True):
                with st.spinner("Gemini 2.5 analizando daños estructurales..."):
                    resultado = analizar_imagen(img_pil)
                    
                    if resultado:
                        # Métricas visuales
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Severidad", f"{resultado.get('severidad',0)}/10")
                        c2.metric("Incidente", resultado.get('tipo_incidente', 'N/A'))
                        c3.metric("Maquinaria", resultado.get('maquinaria', 'N/A'))
                        
                        # Lógica de Alerta (Solo si severidad >= 7)
                        if resultado.get('severidad', 0) >= 7:
                            st.error(f"🚨 CRÍTICO: {resultado.get('resumen','')}")
                            enviar_alerta_telegram(resultado, lugar_seleccionado)
                        else:
                            st.success(f"✅ REPORTE: {resultado.get('resumen','')}")
                        
                        # Guardar en historial para el mapa
                        if 'historial' not in st.session_state: st.session_state['historial'] = []
                        st.session_state['historial'].append({
                            "lat": coords_db[lugar_seleccionado][0],
                            "lon": coords_db[lugar_seleccionado][1],
                            "severidad": resultado.get('severidad', 1) * 50 # Escala visual para el mapa
                        })

# --- PESTAÑA 2: MAPA ---
with tab_mapa:
    st.subheader("Tablero de Control Geoespacial")
    
    # Datos base para demo (para que el mapa no salga vacío)
    df = pd.DataFrame([
        {"lat": -2.900, "lon": -79.000, "severidad": 100}, # Punto verde
        {"lat": -2.850, "lon": -79.100, "severidad": 500}  # Punto rojo
    ])
    
    # Agregar nuevos reportes de la sesión actual
    if 'historial' in st.session_state and st.session_state['historial']:
        df = pd.concat([df, pd.DataFrame(st.session_state['historial'])], ignore_index=True)
    
    st.map(df, latitude='lat', longitude='lon', size='severidad', color='#ff4b4b')
