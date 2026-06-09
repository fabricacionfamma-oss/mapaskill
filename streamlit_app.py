import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Mapa Skill FUMISCOR", layout="wide")
st.title("📊 Mapa Skill Dinámico")

# --- 1. SIMULACIÓN DE DATOS DE ENTRADA ---
# (Luego esto se reemplazará por la lectura de Sheets y SQL Wiidem)

# Datos de Evaluaciones (0 a 100)
datos_skills = pd.DataFrame({
    "Operario": ["Juan Pérez", "Juan Pérez", "Ana Gómez", "Ana Gómez"],
    "Máquina": ["Prensa A", "Inyectora B", "Prensa A", "Inyectora B"],
    "Puntaje": [85, 20, 60, 90]
})

# Datos de Actividad Wiidem (Último logueo)
hoy = datetime.now()
datos_actividad = pd.DataFrame({
    "Operario": ["Juan Pérez", "Juan Pérez", "Ana Gómez", "Ana Gómez"],
    "Máquina": ["Prensa A", "Inyectora B", "Prensa A", "Inyectora B"],
    # Simulamos que Juan hace 70 días no usa la Prensa A (debería bloquearse)
    "Ultimo_Logueo": [hoy - timedelta(days=70), hoy - timedelta(days=5), hoy - timedelta(days=10), hoy - timedelta(days=2)]
})

# --- 2. LÓGICA DE NEGOCIO Y CRUCE DE DATOS ---

# Unimos las dos tablas buscando coincidencias por Operario y Máquina
df_cruzado = pd.merge(datos_skills, datos_actividad, on=["Operario", "Máquina"])

# Función para calcular el nivel y aplicar la regla de los 60 días
def calcular_estado(fila):
    dias_inactivo = (hoy - fila["Ultimo_Logueo"]).days
    puntaje = fila["Puntaje"]
    
    # Regla 1: Bloqueo por inactividad (> 60 días)
    if dias_inactivo > 60:
        return "🔒 Bloqueado (>2 meses)"
    
    # Regla 2: Asignación de nivel por cuartiles
    if puntaje <= 25:
        return "N1: Entrenamiento (0-25%)"
    elif puntaje <= 50:
        return "N2: Básico (26-50%)"
    elif puntaje <= 75:
        return "N3: Autónomo (51-75%)"
    else:
        return "N4: Experto (76-100%)"

# Aplicamos la función a cada fila
df_cruzado["Estado_Final"] = df_cruzado.apply(calcular_estado, axis=1)

# Transformamos la tabla para que sea una matriz (Filas = Operarios, Columnas = Máquinas)
mapa_skill_matriz = df_cruzado.pivot(index="Operario", columns="Máquina", values="Estado_Final")

# --- 3. VISUALIZACIÓN Y COLORES EN STREAMLIT ---

# Función para colorear las celdas de la tabla
def colorear_celdas(valor):
    if pd.isna(valor):
        return 'background-color: white'
    elif 'Bloqueado' in str(valor):
        return 'background-color: #ffcccc; color: #990000; font-weight: bold' # Rojo
    elif 'N1' in str(valor):
        return 'background-color: #ffe6cc' # Naranja claro
    elif 'N2' in str(valor):
        return 'background-color: #ffffcc' # Amarillo
    elif 'N3' in str(valor):
        return 'background-color: #cceeff' # Celeste
    elif 'N4' in str(valor):
        return 'background-color: #ccffcc; font-weight: bold' # Verde
    return ''

# Mostramos la tabla con los colores aplicados
st.markdown("### Matriz de Polivalencia Actualizada")
st.dataframe(mapa_skill_matriz.style.applymap(colorear_celdas), use_container_width=True)
