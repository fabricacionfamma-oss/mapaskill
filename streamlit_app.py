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
    
    /* Estilos para el Tablero del Turnero de Planta */
    .tablero-planta { width: 100%; border-collapse: collapse; margin-top: 15px; font-family: 'Segoe UI', sans-serif; }
    .tablero-planta th { background-color: #1e293b; color: white; padding: 12px; text-align: left; border: 1px solid #cbd5e1; }
    .tablero-planta td { padding: 10px; border: 1px solid #cbd5e1; vertical-align: middle; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block; }
    .badge-apto { background-color: #dcfce7; color: #166534; }
    .badge-reind { background-color: #fef3c7; color: #92400e; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA MAESTRA DEL TURNERO DE PLANTA ---
if 'roster_planta' not in st.session_state:
    st.session_state.roster_planta = {}

# --- 2. BASE DE DATOS UNIFICADA (Simulación de Forms + Wiidem) ---
hoy = datetime.now()
datos_fabrica = [
    # Famma Estampado
    {"Legajo": "1001", "Operario": "Juan Pérez", "Área": "Famma Estampado", "Máquina": "Línea 2", "Puntaje": 25, "Ultimo_Logueo": hoy - timedelta(days=5)},
    {"Legajo": "1001", "Operario": "Juan Pérez", "Área": "Famma Estampado", "Máquina": "Línea 3", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=72)}, 
    {"Legajo": "1001", "Operario": "Juan Pérez", "Área": "Famma Estampado", "Máquina": "Línea 4", "Puntaje": 60, "Ultimo_Logueo": hoy - timedelta(days=10)},
    {"Legajo": "1002", "Operario": "Ana Gómez", "Área": "Famma Estampado", "Máquina": "Línea 2", "Puntaje": 55, "Ultimo_Logueo": hoy - timedelta(days=12)},
    {"Legajo": "1002", "Operario": "Ana Gómez", "Área": "Famma Estampado", "Máquina": "Línea 4", "Puntaje": 90, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1003", "Operario": "Carlos Ruiz", "Área": "Famma Estampado", "Máquina": "Línea 3", "Puntaje": 20, "Ultimo_Logueo": hoy - timedelta(days=1)},
    {"Legajo": "1006", "Operario": "Gabriel Méndez", "Área": "Famma Estampado", "Máquina": "Línea 2", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=4)},
    {"Legajo": "1008", "Operario": "Cristian Ortega", "Área": "Famma Estampado", "Máquina": "Línea 4", "Puntaje": 70, "Ultimo_Logueo": hoy - timedelta(days=6)},
    {"Legajo": "1010", "Operario": "Lucas Herrera", "Área": "Famma Estampado", "Máquina": "Línea 2", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=90)}, 
    
    # Famma Soldadura
    {"Legajo": "1002", "Operario": "Ana Gómez", "Área": "Famma Soldadura", "Máquina": "MIG", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=4)},
    {"Legajo": "1003", "Operario": "Carlos Ruiz", "Área": "Famma Soldadura", "Máquina": "PRP", "Puntaje": 40, "Ultimo_Logueo": hoy - timedelta(days=80)}, 
    {"Legajo": "1004", "Operario": "María López", "Área": "Famma Soldadura", "Máquina": "Celdas Robot", "Puntaje": 95, "Ultimo_Logueo": hoy - timedelta(days=3)},
    {"Legajo": "1004", "Operario": "María López", "Área": "Famma Soldadura", "Máquina": "MIG", "Puntaje": 75, "Ultimo_Logueo": hoy - timedelta(days=8)},
    {"Legajo": "1005", "Operario": "Diego Torres", "Área": "Famma Soldadura", "Máquina": "PRP", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=65)}, 
    {"Legajo": "1005", "Operario": "Diego Torres", "Área": "Famma Soldadura", "Máquina": "Celdas Robot", "Puntaje": 15, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1007", "Operario": "Sofia Rodríguez", "Área": "Famma Soldadura", "Máquina": "Celdas Robot", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=1)},
    {"Legajo": "1009", "Operario": "Valeria Russo", "Área": "Famma Soldadura", "Máquina": "PRP", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=2)}
]

