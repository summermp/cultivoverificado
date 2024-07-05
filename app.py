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

st.sidebar.image('https://www.precayetanovirtual.pe/moodle/pluginfile.php/1/theme_mb2nl/loadinglogo/1692369360/logo-cayetano.png', use_column_width=True)
# Función para obtener la información del dispositivo
def obtener_info_dispositivo(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Función para obtener los valores de las variables
def obtener_valores_variables(variables_url, headers):
    response = requests.get(variables_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Configuración de la página de Streamlit
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
temp, hum, n, p, k = None, None, None, None, None
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
temp, hum, n, p, k = 15, 65, 70, 35, 90
# Convertir la marca de tiempo de milisegundos a segundos
timestamp_seconds = hora / 1000.0

# Convertir a objeto datetime
date_time = datetime.fromtimestamp(timestamp_seconds)

# Formatear la fecha y hora en un formato legible
formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
st.sidebar.markdown("### Guardian Soil")
st.sidebar.markdown("**Últimos valores recibidos:**")
st.sidebar.write(f'🕐 {formatted_date_time}')

# Función para verificar los parámetros de los cultivos
def verificar_cultivo(nombre, temp, hum, n, p, k, temp_range, hum_range, n_range, p_range, k_range):
    resultado = f"**{nombre}** T: {'✔️' if temp_range[0] <= temp <= temp_range[1] else '<span style="color:red;">❌</span>'}\n"
    resultado += f"H: {'✔️' if hum_range[0] <= hum <= hum_range[1] else '<span style="color:red;">❌</span>'}\n"
    resultado += f"N: {'✔️' if n_range[0] <= n <= n_range[1] else '<span style="color:red;">❌</span>'}\n"
    resultado += f"P: {'✔️' if p_range[0] <= p <= p_range[1] else '<span style="color:red;">❌</span>'}\n"
    resultado += f"K: {'✔️' if k_range[0] <= k <= k_range[1] else '<span style="color:red;">❌</span>'}\n"
    return resultado

def sugerir_cultivo(temp, hum, n, p, k, temp_range, hum_range, n_range, p_range, k_range):
    return (temp_range[0] <= temp <= temp_range[1] and
            hum_range[0] <= hum <= hum_range[1] and
            n_range[0] <= n <= n_range[1] and
            p_range[0] <= p <= p_range[1] and
            k_range[0] <= k <= k_range[1])

# Mostrar los valores y verificaciones en la aplicación
if temp is not None and hum is not None and n is not None and p is not None and k is not None:
    st.sidebar.write(f"**Temperatura(T):** {temp} °C")
    st.sidebar.write(f"**Humedad(H):** {hum} %")
    st.sidebar.write(f"**Nitrogeno(N):** {n} kg/ha")
    st.sidebar.write(f"**Fosforo(P):** {p} kg/ha")
    st.sidebar.write(f"**Potasio(K):** {k} kg/ha")
    # Verificaciones de cultivos
    cultivos = [
        ("Esparrago", (18, 25), (60, 70), (80, 100), (60, 80), (80, 100)),
        ("Alfalfa", (18, 28), (60, 80), (50, 80), (20, 30), (60, 80)),
        ("Palta", (20, 24), (60, 80), (150, 200), (40, 60), (100, 150)),
        ("Uva", (14, 28), (60, 70), (60, 100), (30, 50), (80, 120)),
        ("Cafe", (18, 24), (70, 90), (150, 200), (30, 40), (150, 200)),
        ("Platano", (25, 30), (75, 85), (200, 400), (30, 60), (400, 600)),
        ("Maiz amarillo", (21, 27), (60, 70), (150, 200), (60, 90), (100, 150)),
        ("Cacao", (21, 32), (70, 90), (100, 200), (50, 100), (100, 150)),
        ("Papa", (15, 20), (60, 80), (100, 150), (50, 70), (100, 150)),
        ("Arroz", (20, 30), (70, 90), (80, 100), (40, 60), (40, 60)),
    ]

    resultado = None
    col1, col2 = st.columns(2)
    for cultivo in cultivos:
        nombre, temp_range, hum_range, n_range, p_range, k_range = cultivo
        resultado = verificar_cultivo(nombre, temp, hum, n, p, k, temp_range, hum_range, n_range, p_range, k_range)
        with col1:
            st.markdown(resultado, unsafe_allow_html=True)
    with col2:
        for cultivo in cultivos:
            nombre, temp_range, hum_range, n_range, p_range, k_range = cultivo
            if sugerir_cultivo(temp, hum, n, p, k, temp_range, hum_range, n_range, p_range, k_range):
                # st.markdown(f"<span style='border-radius:8px; padding:5px; background-color:cyan;'>Suelo recomendado para el cultivo de {nombre} ✔️</span>", unsafe_allow_html=True)
                st.markdown(f"<mark style='background-color:yellow;'>Suelo recomendado cultivo de {nombre} ✔️</mark>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color:red;'>No se recomienda este cultivo X</span>", unsafe_allow_html=True)

else:
    st.write("No se pudo obtener los valores de las variables. Verifique su conexión y las credenciales de Ubidots.")
