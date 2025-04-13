import streamlit as st
import requests
import pandas as pd
import json
import re

# --- URL Validation ---
def is_valid_url(url):
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url.startswith(('http://', 'https://')) and bool(pattern.match(url))

# --- App Config ---
st.set_page_config(page_title="Job Processor", layout="wide")
st.title("Job Posting Processor")

option = st.selectbox(
    "Select input type:",
    ("Images & PDFs", "Text", "URLs"),
    index=0
)

# ===== PATH 1: Images/PDFs =====
if option == "Images & PDFs":
    st.subheader("Upload Job Posting")
    uploaded_file = st.file_uploader(
        "PDF or Image (JPEG/PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        if uploaded_file.size <= 5 * 1024 * 1024:
            st.success("✓ File uploaded successfully")
            if st.button("Process"):
                with st.spinner("Extracting job details...", show_time=True):
                    try:
                        response = requests.post(
                            "https://liq2d5.buildship.run/file-upload",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue())}
                        )
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            content = response_data.get("value", "")
                            
                            try:
                                job_data = json.loads(content) if isinstance(content, str) else content
                                if isinstance(job_data, dict):
                                    df = pd.DataFrame([job_data])
                                    st.data_editor(
                                        df,
                                        hide_index=True,
                                        column_config={
                                            "Description": st.column_config.TextColumn(width="large"),
                                            "apply_URL": st.column_config.LinkColumn("Apply Link")
                                        },
                                        use_container_width=True
                                    )
                                else:
                                    st.markdown(str(job_data))
                            except (json.JSONDecodeError, AttributeError):
                                st.markdown(content)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Processing failed: {str(e)}")
        else:
            st.error("File size must be under 5MB")

# ===== PATH 3: URLs =====
elif option == "URLs":
    st.subheader("Enter Job Posting URL")
    url = st.text_input("Paste job posting URL:", placeholder="https://example.com/job-posting")
    
    if url:
        if not is_valid_url(url):
            st.error("Please enter a valid URL starting with http:// or https://")
        elif st.button("Process"):
            with st.spinner("Analyzing job posting...", show_time=True):
                try:
                    response = requests.post(
                        "https://liq2d5.buildship.run/text-url-v-3-copy-df79b737eab2",
                        json={"websiteUrl": url},
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        # First try to parse as JSON
                        try:
                            response_data = response.json()
                            
                            # Handle case where API returns JSON with 'value' field
                            if 'value' in response_data:
                                content = response_data['value']
                                try:
                                    # If value is JSON string, parse it
                                    if isinstance(content, str):
                                        content = json.loads(content)
                                    
                                    # If we have a dictionary, show as DataFrame
                                    if isinstance(content, dict):
                                        df = pd.DataFrame([content])
                                        st.data_editor(
                                            df,
                                            hide_index=True,
                                            column_config={
                                                "Description": st.column_config.TextColumn(width="large"),
                                                "apply_URL": st.column_config.LinkColumn("Apply Link")
                                            },
                                            use_container_width=True
                                        )
                                    else:
                                        # For non-dict JSON, show as Markdown
                                        st.markdown(str(content))
                                except json.JSONDecodeError:
                                    # If value is plain text, show as Markdown
                                    st.markdown(content)
                            else:
                                # For direct JSON responses without 'value' field
                                df = pd.DataFrame([response_data])
                                st.data_editor(
                                    df,
                                    hide_index=True,
                                    column_config={
                                        "Description": st.column_config.TextColumn(width="large"),
                                        "apply_URL": st.column_config.LinkColumn("Apply Link")
                                    },
                                    use_container_width=True
                                )
                        except json.JSONDecodeError:
                            # If response is not JSON at all, display as Markdown
                            st.markdown(response.text)
                    else:
                        st.error(f"API Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")


# ===== PATH 2: Text (Placeholder) =====
elif option == "Text":
    st.subheader("Paste Job Description")
    text_input = st.text_area("Enter job description text:", height=200)
    st.warning("Text processing feature coming soon!")