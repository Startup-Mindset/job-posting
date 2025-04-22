import re
import requests
import json
import pandas as pd
from notion_client import Client
import logging


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
    if isinstance(job_data, dict):
        # Convert dict to DataFrame
        return pd.DataFrame([job_data])
    elif isinstance(job_data, str):
        # Return text directly
        return job_data
    else:
        # Fallback string conversion
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
    
def send_to_notion(data, database_id, token):
    """Send processed job data to Notion database.
    
    Args:
        data (dict): Job data matching Notion's property schema
        database_id (str): Notion database ID
        token (str): Notion integration token
    
    Returns:
        str: URL of the created Notion page
    """
    try:
        notion = Client(auth=token)
        
        # Map our data to Notion properties
        new_page = {
            "Role": {"title": [{"text": {"content": data["Job Title"]}}]},
            "Startup": {"rich_text": [{"text": {"content": data["Company"]}}]},
            "Apply URL": {"url": data["apply_Url"]},
            "Summary": {"rich_text": [{"text": {"content": data["Description"]}}]},
            "Location": {"rich_text": [{"text": {"content": data["Location"]}}]},
            "Remote": {"select": {"name": data["Remote"]}}
        }

        # Only add file_URL if it exists and isn't empty
        if data.get("file_Url"):
            new_page["Original file"] = {"url": data["file_Url"]}
        
        created_page = notion.pages.create(
            parent={"database_id": database_id},
            properties=new_page
        )
        
        return created_page["url"]
    
    except Exception as e:
        logging.error(f"Notion API error: {str(e)}")
        raise Exception(f"Failed to send to Notion: {str(e)}")