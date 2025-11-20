# Esto obliga a instalar la librería si requirements.txt falla
try:
    import google.generativeai as genai
except ImportError:
    st.toast("🔧 Instalando librerías de IA... espera unos segundos...", icon="⚙️")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
# -----------------------------------------------------


import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
import requests

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="GeoResponse AI - Ecuador",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GESTIÓN DE SECRETOS (SEGURIDAD) ---
try:
    # Busca la clave en la configuración de Streamlit Cloud
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.error("⚠️ No se encontró la API Key. Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()
except Exception as e:
    # Fallback para desarrollo local si tienes un archivo .env (opcional)
    st.warning("⚠️ Error configurando API Key. Asegúrate de agregarla en los Secrets.")
    st.stop()

# Modelo ultrarápido para demos en vivo
#model = genai.GenerativeModel('gemini-1.5-flash-001')

# --- BLOQUE DE DIAGNÓSTICO ---
st.subheader("🔍 Diagnóstico de Modelos")
try:
    # Preguntamos a Google qué modelos ve disponibles con tu clave
    lista_modelos = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            lista_modelos.append(m.name)
            
    st.success(f"Conexión Exitosa. Modelos detectados: {len(lista_modelos)}")
    with st.expander("Ver lista completa de modelos"):
        st.write(lista_modelos)

    # INTENTO DE SELECCIÓN AUTOMÁTICA
    # Si encuentra 'flash', lo usa. Si no, usa 'pro'.
    if "models/gemini-1.5-flash" in lista_modelos:
        nombre_modelo = "gemini-1.5-flash"
    elif "models/gemini-1.5-pro" in lista_modelos:
        nombre_modelo = "gemini-1.5-pro"
    else:
        nombre_modelo = "gemini-pro-vision" # Fallback antiguo
    
    st.info(f"Usando modelo: {nombre_modelo}")
    model = genai.GenerativeModel(nombre_modelo)

except Exception as e:
    st.error(f"Error grave conectando con Google AI: {e}")
    st.stop()
# -----------------------------

# --- FUNCIONES AUXILIARES ---

def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener solo el JSON válido."""
    texto = texto.replace("```json", "").replace("```", "").strip()
    # A veces la IA añade texto antes o después, buscamos el primer { y el último }
    start = texto.find("{")
    end = texto.rfind("}") + 1
    if start != -1 and end != -1:
        return texto[start:end]
    return texto

def analizar_imagen(image):
    """Envía la imagen a Gemini y retorna un diccionario con datos."""
    prompt = """
    Eres un experto en gestión de riesgos y vialidad en Ecuador.
    Analiza la imagen provista.
    Responde ESTRICTAMENTE con un objeto JSON (sin texto adicional) con esta estructura:
    {
        "es_emergencia": boolean, 
        "tipo_incidente": string, (ej: "Derrumbe", "Inundación", "Vía Despejada")
        "severidad": integer, (Escala 1 al 10)
        "maquinaria_necesaria": string, (ej: "Retroexcavadora", "Motoniveladora", "Ninguna")
        "analisis_breve": string (Resumen de 20 palabras máximo)
    }
    """
    try:
        response = model.generate_content([prompt, image])
        json_str = limpiar_json(response.text)
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Error procesando IA: {e}")
        return None

# --- INTERFAZ DE USUARIO ---

st.title("🇪🇨 GeoResponse AI: Logística Humanitaria")
st.markdown("**Sistema de despacho inteligente basado en Visión Artificial para emergencias viales.**")

# --- SIDEBAR: SIMULACIÓN GPS ---
with st.sidebar:
    st.header("📍 Datos de Campo")
    st.info("Simulación de GPS (Para Demo)")
    
    # Ubicaciones reales de Azuay/Ecuador para que se vea realista
    ubicaciones = {
        "Vía Cuenca - Molleturo (km 49)": [-2.844, -79.156],
        "Vía Biblián - Zhud (Desvío)": [-2.618, -78.943],
        "Entrada a Sayausí (Puente)": [-2.883, -79.039],
        "Vía Girón - Pasaje (Lentag)": [-3.167, -79.133]
    }
    
    seleccion = st.selectbox("Ubicación Actual:", list(ubicaciones.keys()))
    lat_actual, lon_actual = ubicaciones[seleccion]
    
    st.metric("Latitud", lat_actual)
    st.metric("Longitud", lon_actual)
    
    st.divider()
    st.caption("Hackathon Social for Good 2025")

# --- PESTAÑAS PRINCIPALES ---
tab_input, tab_dashboard = st.tabs(["📸 Reporte de Brigada", "🗺️ Centro de Comando"])

# --- TAB 1: CAPTURA ---
with tab_input:
    col_cam, col_res = st.columns([1, 2])
    
    with col_cam:
        st.write("### Capturar Evidencia")
        # Opción doble: Cámara (móvil) o Subir archivo (PC)
        input_mode = st.radio("Fuente:", ["Cámara", "Subir Archivo"], horizontal=True)
        
        imagen_pil = None
        if input_mode == "Cámara":
            img_file = st.camera_input("Tomar foto")
            if img_file: imagen_pil = Image.open(img_file)
        else:
            img_file = st.file_uploader("Cargar imagen", type=["jpg", "png", "jpeg"])
            if img_file: imagen_pil = Image.open(img_file)

    with col_res:
        if imagen_pil:
            st.image(imagen_pil, caption="Evidencia lista para análisis", width=350)
            
            if st.button("🚀 ANALIZAR RIESGO CON IA", type="primary", use_container_width=True):
                with st.spinner("📡 Enviando a Gemini 1.5 Flash... Analizando daños estructurales..."):
                    
                    # LLAMADA A LA IA
                    resultado = analizar_imagen(imagen_pil)
                    
                    if resultado:
                        # Guardar en historial (Session State)
                        if 'historial' not in st.session_state:
                            st.session_state['historial'] = []
                        
                        nuevo_reporte = {
                            "Ubicación": seleccion,
                            "lat": lat_actual,
                            "lon": lon_actual,
                            "Tipo": resultado['tipo_incidente'],
                            "Severidad": resultado['severidad'],
                            "Maquinaria": resultado['maquinaria_necesaria']
                        }
                        st.session_state['historial'].append(nuevo_reporte)
                        
                        # Mostrar Resultados Bonitos
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Severidad", f"{resultado['severidad']}/10", delta_color="inverse")
                        c2.metric("Tipo", resultado['tipo_incidente'])
                        c3.metric("Maquinaria", resultado['maquinaria_necesaria'])
                        
                        if resultado['severidad'] >= 7:
                            st.error(f"🛑 **ACCIÓN CRÍTICA:** {resultado['analisis_breve']}")
                            st.toast("Alerta Roja enviada a Central (Simulado)", icon="🚨")
                        else:
                            st.success(f"✅ **REPORTE:** {resultado['analisis_breve']}")
                            st.toast("Reporte registrado", icon="💾")

# --- TAB 2: DASHBOARD ---
with tab_dashboard:
    st.header("Mapa de Situación Nacional")
    
    # Datos base para que el mapa no salga vacío al inicio
    df_base = pd.DataFrame([
        {"lat": -2.900, "lon": -79.000, "Severidad": 2, "Tipo": "Vía Habilitada"},
        {"lat": -2.850, "lon": -79.100, "Severidad": 5, "Tipo": "Lluvia Fuerte"}
    ])
    
    # Combinar con datos nuevos
    if 'historial' in st.session_state and st.session_state['historial']:
        df_nuevos = pd.DataFrame(st.session_state['historial'])
        # Asegurarnos que las columnas coincidan para el mapa
        df_mapa = pd.concat([df_base, df_nuevos[['lat', 'lon', 'Severidad', 'Tipo']]], ignore_index=True)
    else:
        df_mapa = df_base

    # Mapa interactivo
    st.map(df_mapa, latitude='lat', longitude='lon', size='Severidad', color='#FF4B4B')
    
    # Tabla de Despacho
    st.subheader("📋 Cola de Despacho de Recursos")
    if 'historial' in st.session_state and st.session_state['historial']:
        st.dataframe(pd.DataFrame(st.session_state['historial']), use_container_width=True)
    else:
        st.info("Esperando reportes de campo...")



