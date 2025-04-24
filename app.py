import streamlit as st
import pandas as pd
from utils import (
    is_valid_url,
    process_file,
    process_text,
    process_url,
    display_job_data,
    send_to_notion
)

# --- Initialize Session State ---
if 'job_data' not in st.session_state:
    st.session_state.job_data = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'display_mode' not in st.session_state:  # 'table' or 'text'
    st.session_state.display_mode = None

# --- App Config ---
st.set_page_config(page_title="Job Processor", layout="wide")

# --- Processing Functions ---
def process_and_store_data(processor, *args):
    """Universal processing function for all paths"""
    try:
        st.session_state.job_data = processor(*args)
        result = display_job_data(st.session_state.job_data)
        
        if isinstance(result, pd.DataFrame):
            st.session_state.df = result
            st.session_state.display_mode = 'table'
        else:
            st.session_state.display_mode = 'text'
            st.session_state.text_output = str(result)
            
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        st.session_state.display_mode = None

# --- Main UI ---
option = st.selectbox(
    "Selecciona la opción que desees:",
    ("Imágenes & PDFs", "Texto", "URLs"),
    index=0
)

# ===== PATH 1: Images/PDFs =====
if option == "Imágenes & PDFs":
    st.markdown("##### Por favor sube una posición de trabajo")
    uploaded_file = st.file_uploader(
        "PDF o Imagen (JPEG/PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=False
    )
    
    if uploaded_file and st.button("Process"):
        if uploaded_file.size <= 5 * 1024 * 1024:
            with st.spinner("Extrayendo los detalles...", show_time=True):
                process_and_store_data(
                    process_file,
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                    st.secrets["api_file"]
                )
        else:
            st.error("El archivo debe pesar menos de 5MB")

# ===== PATH 2: Texto =====
elif option == "Texto":
    st.markdown("##### Pega el texto de la posición de trabajo")
    text_input = st.text_area("Ingresa el texto de la posición:", height=200)
    
    if text_input.strip() and st.button("Procesar"):
        with st.spinner("Analizando texto...", show_time=True):
            process_and_store_data(
                process_text,
                text_input,
                st.secrets["api_text"]
            )

# ===== PATH 3: URLs =====
elif option == "URLs":
    st.markdown("##### Ingresa el URL de la posición")
    url = st.text_input("Pega el URL:", placeholder="https://example.com/job-posting")
    
    if url and st.button("Process"):
        if not is_valid_url(url):
            st.error("URL inválido. Debe comenzar con http:// o https://")
        else:
            with st.spinner("Analizando URL...", show_time=True):
                process_and_store_data(
                    process_url,
                    url,
                    st.secrets["api_text"]
                )

# ===== Display Results =====
st.divider()
if st.session_state.display_mode == 'table':
    st.markdown("##### Resultados")
    edited_df = st.data_editor(
        st.session_state.df,
        hide_index=True,
        column_config={
            "Description": st.column_config.TextColumn(width="large"),
            "apply_URL": st.column_config.LinkColumn("Apply Link")
        },
        key="data_editor"
    )
    
    # Auto-save changes
    if not edited_df.equals(st.session_state.df):
        st.session_state.df = edited_df
        st.session_state.job_data = edited_df.to_dict('records')[0]
    
    # --- New Notion Integration UI ---
    st.divider()
    confirmed = st.checkbox("La data es correcta y quiero postearla")
    
    if confirmed:
        if st.button("Enviar a Revisión", type="primary"):
            with st.spinner("Enviando a Revisión..."):
                try:
                    # Convert DataFrame to dict
                    job_data = st.session_state.df.to_dict('records')[0]
                    
                    # Send to Notion
                    notion_page_url = send_to_notion(
                        data=job_data,
                        database_id=st.secrets["notion_database_id"],
                        token=st.secrets["notion_token"]
                    )
                    
                    st.success(f"¡Enviada con Éxito!")
                except Exception as e:
                    st.error(f"Error al enviar a Revisión: {str(e)}")

elif st.session_state.display_mode == 'text':
    st.markdown("##### Resultados")
    st.markdown(st.session_state.text_output)
