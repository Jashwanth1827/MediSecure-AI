import sys
import os
import tempfile
import logging

# Vercel serverless fix: use /tmp for writable files
os.environ['VERCEL'] = '1'
os.environ['CHATBOT_DB_PATH'] = os.path.join(tempfile.gettempdir(), 'chat_history.db')
os.environ['TMPDIR'] = tempfile.gettempdir()

# Suppress logging to avoid file write issues
logging.getLogger().setLevel(logging.WARNING)

# Import Flask app
from app import app as application

# Vercel expects `app` as the handler
app = application
