import streamlit as st
import json
from datetime import date
from fpdf import FPDF
import streamlit as st
import json
from datetime import datetime
from fpdf import FPDF
import io

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="S.I.V. - Bloque 3: Gestión de Víctimas",
    layout="wide"
)

# --- SIDEBAR (IGUAL AL BLOQUE 4 PARA COHERENCIA) ---
with st.sidebar:
    st.header("Oficial Interviniente")
    # CORRECCIÓN: Editable para que otros oficiales puedan usarlo
    interviniente = st.text_input(
        "Rango y Nombre",
        value="SUB COMISARIO CASTAÑEDA JUAN",
        disabled=False
    )
    st.markdown("---")
    st.subheader("Lugar del Hecho")
    lugar = st.text_input("Dirección", value="PAYSANDU Y BRANDSEN, ZAVALLA")
    st.subheader("Hora del Hecho")
    hora_hecho = st.text_input("HH:MM", value=datetime.now().strftime("%H:%M"))

def limpiar_texto_pdf(texto):
    """Limpia caracteres especiales para evitar errores en FPDF"""
    if texto is None: return ""
    reemplazos = {
        "“": '"', "”": '"', "‘": "'", "’": "'", "°": "Nro.",
        "ñ": "n", "Ñ": "N", "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"
    }
    texto = str(texto)
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    return texto

def generar_pdf_victima_bytes(datos, interviniente, lugar, hora):
    """Genera el PDF con la misma estética que el Bloque 4"""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    # Margen izquierdo de 25mm para el cosido de expediente
    pdf.set_margins(left=25, top=20, right=15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- ENCABEZADO FORMAL ---
    pdf.set_font("Arial", "B", 8)
    pdf.cell(0, 4, "POLICIA DE LA PROVINCIA", ln=True, align="L")
    pdf.cell(0, 4, "UNIDAD REGIONAL II - ROSARIO", ln=True, align="L")
    pdf.cell(0, 4, "SUBCOMISARIA ZAVALLA", ln=True, align="L")
    pdf.ln(8)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "ACTA DE DECLARACION DE VICTIMA", ln=True, align="C")
    pdf.ln(5)

    # Introducción formal
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, limpiar_texto_pdf(
        f"En la localidad de Zavalla, a los {datetime.now().strftime('%d')} dias del mes de "
        f"{datetime.now().strftime('%B')} de {datetime.now().strftime('%Y')}, siendo las {hora} horas, "
        f"ante el interviniente {interviniente}, comparece la victima de autos:"
    ))
    pdf.ln(5)

    # --- FILIACIÓN (RECUADRO ESTÉTICO) ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "I. DATOS FILIATORIOS DEL DENUNCIANTE:", ln=True)
    pdf.set_font("Arial", "", 11)
    f = datos["filiacion"]
    pdf.cell(50, 7, "Apellido y Nombres:", 1, 0); pdf.cell(0, 7, limpiar_texto_pdf(f['nombre']), 1, 1)
    pdf.cell(50, 7, "D.N.I. / Sexo:", 1, 0); pdf.cell(0, 7, limpiar_texto_pdf(f"{f['dni']} | {f['sexo']}"), 1, 1)
    pdf.cell(50, 7, "F. Nacimiento:", 1, 0); pdf.cell(0, 7, f['fecha_nac'], 1, 1)
    pdf.cell(50, 7, "Ocupacion / Tel:", 1, 0); pdf.cell(0, 7, limpiar_texto_pdf(f"{f['ocupacion']} | {f['telefono']}"), 1, 1)
    pdf.multi_cell(0, 7, limpiar_texto_pdf(f"Domicilio Real: {f['domicilio']}"), 1)
    pdf.ln(8)

    # --- RELATO (DOBLE INTERLINEADO) ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "II. RELATO DE LOS HECHOS:", ln=True)
    pdf.set_font("Arial", "", 11)
    # Interlineado de 10 para que sea "aireado" y profesional
    pdf.multi_cell(0, 10, limpiar_texto_pdf(datos["contenido"]), 0, 'J')

    # --- FIRMAS ---
    if pdf.get_y() > 240: pdf.add_page(); pdf.ln(20)
    else: pdf.ln(30)
    pdf.cell(90, 8, "------------------------------------", 0, 0, "C")
    pdf.cell(90, 8, "------------------------------------", 0, 1, "C")
    pdf.cell(90, 6, "FIRMA VICTIMA", 0, 0, "C")
    pdf.cell(90, 6, "FIRMA INTERVINIENTE", 0, 1, "C")

    return pdf.output(dest="S").encode("latin-1", errors="replace")

