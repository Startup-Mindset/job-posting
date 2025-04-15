import re
import requests
import json
import pandas as pd

def is_valid_url(url):
    """Validate URL format"""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url.startswith(('http://', 'https://')) and bool(pattern.match(url))

def process_file(file_content, file_name, api_endpoint):
    """Process uploaded file through API"""
    try:
        response = requests.post(
            api_endpoint,
            files={"file": (file_name, file_content)}
        )
        return handle_api_response(response)
    except Exception as e:
        raise Exception(f"File processing failed: {str(e)}")

def process_url(url, api_endpoint):
    """Process URL through API"""
    if not is_valid_url(url):
        raise ValueError("Invalid URL format")
    
    try:
        response = requests.post(
            api_endpoint,
            json={"websiteUrl": url},
            headers={"Content-Type": "application/json"}
        )
        return handle_api_response(response)
    except Exception as e:
        raise Exception(f"URL processing failed: {str(e)}")

def handle_api_response(response):
    """Handle API response and return standardized data"""
    if response.status_code == 200:
        try:
            response_data = response.json()
            if isinstance(response_data, dict):
                # Handle both direct responses and responses with 'value' field
                content = response_data.get('value', response_data)
                
                # If content is a string, try to parse it as JSON
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
                return content
            return response_data
        except json.JSONDecodeError:
            return response.text
    elif response.status_code == 500:
        raise Exception("Multiple job postings detected. Please use the specific job posting URL.")
    else:
        raise Exception(f"API Error: {response.status_code}")

def display_job_data(job_data):
    """Display job data in appropriate format"""
    if isinstance(job_data, dict):
        # Ensure we have a flat dictionary for DataFrame conversion
        flat_data = {k: str(v) if isinstance(v, (list, dict)) else v 
                   for k, v in job_data.items()}
        return pd.DataFrame([flat_data])
    elif isinstance(job_data, str):
        return job_data
    else:
        return str(job_data)
    

def process_text(text, api_endpoint):
    """Send raw text to API for processing."""
    try:
        response = requests.post(
            api_endpoint,
            json={"text": text},  # Using the expected payload format
            headers={"Content-Type": "application/json"}
        )
        return handle_api_response(response)
    except Exception as e:
        raise Exception(f"Text processing failed: {str(e)}")