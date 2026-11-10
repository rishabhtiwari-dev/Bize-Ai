import os
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
STATIC_DIR = BASE_DIR / "app" / "web" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "web" / "templates"

# Network & Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")  # e.g., http://localhost:11434/v1 for Ollama
LLM_MODEL = os.getenv("LLM_MODEL", "")  # auto-detected based on provider if empty

# RAG Configuration
TOP_K = int(os.getenv("TOP_K", 4))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", 0.05))

def get_local_ip() -> str:
    """Detect the machine's primary local LAN IP address for phone/tablet access."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually establish a connection; used to resolve outgoing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()
