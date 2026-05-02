import streamlit as st
import json
from datetime import date
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="S.I.V. - Bloque 3: Víctima", layout="wide", initial_sidebar_state="expanded")

# --- 2. CLASE GENERADORA DE PDF (ACTUALIZADA CON NUEVO TÍTULO) ---
class ActaPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        # Título actualizado según tu requerimiento
        self.cell(0, 10, 'ACTA DE ENTREVISTA', 0, 1, 'C') 
        self.ln(5)

    def crear_cuadros(self, d, relato):
        self.set_font('Arial', '', 9)
        self.rect(10, 25, 190, 20)
        self.text(12, 31, f"LUGAR: {d['lugar']}")
        self.text(140, 31, f"FECHA: {d['fecha']}")
        self.text(12, 40, f"ENTREVISTADOR: {d['oficial']}")
        self.text(140, 40, f"HORA: {d['hora']}")
        self.ln(22)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'SE PROCEDE A ENTREVISTAR A:', 1, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(30, 8, ' NOMBRE:', 1); self.cell(160, 8, d['nombre'], 1, 1)
        self.cell(30, 8, ' DNI:', 1); self.cell(65, 8, d['dni'], 1)
        self.cell(30, 8, ' EDAD / SEXO:', 1); self.cell(65, 8, f"{d['edad']} AÑOS / {d['sexo']}", 1, 1)
        self.cell(30, 8, ' DOMICILIO:', 1); self.cell(160, 8, d['domicilio'], 1, 1)
        self.cell(30, 8, ' NACIONALIDAD:', 1); self.cell(65, 8, d['nacionalidad'], 1)
        self.cell(30, 8, ' EST. CIVIL:', 1); self.cell(65, 8, d['est_civil'], 1, 1)
        self.cell(30, 8, ' OCUPACIÓN:', 1); self.cell(160, 8, d['ocupacion'], 1, 1)
        self.cell(30, 8, ' CONTACTO:', 1); self.cell(160, 8, f"CEL: {d['tel']} - EMAIL: {d['email']}", 1, 1)
        self.ln(5)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'RELATO DE ENTREVISTA', 1, 1, 'C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 7, relato, 1)
        self.ln(20)
        self.cell(95, 10, '__________________________', 0, 0, 'C')
        self.cell(95, 10, '__________________________', 0, 1, 'C')
        self.cell(95, 5, 'FIRMA ENTREVISTADO', 0, 0, 'C')
        self.cell(95, 5, 'FIRMA INTERVINIENTE', 0, 1, 'C')

# --- 3. FUNCIONES LÓGICAS ---
def calcular_edad(fecha_nac):
    today = date.today()
    return today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))

def detectar_protocolos(texto):
    t = texto.lower()
    p = []
    if any(w in t for w in ["arma", "pistola", "revólver", "cuchillo", "amenazó", "muerte", "matar"]): p.append("AMENAZAS CALIFICADAS")
    if any(w in t for w in ["sustrajo", "llevó", "celular", "robó", "forcejeó", "culatazo", "quitó", "mochila"]): p.append("ROBO CALIFICADO")
    if any(w in t for w in ["sangre", "golpe", "lesión", "lastimó", "herida", "pegó", "dolor", "médico"]): p.append("LESIONES")
    return p

# --- 4. INTERFAZ ---
# Título en interfaz actualizado
st.title("🚔 S.I.V. - Bloque 3: ACTA DE ENTREVISTA")
# Autoría actualizada según tu pedido
st.caption("Autor: Sub Comisario CASTAÑEDA Juan") 

with st.sidebar:
    st.header("Oficial Interviniente")
    oficial = st.text_input("Rango y Nombre", value="SUB COMISARIO CASTAÑEDA JUAN")
    st.divider()
    lugar = st.text_input("Lugar del Hecho", placeholder="EJ: CALLE SALTA 1200, ROSARIO").upper()
    hora = st.text_input("Hora del Hecho", placeholder="HH:MM")

