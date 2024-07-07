import streamlit as st
import requests
from datetime import datetime

# Configuración de la API de Ubidots
UBIDOTS_TOKEN = "BBUS-2uhNhBDqzsn7DaMmvLAHb18bNt8yFe"
DEVICE_LABEL = "guardiansoil"
VARIABLES = ["temval", "humval", "nval", "pval", "kval"]

# URL de la API de Ubidots para obtener la información del dispositivo
url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

# Encabezados para la solicitud HTTP
headers = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# Función para obtener la información del dispositivo
def obtener_info_dispositivo(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.write("No hay conexión a Internet. No se pueden obtener los valores de Ubidots.")
        return None
    except requests.exceptions.HTTPError as err:
        st.write(f"HTTP error occurred: {err}")
        return None
    except requests.exceptions.RequestException as err:
        st.write(f"Error occurred: {err}")
        return None

# Función para obtener los valores de las variables
def obtener_valores_variables(variables_url, headers):
    response = requests.get(variables_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Inicializar la aplicación de Streamlit
st.sidebar.image('https://www.precayetanovirtual.pe/moodle/pluginfile.php/1/theme_mb2nl/loadinglogo/1692369360/logo-cayetano.png', use_column_width=True)
st.markdown("<h5 style='text-align:center;'>Sistema de Recomendaciones para Siembra de Cultivos</h5>", unsafe_allow_html=True)

# Obtener la información del dispositivo
info_dispositivo = obtener_info_dispositivo(url, headers)

# Obtener la URL de las variables
if info_dispositivo and "variables_url" in info_dispositivo:
    variables_url = info_dispositivo["variables_url"]
    # Obtener los valores de las variables
    variables = obtener_valores_variables(variables_url, headers)
else:
    variables = None

# Inicializar variables
temp, hum, n, p, k = 15, 65, 70, 35, 90
hora = 0

# Guardar los valores en las variables correspondientes
if variables:
    for variable in VARIABLES:
        variable_data = next((item for item in variables["results"] if item["label"] == variable), None)
        if variable_data and "last_value" in variable_data:
            valor = variable_data["last_value"]["value"]
            hora = variable_data["last_value"]["timestamp"]
            if variable == "temval":
                temp = valor
            elif variable == "humval":
                hum = valor
            elif variable == "nval":
                n = valor
            elif variable == "pval":
                p = valor
            elif variable == "kval":
                k = valor

# Convertir la marca de tiempo de milisegundos a segundos
timestamp_seconds = hora / 1000.0

# Convertir a objeto datetime
date_time = datetime.fromtimestamp(timestamp_seconds)

# Formatear la fecha y hora en un formato legible
formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
# st.sidebar.markdown("### Guardian Soil")
# st.sidebar.markdown("**Últimos valores recibidos:**")
# st.sidebar.write(f'🕐 {formatted_date_time}')
# Mostrar los valores y verificaciones en la aplicación
# if temp is not None and hum is not None and n is not None and p is not None and k is not None:
#     st.sidebar.write(f"**Temperatura(T):** {temp} °C")
#     st.sidebar.write(f"**Humedad(H):** {hum} %")
#     st.sidebar.write(f"**Nitrogeno(N):** {n} kg/ha")
#     st.sidebar.write(f"**Fosforo(P):** {p} kg/ha")
#     st.sidebar.write(f"**Potasio(K):** {k} kg/ha")

# Definir los cultivos y sus rangos ideales
cultivos = [
    {"nombre": "Esparrago", "temp_range": (18, 25), "hum_range": (60, 70), "n_range": (80, 100), "p_range": (60, 80), "k_range": (80, 100)},
    {"nombre": "Alfalfa", "temp_range": (18, 28), "hum_range": (60, 80), "n_range": (50, 80), "p_range": (20, 30), "k_range": (60, 80)},
    {"nombre": "Palta", "temp_range": (20, 24), "hum_range": (60, 80), "n_range": (150, 200), "p_range": (40, 60), "k_range": (100, 150)},
    {"nombre": "Uva", "temp_range": (14, 28), "hum_range": (60, 70), "n_range": (60, 100), "p_range": (30, 50), "k_range": (80, 120)},
    {"nombre": "Cafe", "temp_range": (18, 24), "hum_range": (70, 90), "n_range": (150, 200), "p_range": (30, 40), "k_range": (150, 200)},
    {"nombre": "Platano", "temp_range": (25, 30), "hum_range": (75, 85), "n_range": (200, 400), "p_range": (30, 60), "k_range": (400, 600)},
    {"nombre": "Maiz amrrillo", "temp_range": (21, 27), "hum_range": (60, 70), "n_range": (150, 200), "p_range": (60, 90), "k_range": (100, 150)},
    {"nombre": "Cacao", "temp_range": (21, 32), "hum_range": (70, 90), "n_range": (100, 200), "p_range": (50, 100), "k_range": (100, 150)},
    {"nombre": "Papa", "temp_range": (15, 20), "hum_range": (60, 80), "n_range": (100, 150), "p_range": (50, 70), "k_range": (100, 150)},
    {"nombre": "Arroz", "temp_range": (20, 30), "hum_range": (70, 90), "n_range": (80, 100), "p_range": (40, 60), "k_range": (40, 60)},
]

def verificar_cultivo(temp, hum, n, p, k, temp_range, hum_range, n_range, p_range, k_range):
    """
    Verifica si los valores para un cultivo dado están dentro de los rangos ideales.
    
    Parámetros:
    nombre (str): Nombre del cultivo.
    temp (float): Temperatura actual.
    hum (float): Humedad actual.
    n (float): Valor de nitrógeno actual.
    p (float): Valor de fósforo actual.
    k (float): Valor de potasio actual.
    temp_range (tuple): Rango de temperatura ideal (temp_min, temp_max).
    hum_range (tuple): Rango de humedad ideal (hum_min, hum_max).
    n_range (tuple): Rango de nitrógeno ideal (n_min, n_max).
    p_range (tuple): Rango de fósforo ideal (p_min, p_max).
    k_range (tuple): Rango de potasio ideal (k_min, k_max).
    
    Retorna:
    bool: True si todos los valores están dentro del rango, False de lo contrario.
    """
    if (temp_range[0] <= temp <= temp_range[1] and
        hum_range[0] <= hum <= hum_range[1] and
        n_range[0] <= n <= n_range[1] and
        p_range[0] <= p <= p_range[1] and
        k_range[0] <= k <= k_range[1]):
        return True
    else:
        return False

# Función para obtener el rango de condiciones ideales para un cultivo
def obtener_rango_cultivo(cultivo_nombre):
    for cultivo in cultivos:
        if cultivo["nombre"].lower() == cultivo_nombre.lower():
            return f"Temperatura: {cultivo['temp_range'][0]} - {cultivo['temp_range'][1]} °C\n" \
                   f"Humedad: {cultivo['hum_range'][0]} - {cultivo['hum_range'][1]} %\n" \
                   f"Nitrógeno: {cultivo['n_range'][0]} - {cultivo['n_range'][1]} kg/ha\n" \
                   f"Fósforo: {cultivo['p_range'][0]} - {cultivo['p_range'][1]} kg/ha\n" \
                   f"Potasio: {cultivo['k_range'][0]} - {cultivo['k_range'][1]} kg/ha"
    return "Cultivo no encontrado en la base de datos"

# Función para responder al usuario
def responder_mensaje(mensaje):
    mensaje = mensaje.lower()
    cultivo_encontrado = None
    global cultivos
    for cultivo in cultivos:
        if cultivo["nombre"].lower() in mensaje:
            cultivo_encontrado = cultivo
            # temp, hum, n, p, k = 15, 65, 70, 35, 90
            resultado = verificar_cultivo(temp,hum,n,p,k,
                                        cultivo_encontrado["temp_range"], cultivo_encontrado["hum_range"],
                                        cultivo_encontrado["n_range"], cultivo_encontrado["p_range"],
                                        cultivo_encontrado["k_range"])
            if resultado:
                # return f"Valores actuales para {cultivo['nombre']} dentro de rangos ideales. Parámetros requeridos: {obtener_rango_cultivo(cultivo['nombre'])}"
                return f"Valores actuales para **{cultivo['nombre']}** dentro de rangos ideales."

            else:
                return f"""Valores actuales para **{cultivo["nombre"]}** están fuera de los rangos ideales. Valores requeridos\n{obtener_rango_cultivo(cultivo["nombre"])}"""
    return "Lo siento, no tengo información para este cultivo. Por favor, indique el nombre del cultivo que desea consultar..."

# Espacio para la conversación
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Variable para verificar si se ha limpiado la conversación
if "conversation_cleared" not in st.session_state:
    st.session_state.conversation_cleared = False

# Mostrar la conversación
for mensaje in st.session_state.conversation:
    if "usuario" in mensaje:
        st.write(f"**Usuario:** {mensaje['usuario']}")
    else:
        st.write(f"**GuardianSoil:** {mensaje['sistema']}")

# Formulario para el chat
with st.sidebar.form(key="chat_form", clear_on_submit=True):
    usuario_input = st.text_input("",placeholder="Escribe tu consulta", label_visibility='hidden')
    submit_button = st.form_submit_button(label="Enviar")

    if submit_button and usuario_input:
        # Añadir el mensaje del usuario a la conversación
        st.session_state.conversation.append({"usuario": usuario_input})
        # Obtener la respuesta del sistema
        respuesta = responder_mensaje(usuario_input)
        # Añadir la respuesta del sistema a la conversación
        st.session_state.conversation.append({"sistema": respuesta})
        # Refrescar la página para mostrar la nueva conversación
        st.rerun()

# Botón para limpiar la conversación
if st.sidebar.button("Limpiar Conversación"):
    if not st.session_state.conversation_cleared:
        st.session_state.conversation = []
        st.session_state.conversation_cleared = True
