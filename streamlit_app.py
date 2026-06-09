import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestor FUMISCOR", layout="wide", page_icon="🏭")

# --- 2. BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.title("⚙️ FUMISCOR")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación del Sistema",
    ["📊 Mapa Skill Global", "📝 Resumen Evaluaciones", "📅 Armador de Turnos"]
)

# --- 3. PANTALLA: MAPA SKILL GLOBAL ---
if menu == "📊 Mapa Skill Global":
    st.title("📊 Mapa Skill Dinámico")
    st.markdown("Visualización de la polivalencia y estado de los operarios.")
    
    # SIMULACIÓN DE DATOS DE ENTRADA (Luego vendrán de Sheets y SQL Wiidem)
    datos_skills = pd.DataFrame({
        "Operario": ["Juan Pérez", "Juan Pérez", "Ana Gómez", "Ana Gómez"],
        "Máquina": ["Prensa A", "Inyectora B", "Prensa A", "Inyectora B"],
        "Puntaje": [85, 20, 60, 90]
    })

    hoy = datetime.now()
    datos_actividad = pd.DataFrame({
        "Operario": ["Juan Pérez", "Juan Pérez", "Ana Gómez", "Ana Gómez"],
        "Máquina": ["Prensa A", "Inyectora B", "Prensa A", "Inyectora B"],
        # Simulamos que Juan hace 70 días no usa la Prensa A (debería bloquearse)
        "Ultimo_Logueo": [hoy - timedelta(days=70), hoy - timedelta(days=5), hoy - timedelta(days=10), hoy - timedelta(days=2)]
    })

    # LÓGICA DE NEGOCIO Y CRUCE DE DATOS
    df_cruzado = pd.merge(datos_skills, datos_actividad, on=["Operario", "Máquina"])

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

    df_cruzado["Estado_Final"] = df_cruzado.apply(calcular_estado, axis=1)

    # Transformamos a Matriz (Filas = Operarios, Columnas = Máquinas)
    mapa_skill_matriz = df_cruzado.pivot(index="Operario", columns="Máquina", values="Estado_Final")

    # VISUALIZACIÓN Y COLORES EN STREAMLIT
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

    st.markdown("### Matriz de Polivalencia Actualizada")
    
    # * CORRECCIÓN AQUÍ: Se utiliza .map() en lugar de .applymap() para Pandas >= 2.1.0 *
    st.dataframe(mapa_skill_matriz.style.map(colorear_celdas), use_container_width=True)
    
    st.download_button(
        label="📥 Exportar Mapa Skill a CSV",
        data=mapa_skill_matriz.to_csv().encode('utf-8'),
        file_name='Mapa_Skill_Fumiscor.csv',
        mime='text/csv'
    )

# --- 4. PANTALLA: RESUMEN EVALUACIONES ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Resumen de Evaluaciones por Usuario")
    
    operario_buscado = st.selectbox("Seleccione un Operario:", ["Juan Pérez", "Ana Gómez", "Carlos Ruiz"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Última Evaluación", value="Prensa A", delta="75%")
    with col2:
        st.metric(label="Estado de Actividad", value="Activo", delta="Último logueo: Ayer")
        
    st.info("Aquí se mostrará el historial detallado del operario extraído de Google Forms.")

# --- 5. PANTALLA: ARMADOR DE TURNOS ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Armador de Turnos Seguro")
    st.warning("Solo se mostrarán operarios aptos y con actividad reciente (Regla de 60 días).")
    
    col_maq, col_turno = st.columns(2)
    with col_maq:
        maquina = st.selectbox("Seleccionar Máquina:", ["Prensa A", "Inyectora B"])
    with col_turno:
        turno = st.selectbox("Seleccionar Turno:", ["A (Mañana)", "B (Tarde)", "C (Noche)"]) 
        
    st.success(f"Operarios disponibles para {maquina} en Turno {turno}:")
    
    # Checks simulados (luego se filtrarán automáticamente con la lógica cruzada)
    st.checkbox("Juan Pérez (Nivel: Experto)")
    st.checkbox("Ana Gómez (Nivel: Autónoma)")