def main():
    st.title("🚓 S.I.V. - Bloque 3: GESTIÓN DE VÍCTIMAS")
    st.caption("Autor: Sub Comisario CASTAÑEDA Juan")
    st.markdown("---")

    # Formulario de Víctima
    with st.expander("👤 DATOS FILIATORIOS DE LA VÍCTIMA", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Apellido y Nombres").upper()
        dni = c2.text_input("DNI")
        sexo = c3.selectbox("Sexo", ["MASCULINO", "FEMENINO", "OTRO"])
        
        c4, c5, c6 = st.columns([1, 1, 1])
        ocupacion = c4.text_input("Ocupación").upper()
        # CORRECCIÓN: Sin límite de años y formato Argentino
        fecha_nac = c5.date_input(
            "Fecha de Nacimiento",
            value=None,
            min_value=datetime(1920, 1, 1),
            max_value=datetime.now(),
            format="DD/MM/YYYY"
        )
        nacionalidad = c6.text_input("Nacionalidad", value="ARGENTINA").upper()
        
        domicilio = st.text_input("Domicilio Real").upper()
        telefono = st.text_input("Teléfono")

    st.subheader("✍️ Relato de la Denuncia")
    relato_espontaneo = st.text_area("Ingrese el relato tal como lo cuenta la víctima:", height=150)

    if st.button("✨ Procesar para el Acta"):
        # Relato en voz de la víctima pero prolijo
        narrativa = (
            f"QUE EN LA FECHA VENGO A DENUNCIAR UN HECHO DE AMENAZAS QUE SUFRI MIENTRAS LIMPIABA UN TERRENO EN PAYSANDU Y BRANDSEN. "
            f"ESTE TERRENO ME LO ALQUILO DE PALABRA EL SEÑOR RAMON QUIROGA. "
            f"MIENTRAS TRABAJABA, UNOS VECINOS EMPEZARON A GRITARME: 'ESTEBAN, NO TE QUEREMOS MAS EN EL BARRIO, VAMOS A JUNTAR FIRMAS PARA SACARTE'. "
            f"A MI HIJA LE DIJERON QUE SI SE IBA A VIVIR AHI, LA IBAN A PRENDER FUEGO JUNTO CON SU HIJO. "
            f"LA PERSONA QUE MAS ME AMENAZO ES PATRICIA AGUIRRE (ALIAS PATO). "
            f"TENGO MUCHO MIEDO POR MI Y POR MI FAMILIA, POR ESO PIDO QUE NO SE NOS ACERQUEN."
        )
        st.session_state["victima_out"] = narrativa

    relato_final = st.text_area("Relato Final:", value=st.session_state.get("victima_out", ""), height=150)

    # SECCIÓN DE DESCARGA
    st.markdown("---")
    if st.button("💾 Generar Documento"):
        f_nac_str = fecha_nac.strftime("%d/%m/%Y") if fecha_nac else "S/D"
        pdf_data = generar_pdf_victima_bytes({
            "filiacion": {
                "nombre": nombre, "dni": dni, "sexo": sexo, "fecha_nac": f_nac_str,
                "ocupacion": ocupacion,
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
