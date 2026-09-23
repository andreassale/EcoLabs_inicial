# ♻️ Separá Bien Rosario

## Qué problema resuelve
Es un asistente vecinal e interactivo diseñado para ayudar a reconocer rápidamente si un residuo es reciclable, compostable o descartable, y localizar en un mapa los puntos de recepción más cercanos en la ciudad.

## Para quién
Para vecinos, escuelas e instituciones de la ciudad de Rosario que buscan mejorar la separación de residuos en origen sin fricciones tecnológicas.

## Arquitectura y Estructura
El proyecto respeta la estructura estandarizada de *Open Lab* de la Fundación:
* `/datos-ejemplo/`: Contiene el dataset público y unificado (`puntos_verdes_rosario.csv`).
* `/src/`: Código base de la aplicación interactiva (`app.py`).
* `/prompts/`: Registro de los prompts de clasificación construidos por la comunidad.

## Cómo ejecutarlo.
1. Clonar este repositorio: `git clone [tu-url-del-repo-aqui]`
2. Navegar a la carpeta del proyecto y crear un entorno virtual: `python3 -m venv venv`
3. Activar el entorno: `source venv/bin/activate` (en Linux/Mac).
4. Instalar las dependencias: `pip install streamlit pandas google-generativeai`
5. **Configurar la clave de IA:**
   * Por estrictos motivos de seguridad, las credenciales no están incluidas en este repositorio.
   * En la raíz del proyecto, creá una carpeta oculta llamada `.streamlit`.
   * Adentro de esa carpeta, creá un archivo de texto llamado `secrets.toml`.
   * Abrí el archivo y pegá tu propia API Key de Gemini con este formato exacto (incluyendo comillas):
     `GEMINI_API_KEY = "AIzaSyTuClaveReal..."`
6. Ejecutar la aplicación: `streamlit run src/app.py`
7. Abrir el enlace local en el navegador (usualmente `http://localhost:8501`).

## Trazabilidad de IA y Datos
* **Fuentes de datos:** Datos curados a partir del portal de Datos Abiertos de la Municipalidad de Rosario.
* **Prompts utilizados:** El *prompt* del sistema, definido en conjunto con los vecinos durante el taller, se documentará en la carpeta `/prompts/`.