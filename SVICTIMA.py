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

# --- SIDEBAR ---
with st.sidebar:
    st.header("Oficial Interviniente")
    interviniente = st.text_input("Rango y Nombre", value="SUB COMISARIO CASTAÑEDA JUAN")
    st.markdown("---")
    st.subheader("Lugar del Hecho")
    lugar = st.text_input("Dirección", placeholder="EJ: CALLE BRANDSEN 123, ZAVALLA")
    st.subheader("Hora del Hecho")
    hora_hecho = st.text_input("HH:MM", value=datetime.now().strftime("%H:%M"))

def limpiar_texto_pdf(texto):
    if texto is None: return ""
    reemplazos = {"ñ": "n", "Ñ": "N", "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "°": "Nro."}
    texto = str(texto)
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    return texto

def generar_pdf_victima_bytes(datos, interviniente, lugar, hora):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=25, top=20, right=15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ENCABEZADO
    pdf.set_font("Arial", "B", 8)
    pdf.cell(0, 4, "POLICIA DE LA PROVINCIA - UR II", ln=True)
    pdf.cell(0, 4, "SUBCOMISARIA ZAVALLA", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "ACTA DE DECLARACION DE VICTIMA", ln=True, align="C")
    pdf.ln(5)

    # FILIACIÓN
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "I. DATOS FILIATORIOS DEL DENUNCIANTE:", ln=True)
    pdf.set_font("Arial", "", 11)
    f = datos["filiacion"]
    pdf.cell(50, 7, "Apellido y Nombres:", 1, 0); pdf.cell(0, 7, limpiar_texto_pdf(f['nombre']), 1, 1)
    pdf.cell(50, 7, "D.N.I. / F. Nac:", 1, 0); pdf.cell(0, 7, f"{f['dni']} | {f['fecha_nac']}", 1, 1)
    # Agregamos Correo al PDF
    pdf.cell(50, 7, "Tel / Correo:", 1, 0); pdf.cell(0, 7, limpiar_texto_pdf(f"{f['telefono']} | {f['correo']}"), 1, 1)
    pdf.multi_cell(0, 7, limpiar_texto_pdf(f"Domicilio Real: {f['domicilio']}"), 1)
    pdf.ln(8)

    # RELATO
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "II. RELATO DE LOS HECHOS:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, limpiar_texto_pdf(datos["contenido"]), 0, 'J')

    # FIRMAS
    pdf.ln(30)
    pdf.cell(90, 8, "------------------------------------", 0, 0, "C")
    pdf.cell(90, 8, "------------------------------------", 0, 1, "C")
    pdf.cell(90, 6, "FIRMA VICTIMA", 0, 0, "C")
    pdf.cell(90, 6, "FIRMA INTERVINIENTE", 0, 1, "C")

    return pdf.output(dest="S").encode("latin-1", errors="replace")

def main():
    st.title("🚓 S.I.V. - Bloque 3: GESTIÓN DE VÍCTIMAS")
    st.caption("Autor: Sub Comisario CASTAÑEDA Juan")

    with st.expander("👤 DATOS FILIATORIOS", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Apellido y Nombres").upper()
        dni = c2.text_input("DNI")
        sexo = c3.selectbox("Sexo", ["MASCULINO", "FEMENINO", "OTRO"])
        
        c4, c5, c6 = st.columns([1, 1, 1])
        ocupacion = c4.text_input("Ocupación").upper()
        fecha_nac = c5.date_input("Fecha de Nacimiento", value=None, min_value=datetime(1920, 1, 1), max_value=datetime.now(), format="DD/MM/YYYY")
        nacionalidad = c6.text_input("Nacionalidad", value="ARGENTINA").upper()
        
        c7, c8 = st.columns([1, 1])
        telefono = c7.text_input("Teléfono")
        # RECUPERAMOS EL CORREO
        correo = c8.text_input("Correo Electrónico")
        
        domicilio = st.text_input("Domicilio Real").upper()

    st.subheader("✍️ Relato")
    relato_espontaneo = st.text_area("Ingrese el relato:", height=150)

    if st.button("✨ Procesar Relato"):
        st.session_state["victima_out"] = f"QUE EN LA FECHA MANIFIESTA QUE: {relato_espontaneo.upper()}"

    relato_final = st.text_area("Relato Final:", value=st.session_state.get("victima_out", ""), height=150)

    # PREPARACIÓN DE DATOS PARA EXPORTAR
    f_nac_str = fecha_nac.strftime("%d/%m/%Y") if fecha_nac else "S/D"
    datos_completos = {
        "filiacion": {
            "nombre": nombre, "dni": dni, "sexo": sexo, "fecha_nac": f_nac_str,
            "ocupacion": ocupacion, "domicilio": domicilio, "telefono": telefono, "correo": correo
        },
        "contenido": relato_final
    }

    # SECCIÓN DE DESCARGAS (RECUPERAMOS EL BOTÓN JSON)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        # BOTÓN JSON PARA EL ACTANTE
        st.download_button(
            label="📥 EXPORTAR JSON (ACTANTE)",
            data=json.dumps(datos_completos, indent=4, ensure_ascii=False),
            file_name=f"victima_{dni}.json",
            mime="application/json"
        )
    with col2:
        if st.button("💾 Generar PDF"):
            pdf_data = generar_pdf_victima_bytes(datos_completos, interviniente, lugar, hora_hecho)
            st.download_button(label="📄 DESCARGAR PDF", data=pdf_data, file_name=f"Acta_Victima_{dni}.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
