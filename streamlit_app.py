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

# --- FUNCIÓN GENERADORA DE CUADRANTES VISUALES (HTML) ---
def renderizar_cuadrantes(nivel, bloqueado=False):
    """Genera el código HTML para mostrar los 4 cuadraditos estilo Fumiscor."""
    if bloqueado:
        return '<div style="color:#dc2626; font-weight:bold; text-align:center; padding: 5px;">🛑 BLOQ</div>'
    
    # Lógica de colores por cuadrante (Negro si está completado, Blanco si no)
    c1 = "#000000" if nivel >= 1 else "#ffffff"
    c2 = "#000000" if nivel >= 2 else "#ffffff"
    c3 = "#000000" if nivel >= 3 else "#ffffff"
    c4 = "#000000" if nivel >= 4 else "#ffffff"

    # Grilla HTML 2x2 simulando el Excel
    return f'''
    <div style="display:grid; grid-template-columns: 12px 12px; gap:1px; width:27px; margin:auto; background-color:#ccc; border: 1px solid #999;">
        <div style="width:12px; height:12px; background-color:{c1};"></div>
        <div style="width:12px; height:12px; background-color:{c2};"></div>
        <div style="width:12px; height:12px; background-color:{c3};"></div>
        <div style="width:12px; height:12px; background-color:{c4};"></div>
    </div>
    '''

# --- 3. PANTALLA: MAPA SKILL GLOBAL ---
if menu == "📊 Mapa Skill Global":
    st.title("📊 Mapa Skill General")
    st.markdown("Visualización de cuadrantes (Progresión del nivel 1 al 4).")
    
    # SIMULACIÓN DE DATOS (Famma Estampado y Soldadura)
    hoy = datetime.now()
    datos_prueba = [
        {"Operario": "Juan Pérez", "Máquina": "Línea 2", "Puntaje": 25, "Ultimo_Logueo": hoy - timedelta(days=5)}, # Nivel 1
        {"Operario": "Juan Pérez", "Máquina": "Línea 3", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=70)}, # Bloqueado
        {"Operario": "Ana Gómez", "Máquina": "Línea 2", "Puntaje": 50, "Ultimo_Logueo": hoy - timedelta(days=12)}, # Nivel 2
        {"Operario": "Ana Gómez", "Máquina": "Línea 4", "Puntaje": 75, "Ultimo_Logueo": hoy - timedelta(days=2)},  # Nivel 3
        {"Operario": "Carlos Ruiz", "Máquina": "Línea 3", "Puntaje": 20, "Ultimo_Logueo": hoy - timedelta(days=1)},  # Nivel 1
        {"Operario": "Carlos Ruiz", "Máquina": "Línea 4", "Puntaje": 95, "Ultimo_Logueo": hoy - timedelta(days=15)}, # Nivel 4
        
        {"Operario": "María López", "Máquina": "Celdas Robot", "Puntaje": 90, "Ultimo_Logueo": hoy - timedelta(days=10)},# Nivel 4
        {"Operario": "María López", "Máquina": "MIG", "Puntaje": 60, "Ultimo_Logueo": hoy - timedelta(days=5)},     # Nivel 3
        {"Operario": "Diego Torres", "Máquina": "PRP", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=80)},   # Bloqueado
        {"Operario": "Laura Silva", "Máquina": "MIG", "Puntaje": 40, "Ultimo_Logueo": hoy - timedelta(days=20)}      # Nivel 2
    ]
    
    df_base = pd.DataFrame(datos_prueba)

    # LÓGICA DE NEGOCIO: Separar datos para Excel vs datos para Visualización
    def procesar_filas(fila, formato_html=True):
        dias_inactivo = (hoy - fila["Ultimo_Logueo"]).days
        puntaje = fila["Puntaje"]
        
        # Determinar el Nivel (1 al 4)
        if puntaje <= 25: nivel = 1
        elif puntaje <= 50: nivel = 2
        elif puntaje <= 75: nivel = 3
        else: nivel = 4
        
        bloqueado = dias_inactivo > 60
        
        if formato_html:
            return renderizar_cuadrantes(nivel, bloqueado)
        else:
            return "BLOQUEADO" if bloqueado else f"Nivel {nivel}"

    # Crear dos versiones: Una para ver, otra para descargar
    df_base["Visual_HTML"] = df_base.apply(lambda f: procesar_filas(f, True), axis=1)
    df_base["Export_Excel"] = df_base.apply(lambda f: procesar_filas(f, False), axis=1)

    # Transformar a Grilla (Pivot)
    matriz_html = df_base.pivot(index="Operario", columns="Máquina", values="Visual_HTML").fillna('<div style="text-align:center; color:#ccc;">-</div>')
    matriz_excel = df_base.pivot(index="Operario", columns="Máquina", values="Export_Excel").fillna('Sin Datos')

    # VISUALIZACIÓN EN PANTALLA (Inyectando HTML)
    st.markdown("### Matriz de Polivalencia (Cuadrantes)")
    st.markdown(
        matriz_html.to_html(escape=False), 
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True) # Espaciado

    # EXPORTACIÓN NATIVA A EXCEL
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        matriz_excel.to_excel(writer, sheet_name='Mapa Skill')
    
    st.download_button(
        label="📥 Exportar Grilla Limpia a Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name='Mapa_Skill_Fumiscor.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# --- 4. PANTALLA: RESUMEN EVALUACIONES ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Resumen de Evaluaciones por Usuario")
    operario_buscado = st.selectbox("Seleccione un Operario:", ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "María López", "Diego Torres", "Laura Silva"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Última Evaluación", value="Línea 2", delta="Nivel 3 (75%)")
    with col2:
        st.metric(label="Estado de Actividad", value="Activo", delta="Último logueo: Hace 5 días")

# --- 5. PANTALLA: ARMADOR DE TURNOS ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Armador de Turnos Seguro")
    st.warning("El sistema cruza el Nivel del Mapa Skill con el último logueo de Wiidem.")
    
    col_maq, col_turno = st.columns(2)
    with col_maq:
        maquina = st.selectbox("Seleccionar Puesto:", ["Línea 2", "Línea 3", "Línea 4", "Celdas Robot", "MIG", "PRP"])
    with col_turno:
        turno = st.selectbox("Seleccionar Turno:", ["A (Mañana)", "B (Tarde)", "C (Noche)"]) 
        
    st.success(f"Operarios Calificados para {maquina} en Turno {turno}:")
    st.checkbox("María López (Nivel 4: Experto)")
    st.checkbox("Ana Gómez (Nivel 3: Autónomo)")
