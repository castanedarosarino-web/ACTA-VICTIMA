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
    interviniente = st.text_input(
        "Rango y Nombre",
        value="SUB COMISARIO CASTAÑEDA JUAN",
        disabled=False
    )
    st.markdown("---")
    st.subheader("Lugar del Hecho")
    lugar = st.text_input("Dirección", placeholder="EJ: CALLE BRANDSEN 123, ZAVALLA")
    st.subheader("Hora del Hecho")
    hora_hecho = st.text_input("HH:MM", value=datetime.now().strftime("%H:%M"))

def limpiar_texto_pdf(texto):
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
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=25, top=20, right=15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- ENCABEZADO ---
    pdf.set_font("Arial", "B", 8)
    pdf.cell(0, 4, "POLICIA DE LA PROVINCIA", ln=True, align="L")
    pdf.cell(0, 4, "UNIDAD REGIONAL II - ROSARIO", ln=True, align="L")
    pdf.cell(0, 4, "SUBCOMISARIA ZAVALLA", ln=True, align="L")
    pdf.ln(8)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "ACTA DE DECLARACION DE VICTIMA", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, limpiar_texto_pdf(
        f"En la localidad de Zavalla, a los {datetime.now().strftime('%d')} dias del mes de "
        f"{datetime.now().strftime('%B')} de {datetime.now().strftime('%Y')}, siendo las {hora} horas, "
        f"ante el interviniente {interviniente}, comparece la victima de autos:"
    ))
    pdf.ln(5)

    # --- FILIACIÓN ---
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

    # --- RELATO ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "II. RELATO DE LOS HECHOS:", ln=True)
    pdf.set_font("Arial", "", 11)
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

    with st.expander("👤 DATOS FILIATORIOS DE LA VÍCTIMA", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Apellido y Nombres").upper()
        dni = c2.text_input("DNI")
        sexo = c3.selectbox("Sexo", ["MASCULINO", "FEMENINO", "OTRO"])
        
        c4, c5, c6 = st.columns([1, 1, 1])
        ocupacion = c4.text_input("Ocupación").upper()
        fecha_nac = c5.date_input("Fecha de Nacimiento", value=None, min_value=datetime(1920, 1, 1), max_value=datetime.now(), format="DD/MM/YYYY")
        nacionalidad = c6.text_input("Nacionalidad", value="ARGENTINA").upper()
        
        domicilio = st.text_input("Domicilio Real").upper()
        telefono = st.text_input("Teléfono")

    st.subheader("✍️ Relato de la Denuncia")
    # CAMPO VACÍO PARA CUALQUER CASO NUEVO
    relato_espontaneo = st.text_area("Ingrese el relato espontáneo de la víctima:", height=150, placeholder="Escriba aquí lo que manifiesta la persona...")

    if st.button("✨ Procesar Relato"):
        if relato_espontaneo:
            # Aquí la IA pasaría el texto a MAYÚSCULAS y agregaría la muletilla policial
            narrativa = f"QUE EN LA FECHA MANIFIESTA QUE: {relato_espontaneo.upper()}"
            st.session_state["victima_out"] = narrativa
        else:
            st.warning("Primero debe ingresar el relato de la víctima.")

    relato_final = st.text_area("Relato Final para el PDF:", value=st.session_state.get("victima_out", ""), height=150)

    st.markdown("---")
    if st.button("💾 Generar Documento"):
        f_nac_str = fecha_nac.strftime("%d/%m/%Y") if fecha_nac else "S/D"
        pdf_data = generar_pdf_victima_bytes({
            "filiacion": {
                "nombre": nombre, "dni": dni, "sexo": sexo, "fecha_nac": f_nac_str,
                "ocupacion": ocupacion, "domicilio": domicilio, "telefono": telefono
            },
            "contenido": relato_final
        }, interviniente, lugar, hora_hecho)
        
        st.download_button(label="📄 DESCARGAR PDF", data=pdf_data, file_name=f"Acta_Victima_{dni}.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
