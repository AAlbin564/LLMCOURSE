from google import genai
from dotenv import load_dotenv
import dotenv
import pydantic
import os
import gradio as gr
from google.genai import types



import os
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


default_model = "gemini-2.5-flash"

resp  = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=" hello ",
        config=types.GenerateContentConfig(
           system_instruction = f"""
                You are a Uppsala university Expert. 
                """,
        )
)

print(f"response {resp.text!r}")
