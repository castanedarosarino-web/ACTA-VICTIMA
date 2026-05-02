
import streamlit as st
import json

# --- MOTOR DE DETECCIÓN (Lógica de calificación automática) ---
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

# --- BLOQUE 3: VÍCTIMA (Módulo Completo) ---
def bloque_victima():
    st.header("👤 Bloque 3: Declaración de la Víctima")
    st.info("Nota: La redacción final se generará automáticamente en primera persona del singular (YO).")

    # 1. ENTRADA DE DATOS CRUDA
    relato_crudo = st.text_area(
        "Relato espontáneo (Lo que la persona cuenta):",
        value=st.session_state.data_operativa.get("relato_vic_crudo", ""),
        height=150,
        help="Escriba aquí el borrador. No use lenguaje policial, use las palabras de la víctima."
    )
    st.session_state.data_operativa["relato_vic_crudo"] = relato_crudo

    if relato_crudo:
        # Detección automática del protocolo
        delito_sugerido = detectar_delito(relato_crudo)
        st.warning(f"⚖️ PROTOCOLO DETECTADO: {delito_sugerido}")

        # 2. CAMPOS DINÁMICOS SEGÚN EL DELITO (Protocolos Obligatorios)
        st.markdown("### 📋 Protocolo Específico")
        col1, col2 = st.columns(2)

        if "LESIONES" in delito_sugerido:
            with col1:
                st.session_state.data_operativa["vic_insta_accion"] = st.checkbox("¿Insta la acción penal? (Art. 72 CP)", value=True)
                st.session_state.data_operativa["vic_asistencia"] = st.radio("¿Recibió asistencia médica?", ["SÍ", "NO"])
            with col2:
                st.session_state.data_operativa["vic_medico"] = st.text_input("Médico / Centro de Salud")

        elif "AMENAZAS" in delito_sugerido:
            with col1:
                st.session_state.data_operativa["vic_dichos"] = st.text_area("Dichos textuales del autor (Entre comillas)")
            with col2:
                st.session_state.data_operativa["vic_temor"] = st.radio("¿Siente temor por su integridad?", ["SÍ", "NO"])

        elif "ROBO" in delito_sugerido or "HURTO" in delito_sugerido:
            with col1:
                st.session_state.data_operativa["vic_bienes"] = st.text_input("Bienes sustraídos (Detalle técnico)")
            with col2:
                if "ROBO" in delito_sugerido:
                    st.session_state.data_operativa["vic_fuerza"] = st.text_input("Detalle de la fuerza/daño")

        # 3. DATOS FILIATORIOS
        st.divider()
        st.markdown("### 🆔 Datos Personales")
        c3, c4, c5 = st.columns(3)
        st.session_state.data_operativa["vic_nombre"] = c3.text_input("Nombre Completo", value=st.session_state.data_operativa.get("vic_nombre", ""))
        st.session_state.data_operativa["vic_dni"] = c4.text_input("DNI (Solo números)", value=st.session_state.data_operativa.get("vic_dni", ""))
        st.session_state.data_operativa["vic_tel"] = c5.text_input("Teléfono de contacto")

        # 4. TRANSFORMACIÓN NARRATIVA (Preguntas Camufladas)
        st.divider()
        st.markdown("### 📝 Vista Previa del Acta")
        
        # Construcción lógica del relato (Carga narrativa)
        narrativa = f"Yo, {st.session_state.data_operativa['vic_nombre']}, DNI {st.session_state.data_operativa['vic_dni']}, comparezco y expongo: Que en relación al hecho que se investiga, manifiesto que {relato_crudo}. "
        
        if st.session_state.data_operativa.get("vic_insta_accion"):
            narrativa += "Por las lesiones que presento, es mi deseo expreso instar la acción penal contra el autor del hecho. "
        
        if st.session_state.data_operativa.get("vic_temor") == "SÍ":
            narrativa += "Hago constar que, debido a los dichos recibidos, siento un temor real por mi vida e integridad física. "
            
        if st.session_state.data_operativa.get("vic_asistencia") == "SÍ":
            narrativa += f"Asimismo, manifiesto que fui asistida médicamente en el lugar por el profesional {st.session_state.data_operativa.get('vic_medico', 'interviniente')}. "

        texto_final_vic = st.text_area("Texto listo para el Escribiente:", value=narrativa, height=200)

        # 5. BOTONES DE ACCIÓN (Coherencia del Programa)
        st.divider()
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 COPIAR Y LISTO PARA PEGAR EN IA"):
                prompt_ia = f"Actuá como víctima. Redactá en primera persona del singular (YO) de forma profesional pero natural: {texto_final_vic}"
                st.components.v1.html(f"<script>navigator.clipboard.writeText(`{prompt_ia}`);</script>", height=0)
                st.success("✅ ¡Copiado! Pegalo en la IA para el toque final.")

        with col_btn2:
            data_json = json.dumps(st.session_state.data_operativa, indent=4)
            st.download_button(
                label="💾 GUARDAR ENTREVISTA VÍCTIMA (JSON)",
                data=data_json,
                file_name=f"entrevista_vic_{st.session_state.data_operativa['vic_dni']}.json",
                mime="application/json",
                use_container_width=True
            )

# Llamada al bloque en la pestaña correspondiente
# bloque_victima()
