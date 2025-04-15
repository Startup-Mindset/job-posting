import streamlit as st
import pandas as pd
from utils import (
    is_valid_url,
    process_file,
    process_url,
    display_job_data,
    process_text
)

# --- Get API endpoints from secrets ---
API_FILE = st.secrets["api_file"]
API_TEXT = st.secrets["api_text"]

# --- App Config ---
st.set_page_config(page_title="Job Processor", layout="wide")
st.markdown(
    '''
    ### Proceso
    1. Envía la posición en el formato que desees 
    2. Puedes el resultado final y editarlo dando click en la columna que desees
    3. Cuando la posición este lista, envíala en ***Enviar a Notion***
    4. En menos de 24h podrás ver la posición en nuestra plataforma

    '''
    )

st.divider()

option = st.selectbox(
    "Selecciona la opción que desees:",
    ("Imágenes & PDFs", "Texto", "URLs"),
    index=0
)

# ===== PATH 1: Images/PDFs =====
if option == "Imágenes & PDFs":
    st.subheader("Por favor sube una posición de trabajo")
    uploaded_file = st.file_uploader(
        "PDF o Imagen (JPEG/PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        if uploaded_file.size <= 5 * 1024 * 1024:
            st.success("✓ Archivo cargado con Éxito")
            if st.button("Process"):
                with st.spinner("Extrayendo los detalles de la posición...", show_time=True):
                    try:
                        job_data = process_file(
                            file_content=uploaded_file.getvalue(),
                            file_name=uploaded_file.name,
                            api_endpoint=API_FILE
                        )
                        result = display_job_data(job_data)
                        
                        if isinstance(result, pd.DataFrame):
                            st.data_editor(
                                result,
                                hide_index=True,
                                column_config={
                                    "Description": st.column_config.TextColumn(width="large"),
                                    "apply_URL": st.column_config.LinkColumn("Apply Link")
                                },
                                use_container_width=True
                            )
                        else:
                            st.markdown(result)
                    except Exception as e:
                        st.error(str(e))
        else:
            st.error("El archivo debe pesar menos de 5MB")

# ===== PATH 3: URLs =====
elif option == "URLs":
    st.subheader("Ingresa el URL de la posición")
    url = st.text_input("Pega el URL:", placeholder="https://example.com/job-posting")
    
    if url:
        if not is_valid_url(url):
            st.error("Por favor ingresa un URL válido que empiece con http:// o https://")
        elif st.button("Process"):
            with st.spinner("Analizando posición de trabajo...", show_time=True):
                try:
                    job_data = process_url(url, API_TEXT)
                    result = display_job_data(job_data)
                    
                    if isinstance(result, pd.DataFrame):
                        st.data_editor(
                            result,
                            hide_index=True,
                            column_config={
                                "Description": st.column_config.TextColumn(width="large"),
                                "apply_URL": st.column_config.LinkColumn("Apply Link")
                            },
                            use_container_width=True
                        )
                    else:
                        st.markdown(result)
                except Exception as e:
                    st.error(str(e))

# ===== PATH 2: Text (Process Text Input) =====
elif option == "Texto":
    st.subheader("Pega el texto de la posición de trabajo")
    text_input = st.text_area("Ingresa el texto de la posición:", height=200, key="job_text_input")
    
    if text_input.strip():
        if st.button("Procesar Texto"):
            with st.spinner("Analizando texto de la posición...", show_time=True):
                try:
                    # Call the dedicated text processor
                    job_data = process_text(text_input, API_TEXT)
                    result = display_job_data(job_data)
                    
                    if isinstance(result, pd.DataFrame):
                        st.data_editor(
                            result,
                            hide_index=True,
                            column_config={
                                "Description": st.column_config.TextColumn(width="large"),
                                "apply_URL": st.column_config.LinkColumn("Apply Link")
                            },
                            use_container_width=True
                        )
                    else:
                        st.markdown(result)
                except Exception as e:
                    st.error(f"Error al procesar el texto: {str(e)}")
    else:
        st.warning("Por favor ingresa el texto de la posición antes de procesar.")