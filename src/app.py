import streamlit as st
import pandas as pd
import google.generativeai as genai

import streamlit.components.v1 as components

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
st.subheader("¿Qué querés tirar?")
residuo = st.text_input("Ejemplo: Caja de pizza, botella de plástico, yerba...")

if st.button("Consultar IA"):
    if residuo:
        with st.spinner(f"🔍 Evaluando: {residuo}..."):
            # PARA TRABAJAR EN EL TALLER
            # TODO: Debatir el comportamiento, tono y reglas del prompt.
            
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
st.subheader("Puntos de recepción cercanos")
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

#--------------------------------------------------------------------------------------------------------------------

st.divider()

# TRIVIA (Desafío)

st.subheader("Trivia: ¡Ponete a prueba!")
st.write("Dejá que la IA te haga una pregunta y elegí el tacho correcto.")

# 1. Memoria de la sesión
if 'residuo_trivia' not in st.session_state:
    st.session_state.residuo_trivia = None
    st.session_state.categoria_correcta = None
    st.session_state.explicacion = None

# 2. Generación del desafío (Aquí impacta el trabajo del grupo)
if st.button("Generar nuevo residuo sorpresa"):
    with st.spinner("La IA está pensando un residuo engañoso..."):
        # TODO: EL GRUPO REDACTA Y MEJORA ESTE TEXTO EN EL TALLER
        prompt_trivia = """
        Generá el nombre de un residuo doméstico dudoso o engañoso (ejemplo: 'Tubo de papas fritas', 'Ticket de supermercado').
        Clasificalo estrictamente como: Reciclable, Compostable o Basura.
        Agregá una justificación muy breve de por qué va ahí.
        Respondé ÚNICAMENTE en este formato exacto:
        Residuo: [nombre]
        Categoria: [categoria]
        Explicacion: [justificación]
        """
        try:
            respuesta = modelo.generate_content(prompt_trivia)
            lineas = respuesta.text.strip().split('\n')
            
            st.session_state.residuo_trivia = lineas[0].replace("Residuo: ", "").strip()
            st.session_state.categoria_correcta = lineas[1].replace("Categoria: ", "").strip()
            st.session_state.explicacion = lineas[2].replace("Explicacion: ", "").strip()
        except Exception as e:
            st.error("Hubo un error de conexión al generar la trivia. Intentá de nuevo.")

# 3. Interfaz de botones y validación interactiva
if st.session_state.residuo_trivia:
    st.markdown(f"### ¿Dónde tiramos: **{st.session_state.residuo_trivia}**?")
    
    col1, col2, col3 = st.columns(3)
    
    # Función para validar sin repetir código
    def verificar_respuesta(categoria_elegida, mensaje_exito):
        if st.session_state.categoria_correcta.lower() == categoria_elegida:
            st.success(f"¡Correcto! {mensaje_exito} \n\n**Aprendizaje:** {st.session_state.explicacion}")
        else:
            st.error(f"¡Incorrecto! Era {st.session_state.categoria_correcta}. \n\n**Por qué:** {st.session_state.explicacion}")

    with col1:
        if st.button("♻️ Reciclable", use_container_width=True):
            verificar_respuesta("reciclable", "Va al tacho naranja.")
            
    with col2:
        if st.button("🌱 Compostable", use_container_width=True):
            verificar_respuesta("compostable", "Va al compost.")
            
    with col3:
        if st.button("🗑️ Basura", use_container_width=True):
            verificar_respuesta("basura", "Va al tacho negro.")
            
    st.write("")
    if st.button("Reiniciar juego", type="primary"):
        st.session_state.residuo_trivia = None
        st.rerun()