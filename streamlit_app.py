import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y CSS INDUSTRIAL ---
st.set_page_config(page_title="Gestor FUMISCOR", layout="wide", page_icon="🏭")

st.markdown("""
<style>
    /* Estilos de la Grilla (Mapa Skill) */
    .grilla-fumiscor { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; font-size: 15px; margin-top: 15px; }
    .grilla-fumiscor th { background-color: #0f172a; color: #ffffff; font-weight: 700; padding: 14px; text-align: center; border: 2px solid #334155; }
    .grilla-fumiscor td { padding: 12px; text-align: center; vertical-align: middle; border: 2px solid #cbd5e1; }
    .grilla-fumiscor td:first-child { font-weight: bold; color: #0f172a; background-color: #f1f5f9; text-align: left; padding-left: 15px; border-right: 3px solid #64748b; width: 250px; }
    .grilla-fumiscor tr:hover { background-color: #f8fafc; }
    
    /* Contenedores del Turnero */
    .box-turno { padding: 15px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #cbd5e1; }
    .box-apto { background-color: #f0fdf4; border-left: 5px solid #16a34a; }
    .box-reind { background-color: #fffbeb; border-left: 5px solid #d97706; }
    .box-noapto { background-color: #fef2f2; border-left: 5px solid #dc2626; }
</style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DATOS UNIFICADA (Simulación de Forms + Wiidem) ---
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
    {"Legajo": "1007", "Operario": "Sofia Rodríguez", "Máquina": "Celdas Robot", "Puntaje": 85, "Ultimo_Logueo": hoy - timedelta(days=1)},
    {"Legajo": "1008", "Operario": "Cristian Ortega", "Máquina": "Línea 4", "Puntaje": 70, "Ultimo_Logueo": hoy - timedelta(days=6)},
    {"Legajo": "1009", "Operario": "Valeria Russo", "Máquina": "PRP", "Puntaje": 80, "Ultimo_Logueo": hoy - timedelta(days=2)},
    {"Legajo": "1010", "Operario": "Lucas Herrera", "Máquina": "Línea 2", "Puntaje": 100, "Ultimo_Logueo": hoy - timedelta(days=90)} # Bloqueado
]
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
puestos_ordenados = ["Línea 2", "Línea 3", "Línea 4", "Celdas Robot", "MIG", "PRP"]

# --- 4. BARRA LATERAL Y EXPORTACIÓN MAESTRA ---
st.sidebar.title("⚙️ PANEL FUMISCOR")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegación", ["📊 Mapa Skill Global", "📝 Resumen Evaluaciones", "📅 Armador de Turnos"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Sincronización Excel")

def generar_excel_master():
    """Genera el Excel exacto para copiar y pegar en la matriz 'Plan de Entrenamiento'"""
    df_export = df_base[["Máquina", "Legajo", "Operario", "Puntaje", "Ultimo_Logueo"]].copy()
    df_export.columns = ["PUESTO DE TRABAJO", "LEGAJO", "APELLIDO Y NOMBRE", "EVALUACIÓN TEÓRICO PRÁCTICA", "FECHA EVALUACIÓN"]
    df_export["FECHA EVALUACIÓN"] = df_export["FECHA EVALUACIÓN"].dt.strftime('%d/%m/%Y')
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='PLAN ENTRENAMIENTO', index=False)
        ws = writer.sheets['PLAN ENTRENAMIENTO']
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 35
        ws.column_dimensions['E'].width = 20
    return buffer.getvalue()

st.sidebar.download_button(
    label="📄 Descargar 'Plan de Entrenamiento'",
    data=generar_excel_master(),
    file_name='Sincronizador_Plan_Entrenamiento.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    help="Descarga el formato exacto de 5 columnas para pegar en tu Excel original."
)

# --- PANTALLA 1: MAPA SKILL GLOBAL ---
if menu == "📊 Mapa Skill Global":
    st.title("📊 Mapa Skill General")
    st.markdown("Visualización de cuadrantes ampliados (18x18px) para seguimiento en Planta.")
    
    def renderizar_html_grid(nivel, bloqueado):
        if bloqueado: return '<div style="color:#ef4444; font-weight:bold; font-size:22px; text-align:center;">🔒</div>'
        c1, c2, c3, c4 = ["#000000" if nivel >= i else "#ffffff" for i in range(1, 5)]
        return f'<div style="display:inline-grid; grid-template-columns:18px 18px; gap:2px; background-color:#000000; border:2px solid #000000; padding:2px; margin:auto;"><div style="width:18px; height:18px; background-color:{c1};"></div><div style="width:18px; height:18px; background-color:{c2};"></div><div style="width:18px; height:18px; background-color:{c3};"></div><div style="width:18px; height:18px; background-color:{c4};"></div></div>'

    df_base["HTML_Grid"] = df_base.apply(lambda f: renderizar_html_grid(f["Nivel"], f["Bloqueado"]), axis=1)
    
    matriz_html = df_base.pivot(index="Operario", columns="Máquina", values="HTML_Grid").fillna('<div style="color:#cbd5e1;">-</div>')
    matriz_html = matriz_html[[p for p in puestos_ordenados if p in matriz_html.columns]]
    
    html_final = matriz_html.to_html(escape=False).replace('<table border="1" class="dataframe">', '<table class="grilla-fumiscor">').replace('<th>Operario</th>', '<th>Colaboradores / Puestos</th>')
    st.markdown(html_final, unsafe_allow_html=True)

# --- PANTALLA 2: RESUMEN EVALUACIONES ---
elif menu == "📝 Resumen Evaluaciones":
    st.title("📝 Legajo Técnico del Colaborador")
    op_seleccionado = st.selectbox("Seleccione el Colaborador:", df_base["Operario"].unique())
    df_op = df_base[df_base["Operario"] == op_seleccionado]
    
    st.markdown(f"### **Colaborador:** {op_seleccionado} | **Legajo:** {df_op['Legajo'].iloc[0]}")
    
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Puestos Autónomos/Expertos (>= N3)", len(df_op[df_op["Nivel"] >= 3]))
    kpi2.metric("Puestos Bloqueados (>60 días inactivo)", len(df_op[df_op["Bloqueado"] == True]))
    
    st.markdown("#### Historial de Certificaciones (Forms + Wiidem)")
    df_historial = df_op.copy()
    df_historial["Estado"] = df_historial.apply(lambda r: "🛑 BLOQUEADO" if r["Bloqueado"] else ("⭐ Experto" if r["Nivel"] == 4 else ("✅ Autónomo" if r["Nivel"] == 3 else ("⚠️ Básico" if r["Nivel"] == 2 else "🌱 Entrenamiento"))), axis=1)
    df_historial["Último logueo"] = df_historial["Dias_Inactivo"].apply(lambda d: f"Hace {d} días")
    st.table(df_historial[["Máquina", "Puntaje", "Estado", "Último logueo"]])

# --- PANTALLA 3: ARMADOR DE TURNOS ---
elif menu == "📅 Armador de Turnos":
    st.title("📅 Armador Seguro de Turnos")
    
    col_p, col_t = st.columns(2)
    with col_p: puesto_t = st.selectbox("Seleccionar Puesto:", puestos_ordenados)
    with col_t: turno_t = st.selectbox("Seleccionar Turno:", ["A (Mañana)", "B (Tarde)", "C (Noche)"])
        
    st.markdown(f"### Dotación para **{puesto_t}** en **Turno {turno_t}**")
    df_puesto = df_base[df_base["Máquina"] == puesto_t]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🟢 Aptos Inmediatos")
        aptos = df_puesto[(df_puesto["Nivel"] >= 3) & (~df_puesto["Bloqueado"])]
        if not aptos.empty:
            for _, row in aptos.iterrows():
                st.checkbox(f"{row['Operario']} (N{row['Nivel']})", key=f"apto_{row['Operario']}")
                st.markdown(f'<div class="box-turno box-apto"><b>{row["Operario"]}</b><br>Listo para operar.</div>', unsafe_allow_html=True)
        else: st.info("No hay personal activo.")
            
    with col2:
        st.markdown("#### 🟡 Reinducción Requerida")
        reind = df_puesto[(df_puesto["Nivel"] >= 3) & (df_puesto["Bloqueado"])]
        for _, row in reind.iterrows():
            st.markdown(f'<div class="box-turno box-reind"><b>{row["Operario"]}</b><br>⚠️ Exige checklist.</div>', unsafe_allow_html=True)
            
    with col3:
        st.markdown("#### 🔴 No Aptos")
        no_aptos = df_puesto[df_puesto["Nivel"] < 3]
        for _, row in no_aptos.iterrows():
            st.markdown(f'<div class="box-turno box-noapto"><b>{row["Operario"]}</b><br>En entrenamiento.</div>', unsafe_allow_html=True)
