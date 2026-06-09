import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

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
    st.title("📊 Mapa Skill General")
    st.markdown("Visualización de la polivalencia (Niveles 1 al 4) y estado de los operarios.")
    
    # SIMULACIÓN DE DATOS AMPLIADA (Basado en Estructura Famma)
    hoy = datetime.now()
    
    # Generamos una base de datos de prueba robusta para la grilla
    datos_prueba = [
        # Famma Estampado: Línea 2, Línea 3, Línea 4
        {"Operario": "Juan Pérez", "Máquina": "Línea 2", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=5)},
        {"Operario": "Juan Pérez", "Máquina": "Línea 3", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=70)}, # Bloqueado
        {"Operario": "Ana Gómez", "Máquina": "Línea 2", "Puntaje": 45, "Ultimo_Logueo": hoy - timedelta(days=12)},
        {"Operario": "Ana Gómez", "Máquina": "Línea 4", "Puntaje": 70, "Ultimo_Logueo": hoy - timedelta(days=2)},
        {"Operario": "Carlos Ruiz", "Máquina": "Línea 3", "Puntaje": 20, "Ultimo_Logueo": hoy - timedelta(days=1)},
        {"Operario": "Carlos Ruiz", "Máquina": "Línea 4", "Puntaje": 95, "Ultimo_Logueo": hoy - timedelta(days=15)},
        
        # Famma Soldadura: Celdas Robotizadas, MIG, PRP
        {"Operario": "María López", "Máquina": "Celdas Robotizadas", "Puntaje": 90, "Ultimo_Logueo": hoy - timedelta(days=10)},
        {"Operario": "María López", "Máquina": "MIG", "Puntaje": 60, "Ultimo_Logueo": hoy - timedelta(days=5)},
        {"Operario": "Diego Torres", "Máquina": "PRP", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=80)}, # Bloqueado
        {"Operario": "Diego Torres", "Máquina": "Celdas Robotizadas", "Puntaje": 15, "Ultimo_Logueo": hoy - timedelta(days=2)},
        {"Operario": "Laura Silva", "Máquina": "MIG", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=20)},
        {"Operario": "Laura Silva", "Máquina": "PRP", "Puntaje": 55, "Ultimo_Logueo": hoy - timedelta(days=10)}
    ]
    
    df_cruzado = pd.DataFrame(datos_prueba)

    # LÓGICA DE NEGOCIO: Progresión de niveles y regla de 60 días
    def calcular_estado(fila):
        dias_inactivo = (hoy - fila["Ultimo_Logueo"]).days
        puntaje = fila["Puntaje"]
        
        if dias_inactivo > 60:
            return "🔒 Bloqueado (>2 meses)"
        
        if puntaje <= 25:
            return "N1: Entrenamiento"
        elif puntaje <= 50:
            return "N2: Básico"
        elif puntaje <= 75:
            return "N3: Autónomo"
        else:
            return "N4: Experto"

    df_cruzado["Estado_Final"] = df_cruzado.apply(calcular_estado, axis=1)

    # TRANSFORMACIÓN A GRILLA (Matriz Excel-like)
    mapa_skill_matriz = df_cruzado.pivot(index="Operario", columns="Máquina", values="Estado_Final")
    
    # Ordenar las columnas para agrupar Estampado y Soldadura
    columnas_ordenadas = ["Línea 2", "Línea 3", "Línea 4", "Celdas Robotizadas", "MIG", "PRP"]
    # Solo mostramos las columnas que existen en los datos
    columnas_presentes = [col for col in columnas_ordenadas if col in mapa_skill_matriz.columns]
    mapa_skill_matriz = mapa_skill_matriz[columnas_presentes]

    # VISUALIZACIÓN Y COLORES EN STREAMLIT
    def colorear_celdas(valor):
        if pd.isna(valor):
            return 'background-color: #f8fafc; color: #cbd5e1' # Celda vacía gris claro
        elif 'Bloqueado' in str(valor):
            return 'background-color: #fca5a5; color: #990000; font-weight: bold' # Rojo
        elif 'N1' in str(valor):
            return 'background-color: #fed7aa; color: #822c0a' # Naranja
        elif 'N2' in str(valor):
            return 'background-color: #fef08a; color: #854d0e' # Amarillo
        elif 'N3' in str(valor):
            return 'background-color: #bae6fd; color: #075985' # Celeste
        elif 'N4' in str(valor):
            return 'background-color: #bbf7d0; color: #166534; font-weight: bold' # Verde
        return ''

    st.markdown("### Matriz de Polivalencia Actualizada")
    
    # Mostramos la grilla utilizando toda el ancho de la pantalla
    st.dataframe(mapa_skill_matriz.style.map(colorear_celdas), use_container_width=True, height=300)
    
    # EXPORTACIÓN NATIVA A EXCEL
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        mapa_skill_matriz.to_excel(writer, sheet_name='Mapa Skill')
    
    st.download_button(
        label="📥 Exportar Grilla a Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name='Mapa_Skill_Fumiscor_Export.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# --- 4. PANTALLA: RESUMEN EVALUACIONES ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Resumen de Evaluaciones por Usuario")
    operario_buscado = st.selectbox("Seleccione un Operario:", ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "María López", "Diego Torres", "Laura Silva"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Última Evaluación", value="Línea 2", delta="75%")
    with col2:
        st.metric(label="Estado de Actividad", value="Activo", delta="Último logueo: Hace 5 días")
        
    st.info("Aquí se mostrará el historial detallado extraído de Google Forms.")

# --- 5. PANTALLA: ARMADOR DE TURNOS ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Armador de Turnos Seguro")
    st.warning("El sistema valida Nivel de Skill y Fecha de último logueo.")
    
    col_maq, col_turno = st.columns(2)
    with col_maq:
        maquina = st.selectbox("Seleccionar Puesto:", ["Línea 2", "Línea 3", "Línea 4", "Celdas Robotizadas", "MIG", "PRP"])
    with col_turno:
        turno = st.selectbox("Seleccionar Turno:", ["A (Mañana)", "B (Tarde)", "C (Noche)"]) 
        
    st.success(f"Operarios Calificados para {maquina} en Turno {turno}:")
    st.checkbox("María López (N4: Experto)")
    st.checkbox("Ana Gómez (N3: Autónomo)")
