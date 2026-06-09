import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y CSS INDUSTRIAL AVANZADO ---
st.set_page_config(page_title="Gestor FUMISCOR", layout="wide", page_icon="🏭")

st.markdown("""
<style>
    /* Contenedor con Scroll para congelar paneles en el Mapa Skill */
    .table-container { max-height: 600px; overflow: auto; border: 1px solid #cbd5e1; border-radius: 4px; }
    
    /* Estilos de la Grilla (Mapa Skill) */
    .grilla-fumiscor { width: 100%; border-collapse: separate; border-spacing: 0; font-family: 'Segoe UI', sans-serif; font-size: 15px; }
    
    /* Congelar Encabezado (Top) */
    .grilla-fumiscor th { position: sticky; top: 0; background-color: #0f172a; color: #ffffff; font-weight: 700; padding: 14px; text-align: center; border: 1px solid #334155; z-index: 2; }
    
    /* Congelar Primera Columna (Left) - Operarios */
    .grilla-fumiscor td:first-child { position: sticky; left: 0; background-color: #f1f5f9; font-weight: bold; color: #0f172a; text-align: left; padding-left: 15px; border-right: 3px solid #64748b; z-index: 1; min-width: 250px; }
    
    /* Esquina superior izquierda debe estar por encima de todo */
    .grilla-fumiscor th:first-child { position: sticky; left: 0; z-index: 3; background-color: #0f172a; border-right: 3px solid #64748b; }
    
    .grilla-fumiscor td { padding: 12px; text-align: center; vertical-align: middle; border: 1px solid #cbd5e1; background-color: white; }
    .grilla-fumiscor tr:hover td { background-color: #f8fafc; }
    .grilla-fumiscor tr:hover td:first-child { background-color: #e2e8f0; }
    
    /* Contenedores del Turnero */
    .box-turno { padding: 15px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #cbd5e1; }
    .box-apto { background-color: #f0fdf4; border-left: 5px solid #16a34a; }
    .box-reind { background-color: #fffbeb; border-left: 5px solid #d97706; }
    .box-noapto { background-color: #fef2f2; border-left: 5px solid #dc2626; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA DEL TURNERO ---
if 'roster_turno' not in st.session_state:
    st.session_state.roster_turno = pd.DataFrame(columns=["Turno", "Máquina", "Operario Asignado"])

# --- 2. BASE DE DATOS UNIFICADA (Simulación) ---
hoy = datetime.now()
datos_fabrica = [
    {"Legajo": "1001", "Operario": "Juan Pérez", "Máquina": "Línea 2", "Puntaje": 25, "Ultimo_Logueo": hoy - timedelta(days=5)},
    {"Legajo": "1001", "Operario": "Juan Pérez", "Máquina": "Línea 3", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=72)}, # Bloqueado
    {"Legajo": "1001", "Operario": "Juan Pérez", "Máquina": "Línea 4", "Puntaje": 60, "Ultimo_Logueo": hoy - timedelta(days=10)},
    {"Legajo": "1002", "Operario": "Ana Gómez", "Máquina": "Línea 2", "Puntaje": 55, "Ultimo_Logueo": hoy - timedelta(days=12)},
    {"Legajo": "1002", "Operario": "Ana Gómez", "Máquina": "Línea 4", "Puntaje": 90, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1002", "Operario": "Ana Gómez", "Máquina": "MIG", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=4)},
    {"Legajo": "1003", "Operario": "Carlos Ruiz", "Máquina": "Línea 3", "Puntaje": 20, "Ultimo_Logueo": hoy - timedelta(days=1)},
    {"Legajo": "1003", "Operario": "Carlos Ruiz", "Máquina": "PRP", "Puntaje": 40, "Ultimo_Logueo": hoy - timedelta(days=80)}, # Bloqueado
    {"Legajo": "1004", "Operario": "María López", "Máquina": "Celdas Robot", "Puntaje": 95, "Ultimo_Logueo": hoy - timedelta(days=3)},
    {"Legajo": "1004", "Operario": "María López", "Máquina": "MIG", "Puntaje": 75, "Ultimo_Logueo": hoy - timedelta(days=8)},
    {"Legajo": "1005", "Operario": "Diego Torres", "Máquina": "PRP", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=65)}, # Bloqueado
    {"Legajo": "1005", "Operario": "Diego Torres", "Máquina": "Celdas Robot", "Puntaje": 15, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1006", "Operario": "Gabriel Méndez", "Máquina": "Línea 2", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=4)},
    {"Legajo": "1007", "Operario": "Sofia Rodríguez", "Máquina": "MIG", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=1)},
    {"Legajo": "1008", "Operario": "Cristian Ortega", "Máquina": "Línea 4", "Puntaje": 70, "Ultimo_Logueo": hoy - timedelta(days=6)},
    {"Legajo": "1009", "Operario": "Valeria Russo", "Máquina": "PRP", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1010", "Operario": "Lucas Herrera", "Máquina": "Línea 2", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=90)} # Bloqueado
]

# Añadimos datos extra para simular una planta grande y testear el panel congelado
for i in range(11, 40):
    datos_fabrica.append({"Legajo": str(1000+i), "Operario": f"Operario Prueba {i}", "Máquina": "Línea 2", "Puntaje": 75, "Ultimo_Logueo": hoy - timedelta(days=10)})

df_base = pd.DataFrame(datos_fabrica)

# --- 3. LÓGICA DE NEGOCIO (Motor FUMISCOR) ---
def analizar_competencia(fila):
    dias_inactivo = (hoy - fila["Ultimo_Logueo"]).days
    puntaje = fila["Puntaje"]
    
    if puntaje <= 25: nivel = 1
    elif puntaje <= 50: nivel = 2
    elif puntaje <= 75: nivel = 3
    else: nivel = 4
    
    bloqueado = dias_inactivo > 60
    return nivel, bloqueado, dias_inactivo

df_base[['Nivel', 'Bloqueado', 'Dias_Inactivo']] = df_base.apply(lambda r: pd.Series(analizar_competencia(r)), axis=1)

# Jerarquía estricta de puestos de Famma
puestos_ordenados = ["Línea 2", "Línea 3", "Línea 4", "Celdas Robot", "MIG", "PRP"]

# --- 4. BARRA LATERAL Y EXPORTACIÓN MAESTRA ---
st.sidebar.title("⚙️ PANEL FUMISCOR")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegación", ["📊 Mapa Skill Global", "📝 Resumen Evaluaciones", "📅 Armador de Turnos"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Sincronización Master")

def exportar_matriz_actualizacion():
    """Genera la grilla exacta con los puntajes para pegar directo en tu Excel."""
    df_export = df_base.pivot(index=["Legajo", "Operario"], columns="Máquina", values="Puntaje")
    
    columnas_validas = [p for p in puestos_ordenados if p in df_export.columns]
    df_export = df_export[columnas_validas]
    df_export = df_export.fillna('')
    df_export = df_export.reset_index()
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Sincronizacion', index=False)
        ws = writer.sheets['Sincronizacion']
        ws.column_dimensions['A'].width = 15  # Legajo
        ws.column_dimensions['B'].width = 30  # Operario
        for idx in range(3, len(df_export.columns) + 1):
            letra_columna = chr(64 + idx) if idx <= 26 else chr(64 + idx//26) + chr(64 + idx%26)
            ws.column_dimensions[letra_columna].width = 18
            
    return buffer.getvalue()

st.sidebar.download_button(
    label="📄 Exportar Grilla de Actualización",
    data=exportar_matriz_actualizacion(),
    file_name='Actualizacion_Mapa_Skill.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    help="Descarga la matriz con los puntajes para copiar y pegar directamente en tu Excel maestro."
)

# --- PANTALLA 1: MAPA SKILL GLOBAL ---
if menu == "📊 Mapa Skill Global":
    st.title("📊 Mapa Skill General")
    st.markdown("Matriz escalable con **paneles congelados** y filtrado en tiempo real.")
    
    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1: busqueda_nombre = st.text_input("🔍 Buscar por Nombre o Legajo:")
    with col_f2: maquinas_filtradas = st.multiselect("⚙️ Filtrar por Puestos:", puestos_ordenados, default=puestos_ordenados)
    
    def renderizar_html_grid(nivel, bloqueado):
        if bloqueado: return '<div style="color:#ef4444; font-weight:bold; font-size:22px; text-align:center;">🔒</div>'
        c1, c2, c3, c4 = ["#000000" if nivel >= i else "#ffffff" for i in range(1, 5)]
        return f'<div style="display:inline-grid; grid-template-columns:18px 18px; gap:2px; background-color:#000000; border:2px solid #000000; padding:2px; margin:auto;"><div style="width:18px; height:18px; background-color:{c1};"></div><div style="width:18px; height:18px; background-color:{c2};"></div><div style="width:18px; height:18px; background-color:{c3};"></div><div style="width:18px; height:18px; background-color:{c4};"></div></div>'

    df_base["HTML_Grid"] = df_base.apply(lambda f: renderizar_html_grid(f["Nivel"], f["Bloqueado"]), axis=1)
    
    matriz_html = df_base.pivot(index="Operario", columns="Máquina", values="HTML_Grid").fillna('<div style="color:#cbd5e1;">-</div>')
    
    # Aplicación de filtros
    if busqueda_nombre:
        matriz_html = matriz_html[matriz_html.index.str.contains(busqueda_nombre, case=False, na=False)]
    columnas_validas = [p for p in maquinas_filtradas if p in matriz_html.columns]
    matriz_html = matriz_html[columnas_validas]
    
    # Inyección de la tabla con scroll y freeze panes
    html_tabla = matriz_html.to_html(escape=False).replace('<table border="1" class="dataframe">', '<table class="grilla-fumiscor">').replace('<th>Operario</th>', '<th>Colaboradores / Puestos</th>')
    st.markdown(f'<div class="table-container">{html_tabla}</div>', unsafe_allow_html=True)

# --- PANTALLA 2: RESUMEN EVALUACIONES ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Legajo Técnico del Colaborador")
    st.markdown("Historial analítico de certificaciones y estados de entrenamiento[cite: 70].")
    
    op_seleccionado = st.selectbox("Seleccione el Colaborador:", df_base["Operario"].unique())
    df_op = df_base[df_base["Operario"] == op_seleccionado]
    
    st.markdown(f"### **Colaborador:** {op_seleccionado} | **Legajo:** {df_op['Legajo'].iloc[0]}")
    
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Puestos Autónomos/Expertos (>= N3)", len(df_op[df_op["Nivel"] >= 3]))
    kpi2.metric("Puestos Bloqueados (>60 días inactivo)", len(df_op[df_op["Bloqueado"] == True]))
    
    st.markdown("#### Historial de Certificaciones")
    df_historial = df_op.copy()
    df_historial["Estado"] = df_historial.apply(lambda r: "🛑 BLOQUEADO" if r["Bloqueado"] else ("⭐ Experto" if r["Nivel"] == 4 else ("✅ Autónomo" if r["Nivel"] == 3 else ("⚠️ Básico" if r["Nivel"] == 2 else "🌱 Entrenamiento"))), axis=1)
    df_historial["Último logueo"] = df_historial["Dias_Inactivo"].apply(lambda d: f"Hace {d} días")
    st.table(df_historial[["Máquina", "Puntaje", "Estado", "Último logueo"]])

# --- PANTALLA 3: ARMADOR DE TURNOS ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Armador Seguro de Turnos")
    st.markdown("Filtrado predictivo de dotación idónea basado en polivalencia y reglas de login [cite: 97-98].")
    
    col_seleccion, col_resumen = st.columns([1.5, 1])
    
    with col_seleccion:
        st.markdown("### 1. Seleccionar Área y Puesto")
        turno_t = st.selectbox("Turno:", ["A (Mañana)", "B (Tarde)", "C (Noche)"])
        puesto_t = st.selectbox("Máquina a cubrir:", puestos_ordenados) 
        
        df_puesto = df_base[df_base["Máquina"] == puesto_t]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🟢 Aptos")
            aptos = df_puesto[(df_puesto["Nivel"] >= 3) & (~df_puesto["Bloqueado"])]
            if not aptos.empty:
                for _, row in aptos.iterrows():
                    # Botón para asignar a la memoria
                    if st.button(f"Asignar {row['Operario']}", key=f"btn_{row['Operario']}"):
                        nueva_asignacion = pd.DataFrame([{"Turno": turno_t, "Máquina": puesto_t, "Operario Asignado": row['Operario']}])
                        st.session_state.roster_turno = pd.concat([st.session_state.roster_turno, nueva_asignacion], ignore_index=True)
                        st.success("Asignado")
                    st.markdown(f'<div class="box-turno box-apto"><b>{row["Operario"]}</b><br>Nivel {row["Nivel"]}</div>', unsafe_allow_html=True)
            else: st.info("No hay personal calificado.")
                
        with col2:
            st.markdown("#### 🟡 Reinducción")
            reind = df_puesto[(df_puesto["Nivel"] >= 3) & (df_puesto["Bloqueado"])]
            for _, row in reind.iterrows():
                st.markdown(f'<div class="box-turno box-reind"><b>{row["Operario"]}</b><br>⚠️ Requiere checklist.</div>', unsafe_allow_html=True)
                
        with col3:
            st.markdown("#### 🔴 No Aptos")
            no_aptos = df_puesto[df_puesto["Nivel"] < 3]
            for _, row in no_aptos.iterrows():
                st.markdown(f'<div class="box-turno box-noapto"><b>{row["Operario"]}</b><br>Nivel {row["Nivel"]}</div>', unsafe_allow_html=True)

    with col_resumen:
        st.markdown("### 2. Resumen del Turno")
        st.info(f"Asignaciones: **Turno {turno_t}**")
        
        roster_actual = st.session_state.roster_turno[st.session_state.roster_turno["Turno"] == turno_t]
        if not roster_actual.empty:
            st.dataframe(roster_actual[["Máquina", "Operario Asignado"]], use_container_width=True, hide_index=True)
            if st.button("🗑️ Limpiar Turno"):
                st.session_state.roster_turno = st.session_state.roster_turno[st.session_state.roster_turno["Turno"] != turno_t]
                st.rerun()
        else:
            st.write("Aún no hay asignaciones.")
