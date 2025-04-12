import streamlit as st
import requests
import pandas as pd
import json

# Configure the page
st.set_page_config(page_title="File Processor", layout="centered")
st.title("File Processor")

# Dropdown to select the path
option = st.selectbox(
    "Select input type:",
    ("Images & PDFs", "Text", "URLs"),
    index=0
)

if option == "Images & PDFs":
    st.subheader("Upload a file (PDF, JPEG, or PNG)")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        if uploaded_file.size <= 5 * 1024 * 1024:
            st.success("Cargado Exitosamente")
            
            if st.button("Procesar"):
                with st.spinner("Procesando posición...", show_time=True):
                    try:
                        api_url = "https://liq2d5.buildship.run/file-upload"
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        response = requests.post(api_url, files=files)
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            value_content = response_data.get("value", "")
                            
                            try:
                                inner_json = json.loads(value_content)
                                df = pd.DataFrame([inner_json])
                                
                                # DataFrame display configuration
                                st.data_editor(
                                    df,
                                    hide_index=True,  # Hides the index column
                                    column_config={
                                        "Description": st.column_config.TextColumn(
                                            "Description",
                                            width="large",  # Makes description column wider
                                            help="Job description details",
                                        )
                                    },
                                    use_container_width=True
                                )
                                
                            except json.JSONDecodeError:
                                st.markdown(value_content)
                        
                        else:
                            st.error(f"API Error: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.error("Por favor solo imágenes y PDFs hasta 5MB")