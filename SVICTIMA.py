import streamlit as st
import json

# --- 1. CONFIGURACIÓN BÁSICA (Indispensable para que funcione solo) ---
st.set_page_config(page_title="SVI - Solo Bloque Víctima", layout="wide")

# Inicializamos el diccionario de datos si no existe
if "data_operativa" not in st.session_state:
    st.session_state.data_operativa = {
        "personal": "Sub Comisario CASTAÑEDA Juan", #
        "vic_nombre": "", "vic_dni": "", "relato_vic_crudo": ""
    }

# --- 2. MOTOR DE DETECCIÓN (Tu lógica aprobada) ---
def detectar_delito(texto):
    texto = texto.lower()
    if any(w in texto for w in ["cuchillo", "arma", "pistola", "punta", "amenazó", "matar", "muerte"]):
        return "AMENAZAS CALIFICADAS"
    elif any(w in texto for w in ["tirón", "empujó", "fuerza", "rompió", "vidrio", "puerta", "violencia"]):
        return "ROBO / ROBO CALIFICADO"
    elif any(w in texto for w in ["descuido", "sustrajo", "llevó", "faltaba", "sin darse cuenta"]):
        return "HURTO"
    elif any(w in texto for w in ["pegar", "pegó", "piña", "patada", "sangre", "médico", "golpe", "lesión"]):
        return "LESIONES"
    return "OTRO / A DETERMINAR"

# --- 3. EL BLOQUE 3 (Versión Prolija y Camuflada) ---
st.title("🚔 S.I.V. - Módulo de Víctima")
st.markdown(f"**Operador:** {st.session_state.data_operativa['personal']}")

# Relato Crudo
relato_crudo = st.text_area(
    "Relato espontáneo (Lo que la persona cuenta):",
    value=st.session_state.data_operativa.get("relato_vic_crudo", ""),
    height=150
)
st.session_state.data_operativa["relato_vic_crudo"] = relato_crudo

if relato_crudo:
    delito_sugerido = detectar_delito(relato_crudo)
    st.warning(f"⚖️ PROTOCOLO DETECTADO: {delito_sugerido}")

    # Protocolos Dinámicos
    col1, col2 = st.columns(2)
    if "LESIONES" in delito_sugerido:
        with col1:
            st.session_state.data_operativa["vic_insta_accion"] = st.checkbox("¿Insta la acción penal? (Art. 72 CP)", value=True)
            st.session_state.data_operativa["vic_asistencia"] = st.radio("¿Asistencia Médica?", ["SÍ", "NO"])
        with col2:
            st.session_state.data_operativa["vic_medico"] = st.text_input("Médico / Centro de Salud")

    elif "AMENAZAS" in delito_sugerido:
        with col1:
            st.session_state.data_operativa["vic_dichos"] = st.text_area("Dichos textuales del autor (Entre comillas)")
        with col2:
            st.session_state.data_operativa["vic_temor"] = st.radio("¿Siente temor por su integridad?", ["SÍ", "NO"])

    # Datos Personales
    st.divider()
    c3, c4 = st.columns(2)
    st.session_state.data_operativa["vic_nombre"] = c3.text_input("Nombre Completo", value=st.session_state.data_operativa["vic_nombre"])
    st.session_state.data_operativa["vic_dni"] = c4.text_input("DNI (Solo números)", value=st.session_state.data_operativa["vic_dni"])

    # GENERACIÓN NARRATIVA (Camuflaje de preguntas)
    st.subheader("📝 Declaración en Primera Persona")
    
    narrativa = f"Yo, {st.session_state.data_operativa['vic_nombre']}, DNI {st.session_state.data_operativa['vic_dni']}, comparezco y expongo: {relato_crudo}. "
    
    # Camuflaje automático según respuestas
    if st.session_state.data_operativa.get("vic_insta_accion"):
        narrativa += "Por las lesiones que presento, es mi deseo expreso instar la acción penal conforme a derecho. "
    
    if st.session_state.data_operativa.get("vic_temor") == "SÍ":
        narrativa += "Debido a los dichos que recibí, manifiesto que siento un temor real por mi integridad física. "

    st.text_area("Texto para el Acta:", value=narrativa, height=200)

    # Botón de Copiado
    if st.button("🚀 COPIAR PARA IA"):
        prompt_ia = f"Redactá en primera persona (YO), profesionalmente: {narrativa}"
        st.components.v1.html(f"<script>navigator.clipboard.writeText(`{prompt_ia}`);</script>", height=0)
        st.success("Copiado.")
