import os
import re
import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
import gdown
import zipfile
import requests
import shutil
from natsort import natsorted

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

active_extractions = {}

def extract_file_id(url):
    """Extract file ID from various Google Drive URL formats"""
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/folders/([a-zA-Z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_from_drive(file_id, output_path):
    """Download file from Google Drive using file ID"""
    try:
        gdown.download(id=file_id, output=output_path, quiet=False, fuzzy=True)
        return True
    except:
        pass
    
    try:
        url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
        session = requests.Session()
        response = session.get(url, stream=True)
        
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={value}"
                response = session.get(url, stream=True)
                break
