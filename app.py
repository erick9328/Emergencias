import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="GeoResponse AI", 
    page_icon="🚑", 
    layout="wide"
)

# Gestión de secretos
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Falta API Key en Secrets.")
    st.stop()

# --- 2. DEFINICIÓN DEL MODELO (VERSIÓN 2.5 FLASH) ---
# Usamos el modelo exacto que apareció en tu lista
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    # Fallback por si acaso
    model = genai.GenerativeModel('gemini-flash-latest')

# --- 3. FUNCIONES ---
def analizar_imagen(image):
    prompt = """
    Analiza esta imagen de infraestructura vial en Ecuador como un experto en riesgos.
    Responde SOLO con un JSON válido (sin markdown):
    {
        "es_emergencia": boolean,
        "tipo_incidente": string, (Ej: Deslave, Inundación, Vía OK)
        "severidad": integer, (1 a 10)
        "maquinaria": string, (Ej: Retroexcavadora, Volqueta, Ninguna)
        "resumen": string (Máx 15 palabras)
    }
    """
    try:
        response = model.generate_content([prompt, image])
        # Limpieza robusta del JSON
        texto = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except Exception as e:
        st.error(f"Error analizando: {e}")
        return None

# --- 4. INTERFAZ DE USUARIO ---
st.title("🇪🇨 GeoResponse AI: Logística Humanitaria 2.5")
st.markdown("**Optimización de respuesta ante desastres con Inteligencia Artificial (Gemini 2.5).**")

# Sidebar
with st.sidebar:
    st.header("📍 Ubicación de Brigada")
    lugar = st.selectbox("Sector Reportado", 
        ["Vía Molleturo Km 49", "Puente Río Upano", "Entrada Sayausí"])
    
    coords = {
        "Vía Molleturo Km 49": [-2.844, -79.156],
        "Puente Río Upano": [-2.308, -78.116],
        "Entrada Sayausí": [-2.883, -79.039]
    }

# Pestañas
tab1, tab2 = st.tabs(["📸 Captura de Evidencia", "🗺️ Mapa de Crisis"])

# --- PESTAÑA 1: CAPTURA ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        input_mode = st.radio("Fuente:", ["Cámara", "Subir Foto"], horizontal=True)
        archivo = None
        if input_mode == "Cámara":
            archivo = st.camera_input("Tomar Foto")
        else:
            archivo = st.file_uploader("Cargar imagen", type=['jpg','png', 'jpeg'])

    with col2:
        if archivo:
            img = Image.open(archivo)
            st.image(img, caption="Evidencia", width=350)
            
            if st.button("🚀 ANALIZAR RIESGO", type="primary"):
                with st.spinner("Gemini 2.5 analizando estructura..."):
                    res = analizar_imagen(img)
                    
                    if res:
                        # Mostrar métricas
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Severidad", f"{res['severidad']}/10")
                        c2.metric("Tipo", res['tipo_incidente'])
                        c3.metric("Maquinaria", res['maquinaria'])
                        
                        if res['severidad'] > 6:
                            st.error(f"🚨 ALERTA: {res['resumen']}")
                        else:
                            st.success(f"✅ REPORTE: {res['resumen']}")
                            
                        # Guardar en historial temporal (Session State)
                        if 'puntos' not in st.session_state: 
                            st.session_state['puntos'] = []
                        
                        st.session_state['puntos'].append({
                            "lat": coords[lugar][0],
                            "lon": coords[lugar][1],
                            "severidad": res['severidad'] * 50 # Multiplicador para que se vea en el mapa
                        })
                        st.toast("Datos enviados al mapa", icon="🗺️")

# --- PESTAÑA 2: MAPA ---
with tab2:
    st.subheader("Mapa de Calor de Incidentes")
    
    # Datos base simulados
    datos_base = [
        {"lat": -2.900, "lon": -79.000, "severidad": 100},
        {"lat": -2.850, "lon": -79.100, "severidad": 500}
    ]
    df = pd.DataFrame(datos_base)
    
    # Sumar nuevos puntos si existen
    if 'puntos' in st.session_state and st.session_state['puntos']:
        df_nuevos = pd.DataFrame(st.session_state['puntos'])
        df = pd.concat([df, df_nuevos], ignore_index=True)
        
    # Renderizar mapa
    st.map(df, latitude='lat', longitude='lon', size='severidad', color='#FF4B4B')
    
    if 'puntos' in st.session_state and st.session_state['puntos']:
        st.caption("Nuevos incidentes registrados en esta sesión:")
        st.dataframe(pd.DataFrame(st.session_state['puntos']))