# SECCIÓN 1: Identidad
with st.expander("🆔 1. DATOS FILIATORIOS", expanded=True):
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Apellido y Nombres").upper()
    dni = c2.text_input("DNI")
    sexo = c3.selectbox("Sexo", ["MASCULINO", "FEMENINO", "OTRO"])
    nacionalidad = c1.text_input("Nacionalidad", value="ARGENTINA").upper()
    est_civil = c2.selectbox("Estado Civil", ["SOLTERO/A", "CASADO/A", "DIVORCIADO/A", "VIUDO/A", "CONVIVIENTE"])
    fecha_nac = c3.date_input("Fecha de Nacimiento", min_value=date(1940, 1, 1), max_value=date.today())
    ocupacion = c1.text_input("Ocupación").upper()
    telefono = c2.text_input("Teléfono Celular")
    email = c3.text_input("Correo Electrónico").lower()
    domicilio = st.text_input("Domicilio Real").upper()
    edad_calc = calcular_edad(fecha_nac)

# SECCIÓN 2: Relato y Lógica de Instancia
st.subheader("✍️ 2. Relato del Hecho")
relato_crudo = st.text_area("Ingrese el relato espontáneo:", height=150)

if relato_crudo:
    protocolos = detectar_protocolos(relato_crudo)
    hay_lesiones = "LESIONES" in protocolos
    
    if protocolos:
        st.warning(f"⚠️ **AVISO AL SUMARIANTE:** Se detectaron elementos de: {', '.join(protocolos)}")
        
    col_p, col_q = st.columns(2)
    with col_p:
        insta = st.checkbox("¿Insta Acción Penal? (Art. 72 CP)", value=True if hay_lesiones else False)
    with col_q:
        temor = st.checkbox("¿Manifiesta Temor por su integridad?")

    filiacion_tecnica = (f"{nombre}, {nacionalidad}, {est_civil}, DE {edad_calc} AÑOS DE EDAD, "
                         f"NACIDA EN FECHA {fecha_nac.strftime('%d/%m/%Y')}, DNI {dni}, "
                         f"CON DOMICILIO EN {domicilio}, OCUPACIÓN {ocupacion}, "
                         f"TELÉFONO CELULAR {telefono}, CORREO ELECTRÓNICO {email}")

    st.divider()
    col_in, col_out = st.columns(2)
    
    with col_in:
        st.info("📂 **PASO 1: PROCESAR CON IA**")
        prompt_ia = (
            "Actuá como oficial escribiente. Redactá esta declaración en primera persona del singular. "
            "Usá un lenguaje llano y cotidiano, como el de un ciudadano común, sin tecnicismos legales. "
            f"Empezá con: {filiacion_tecnica}. "
            f"Integrá este relato: {relato_crudo}. "
        )
        
        if insta:
            prompt_ia += "Al final, agregá: 'Y con respecto a las lesiones que sufrí provocadas por esta persona, es mi deseo instar la acción penal'."
        if temor:
            prompt_ia += " Dejá constancia de que la víctima siente un miedo real por su vida."

        st.text_area("Copie este prompt:", value=prompt_ia, height=250)

    with col_out:
        st.success("📂 **PASO 2: REVISIÓN DEL SUMARIANTE**")
        acta_final = st.text_area("Texto final (Totalmente Editable):", height=250)
        
        if acta_final:
            datos_json = {
                "bloque": "3",
                "filiacion": filiacion_tecnica,
                "relato_final": acta_final,
                "insta_accion": insta,
                "dni": dni,
                "oficial": oficial
            }
            
            st.download_button(
                label="📥 EXPORTAR PAQUETE JSON PARA WHATSAPP",
                data=json.dumps(datos_json, indent=4, ensure_ascii=False),
                file_name=f"B3_VIC_{dni}.json",
                mime="application/json"
            )

            if st.button("🖨️ GENERAR PDF"):
                d_pdf = {
                    "lugar": lugar, "fecha": date.today().strftime("%d/%m/%Y"),
                    "oficial": oficial, "hora": hora, "nombre": nombre, "dni": dni,
                    "edad": edad_calc, "sexo": sexo, "domicilio": domicilio,
                    "nacionalidad": nacionalidad, "est_civil": est_civil,
                    "ocupacion": ocupacion, "tel": telefono, "email": email
                }
                pdf = ActaPDF(); pdf.add_page(); pdf.crear_cuadros(d_pdf, acta_final)
                pdf.output(f"ACTA_ENTREVISTA_{dni}.pdf") # Nombre de archivo actualizado
                st.success("PDF generado con éxito.")
