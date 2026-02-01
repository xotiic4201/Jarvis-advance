# ============================================================================
# JARVIS AI - MINIMAL REQUIREMENTS (Core Features Only)
# ============================================================================
# This is a minimal installation for basic JARVIS functionality
# For full features, use requirements.txt instead
# ============================================================================

# Core AI & LLM
langchain>=0.1.0
langchain-community>=0.0.20
langchain-ollama>=0.0.1
langchain-core>=0.1.0

# Speech & Voice
SpeechRecognition>=3.10.0
pyttsx3>=2.90
pyaudio>=0.2.13

# GUI
PyQt6>=6.6.0

# System Control
psutil>=5.9.0
pyautogui>=0.9.54
pyperclip>=1.8.2

# Image & OCR
Pillow>=10.0.0
pytesseract>=0.3.10
mss>=9.0.0

# Web & Utilities
requests>=2.31.0
beautifulsoup4>=4.12.0
duckduckgo-search>=3.9.0
python-dotenv>=1.0.0

# Windows-specific (auto-skipped on other platforms)
pywin32>=306; platform_system=='Windows'

# ============================================================================
# NOTE: After installing these packages, you also need:
# 1. Ollama (from https://ollama.ai)
# 2. Tesseract OCR (from https://github.com/UB-Mannheim/tesseract/wiki)
# ============================================================================
