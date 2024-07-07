import streamlit as st
import requests
import base64
import google.generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def process_content(content, image=None):
    model = genai.GenerativeModel('gemini-1.5-pro')

    if image:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        response = model.generate_content([content, img_byte_arr])
    else:
        response = model.generate_content(content)

    return response.text

def update_notion(content):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "New Note"
                        }
                    }
                ]
            },
            "Content": {
                "rich_text": [
                    {
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def main():
    st.title("AI Notes to Notion App")

    # Text input for typed notes
    text_input = st.text_area("Enter your notes here:", height=150)

    # File uploader for existing images
    uploaded_file = st.file_uploader("Choose an image of your notes", type=["jpg", "jpeg", "png"])

    # Camera input for capturing photos
    camera_input = st.camera_input("Take a picture of your notes")

    if st.button('Process Notes and Update Notion'):
        with st.spinner('Processing...'):
            content = ""
            image = None

            if text_input:
                content += f"Typed notes: {text_input}\n\n"

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                content += "Processing uploaded image...\n"

            if camera_input is not None:
                image = Image.open(camera_input)
                st.image(image, caption='Captured Image', use_column_width=True)
                content += "Processing captured image...\n"

            if content or image:
                # Process the content using Gemini API
                processed_content = process_content(content, image)
                st.write("Processed content:", processed_content)

                # Update Notion
                if update_notion(processed_content):
                    st.success("Successfully updated Notion!")
                else:
                    st.error("Failed to update Notion. Please check your API key and database ID.")
            else:
                st.warning("Please enter some text or upload/capture an image before processing.")

if __name__ == "__main__":
    main()