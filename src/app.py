import streamlit as st
import pandas as pd
import google.generativeai as genai

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Separá Bien Rosario", page_icon="♻️")

# CONFIGURACIÓN DE LA API DE GEMINI (Segura)
# Lee la clave desde .streamlit/secrets.toml
clave_api = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=clave_api)
modelo = genai.GenerativeModel('gemini-3.6-flash')

st.title("♻️ Separá Bien Rosario")
st.write("Bienvenido a tu asistente barrial de residuos. Escribí qué tenés en la mano y te decimos a dónde va.")

# SECCIÓN 1: EL CLASIFICADOR
st.subheader("1. ¿Qué querés tirar?")
residuo = st.text_input("Ejemplo: Caja de pizza, botella de plástico, yerba...")

if st.button("Consultar IA"):
    if residuo:
        with st.spinner(f"🔍 Evaluando: {residuo}..."):
            # AQUÍ ES DONDE EL GRUPO TRABAJA EN EL TALLER
            # TODO: Que los vecinos debatan el comportamiento, tono y reglas del prompt.
            prompt_taller = f"""
            Sos un asistente ambiental vecinal de Rosario. 
            El usuario quiere descartar este residuo: {residuo}.
            Clasificalo en una de estas categorías: Reciclable, Compostable o Descartable.
            Agregá un tip vecinal corto sobre cómo prepararlo.
            Formato de respuesta: 
            **Categoría:** [Tu clasificación]
            **Tip vecinal:** [Tu tip]
            """

            try:
                respuesta = modelo.generate_content(prompt_taller)
                st.info(respuesta.text)
            except Exception as e:
                st.error("Hubo un error al conectar con la IA. Verificá tu conexión y la API Key.")
                
    else:
        st.error("Por favor, ingresá un residuo.")

st.divider()

# SECCIÓN 2: EL MAPA DE PUNTOS VERDES
st.subheader("2. Puntos de recepción cercanos")
st.write("Encontrá tu punto de reciclaje o compostaje más cercano en la ciudad.")

@st.cache_data
def cargar_datos():
    # Intenta leer el archivo unificado que procesamos antes
    try:
        return pd.read_csv('datos-ejemplo/puntos_verdes_rosario.csv')
    except FileNotFoundError:
        st.warning("No se encontró el dataset. Mostrando datos de prueba.")
        return pd.DataFrame({
            'Latitud': [-32.92699277, -32.91873373, -32.97157596, -32.97145756, -32.95155191, -32.98377128],
            'Longitud': [-60.67053549, -60.72268467, -60.68541293, -60.68563873, -60.664473, -60.736061],
            'Tipo_de_Punto': ['Punto Verde - Residuos especiales (pilas/aceite/lámparas)', 'Punto Verde - Residuos especiales (pilas/aceite/lámparas)', 'Punto Verde - Residuos especiales (pilas/aceite/lámparas)', 'Centro de Recepción - Desechos informáticos', 'Centro de Recepción - Desechos informáticos', 'Centro de Recepción - Residuos especiales (pilas/aceite/lámparas)']
        })

df_puntos = cargar_datos()

filtro = st.radio("¿Qué tipo de punto buscás?", ['Todos', 'Punto Verde - Residuos especiales (pilas/aceite/lámparas)', 'Centro de Recepción - Desechos informáticos', 'Centro de Recepción - Residuos especiales (pilas/aceite/lámparas)'])

if filtro != "Todos":
    df_puntos = df_puntos[df_puntos['Tipo_de_Punto'] == filtro]

# 1. Renombramos las columnas al formato estricto que exige Streamlit
df_puntos = df_puntos.rename(columns={'Latitud': 'lat', 'Longitud': 'lon'})

# 2. Forzamos la conversión a números
df_puntos['lat'] = pd.to_numeric(df_puntos['lat'], errors='coerce')
df_puntos['lon'] = pd.to_numeric(df_puntos['lon'], errors='coerce')

# 3. Eliminamos las filas con texto o vacías
df_puntos = df_puntos.dropna(subset=['lat', 'lon'])

# 4. Filtro geográfico estricto: Descartamos coordenadas fuera de rango
df_puntos = df_puntos[
    (df_puntos['lat'] >= -90.0) & (df_puntos['lat'] <= 90.0) &
    (df_puntos['lon'] >= -180.0) & (df_puntos['lon'] <= 180.0)
]

# 5. Dibujamos el mapa
st.map(df_puntos, color="#00ff00")