# Rellenado para simulación de panel masivo congelado (+100 usuarios)
for i in range(11, 35):
    datos_fabrica.append({"Legajo": str(1000+i), "Operario": f"Operario Prueba {i}", "Área": "Famma Estampado", "Máquina": "Línea 2", "Puntaje": 75, "Ultimo_Logueo": hoy - timedelta(days=15)})

df_base = pd.DataFrame(datos_fabrica)

# --- 3. LÓGICA DE NEGOCIO (Motor FUMISCOR) ---
def analizar_competencia(fila):
    dias_inactivo = (hoy - fila["Ultimo_Logueo"]).days
    puntaje = fila["Puntaje"]
    if puntaje <= 25: nivel = 1
    elif puntaje <= 50: nivel = 2
    elif puntaje <= 75: nivel = 3
    else: nivel = 4
    return nivel, dias_inactivo > 60, dias_inactivo

df_base[['Nivel', 'Bloqueado', 'Dias_Inactivo']] = df_base.apply(lambda r: pd.Series(analizar_competencia(r)), axis=1)

# Jerarquías oficiales por área
puestos_estampado = ["Línea 2", "Línea 3", "Línea 4"]
puestos_soldadura = ["Celdas Robot", "MIG", "PRP"]
puestos_ordenados = puestos_estampado + puestos_soldadura

# --- 4. BARRA LATERAL Y EXPORTACIÓN MAESTRA ---
st.sidebar.title("⚙️ PANEL FUMISCOR")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegación", ["📊 Mapa Skill Global", "📝 Resumen Evaluaciones", "📅 Armador de Turnos"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Sincronización Master")

def exportar_matriz_actualizacion():
    df_export = df_base.pivot(index=["Legajo", "Operario"], columns="Máquina", values="Puntaje")
    columnas_validas = [p for p in puestos_ordenados if p in df_export.columns]
    df_export = df_export[columnas_validas].fillna('').reset_index()
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Sincronizacion', index=False)
        ws = writer.sheets['Sincronizacion']
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 30
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
    st.markdown("Matriz con **paneles congelados** y filtrado interactivo por área de producción.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1: busqueda_nombre = st.text_input("🔍 Buscar por Nombre o Legajo:")
    with col_f2: area_filtro = st.multiselect("🏭 Filtrar por Área:", ["Famma Estampado", "Famma Soldadura"], default=["Famma Estampado", "Famma Soldadura"])
    
    puestos_filtrados = []
    if "Famma Estampado" in area_filtro: puestos_filtrados.extend(puestos_estampado)
    if "Famma Soldadura" in area_filtro: puestos_filtrados.extend(puestos_soldadura)

    def renderizar_html_grid(nivel, bloqueado):
        if bloqueado: return '<div style="color:#ef4444; font-weight:bold; font-size:22px; text-align:center;">🔒</div>'
        c1, c2, c3, c4 = ["#000000" if nivel >= i else "#ffffff" for i in range(1, 5)]
        return f'<div style="display:inline-grid; grid-template-columns:18px 18px; gap:2px; background-color:#000000; border:2px solid #000000; padding:2px; margin:auto;"><div style="width:18px; height:18px; background-color:{c1};"></div><div style="width:18px; height:18px; background-color:{c2};"></div><div style="width:18px; height:18px; background-color:{c3};"></div><div style="width:18px; height:18px; background-color:{c4};"></div></div>'

    df_base["HTML_Grid"] = df_base.apply(lambda f: renderizar_html_grid(f["Nivel"], f["Bloqueado"]), axis=1)
    matriz_html = df_base.pivot(index="Operario", columns="Máquina", values="HTML_Grid").fillna('<div style="color:#cbd5e1;">-</div>')
    
    if busqueda_nombre:
        matriz_html = matriz_html[matriz_html.index.str.contains(busqueda_nombre, case=False, na=False)]
    columnas_validas = [p for p in puestos_filtrados if p in matriz_html.columns]
    matriz_html = matriz_html[columnas_validas]
    
    html_tabla = matriz_html.to_html(escape=False).replace('<table border="1" class="dataframe">', '<table class="grilla-fumiscor">').replace('<th>Operario</th>', '<th>Colaboradores / Puestos</th>')
    st.markdown(f'<div class="table-container">{html_tabla}</div>', unsafe_allow_html=True)

# --- PANTALLA 2: RESUMEN EVALUACIONES (LEGAJO DIGITAL WIIDEM) ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Legajo Digital de Operarios")
    st.markdown("Consolidado analítico de Evaluaciones Técnicas (Forms) e Historial de Servidores (Wiidem).")
    
    op_seleccionado = st.selectbox("Seleccione el Operario a auditar:", df_base["Operario"].unique())
    df_op = df_base[df_base["Operario"] == op_seleccionado]
    
    st.markdown(f"### **Colaborador:** {op_seleccionado} | **Legajo:** {df_op['Legajo'].iloc[0]}")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Puestos Calificados (Nivel >= 3)", len(df_op[df_op["Nivel"] >= 3]))
    kpi2.metric("Bloqueos por Inactividad (>60 días)", len(df_op[df_op["Bloqueado"] == True]))
    kpi3.metric("Conexión del Legajo", "Servidor FUMIS (OK)", delta="Base wii_bi")
    
    st.markdown("---")
    st.markdown("#### Resumen Cruzado: Habilidad vs Último Login")
    
    df_historial = df_op.copy()
    df_historial["Estado Certificación"] = df_historial.apply(lambda r: "⭐ Experto" if r["Nivel"] == 4 else ("✅ Autónomo" if r["Nivel"] == 3 else ("⚠️ Básico" if r["Nivel"] == 2 else "🌱 Entrenamiento")), axis=1)
    df_historial["Último Login Realizado"] = df_historial["Ultimo_Logueo"].dt.strftime('%d/%m/%Y') + df_historial["Dias_Inactivo"].apply(lambda d: f" (Hace {d} días)")
    df_historial["Habilitación Planta"] = df_historial["Bloqueado"].apply(lambda b: "❌ BLOQUEADO - Requiere Reinducción" if b else "🟢 HABILITADO")
    
    st.table(df_historial[["Máquina", "Puntaje", "Estado Certificación", "Último Login Realizado", "Habilitación Planta"]])

# --- PANTALLA 3: ARMADOR DE TURNOS (TABLERO GENERAL DE PLANTA) ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Tablero Maestro de Asignación por Área")
    st.markdown("Asignación interactiva por puesto en celdas integradas de la planta. **Puede asignar múltiples operarios por celda.**")
    
    col_area, col_turno = st.columns(2)
    with col_area:
        area_t = st.selectbox("Seleccionar Área de Planta:", ["Famma Estampado", "Famma Soldadura"])
    with col_turno:
        turno_t = st.selectbox("Seleccionar Turno de Trabajo:", ["A (Mañana)", "B (Tarde)", "C (Noche)"])
    
    puestos_del_area = puestos_estampado if area_t == "Famma Estampado" else puestos_soldadura
    
    st.markdown(f"### 📋 Roster de Planta: {area_t} - Turno {turno_t}")
    st.markdown("Seleccione todos los operarios necesarios para cada línea o celda (ej. 4 a 6 por Línea).")
    
    key_turno_area = f"{area_t}_{turno_t}"
    
    # Inicializamos la memoria guardando LISTAS vacías en lugar de "Sin Asignar"
    if key_turno_area not in st.session_state.roster_planta:
        st.session_state.roster_planta[key_turno_area] = {p: [] for p in puestos_del_area}
        
    for puesto in puestos_del_area:
        st.markdown(f"#### ⚙️ Puesto: {puesto}")
        
        df_candidatos = df_base[df_base["Máquina"] == puesto]
        lista_aptos = df_candidatos[(df_candidatos["Nivel"] >= 3) & (~df_candidatos["Bloqueado"])]["Operario"].tolist()
        lista_reind = df_candidatos[(df_candidatos["Nivel"] >= 3) & (df_candidatos["Bloqueado"])]["Operario"].tolist()
        
        opciones_select = []
        opciones_select.extend([f"🟢 {op}" for op in lista_aptos])
        opciones_select.extend([f"🟡 {op} (Exige Reinducción)" for op in lista_reind])
        
        # Recuperamos la lista de operarios guardados y los mapeamos al formato visual del multiselect
        valores_guardados = st.session_state.roster_planta[key_turno_area].get(puesto, [])
        # Prevención de errores si había strings guardados de la versión anterior del código
        if isinstance(valores_guardados, str): valores_guardados = [] 
        
        opciones_por_defecto = []
        for opc in opciones_select:
            nombre_limpio = opc.replace("🟢 ", "").replace("🟡 ", "").replace(" (Exige Reinducción)", "")
            if nombre_limpio in valores_guardados:
                opciones_por_defecto.append(opc)
                
        # Cambiamos selectbox por MULTISELECT
        selecciones = st.multiselect(
            f"Asignar equipo para {puesto}:",
            options=opciones_select,
            default=opciones_por_defecto,
            key=f"select_{key_turno_area}_{puesto}"
        )
        
        # Limpiamos los emojis/textos extra y guardamos la lista pura en memoria
        nombres_limpios = [s.replace("🟢 ", "").replace("🟡 ", "").replace(" (Exige Reinducción)", "") for s in selecciones]
        st.session_state.roster_planta[key_turno_area][puesto] = nombres_limpios
        st.markdown("---")
        
    st.markdown(f"### 👁️ Vistazo General de la Planta ({area_t})")
    
    datos_resumen = []
    for p, lista_ops in st.session_state.roster_planta[key_turno_area].items():
        if not lista_ops:  # Si la lista está vacía
            badge = '<span style="color:#94a3b8; font-style:italic;">Celda Vacía</span>'
            datos_resumen.append({"Puesto / Celda": p, "Operario Asignado": "-", "Estado Operativo": badge})
        else:
            # Si hay operarios, creamos una fila por cada uno
            for op in lista_ops:
                match = df_base[(df_base["Operario"] == op) & (df_base["Máquina"] == p)]
                if not match.empty and match["Bloqueado"].iloc[0]:
                    badge = '<span class="status-badge badge-reind">⚠️ REINDUCCIÓN PENDIENTE</span>'
                else:
                    badge = '<span class="status-badge badge-apto">✅ OPERANDO</span>'
                    
                datos_resumen.append({"Puesto / Celda": p, "Operario Asignado": op, "Estado Operativo": badge})
        
    df_resumen = pd.DataFrame(datos_resumen)
    
    html_tablero = df_resumen.to_html(escape=False, index=False)
    html_tablero = html_tablero.replace('<table border="1" class="dataframe">', '<table class="tablero-planta">')
    st.markdown(html_tablero, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Exportación a Excel conservando la nueva estructura de múltiples filas
    df_export_turno = df_resumen.copy()
    df_export_turno["Estado Operativo"] = df_export_turno["Estado Operativo"].str.replace('<[^<]+?>', '', regex=True) 
    df_export_turno.insert(0, "Turno", turno_t)
    df_export_turno.insert(0, "Área", area_t)
    
    buffer_turno = io.BytesIO()
    with pd.ExcelWriter(buffer_turno, engine='openpyxl') as writer:
        df_export_turno.to_excel(writer, sheet_name='Roster Planta', index=False)
        
    st.download_button(
        label=f"📥 Exportar Vistazo General de {area_t} a Excel",
        data=buffer_turno.getvalue(),
        file_name=f"Roster_{area_t.replace(' ', '_')}_{turno_t}.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
