import os
import logging
import time
import threading
import sys
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random
import math
import re
import socket
import warnings
import webbrowser
import subprocess
import psutil

warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- LangChain & AI Memory ---
from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# --- PyQt6 UI ---
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QColorDialog, 
                            QMessageBox, QInputDialog, QVBoxLayout, QLabel,
                            QPushButton, QHBoxLayout, QDialog, QTextEdit,
                            QListWidget, QListWidgetItem, QScrollArea, QGridLayout,
                            QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import (QPainter, QPainterPath, QRadialGradient, QLinearGradient, 
                        QColor, QFont, QPen, QBrush, QFontMetrics, QIcon, QKeyEvent)

from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QColorDialog, 
                            QMessageBox, QInputDialog, QVBoxLayout, QLabel,
                            QPushButton, QHBoxLayout, QDialog, QTextEdit,
                            QListWidget, QListWidgetItem, QScrollArea, QGridLayout,
                            QLineEdit, QGroupBox)  # Add QGroupBox here
# --- Speech & TTS ---
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# --- Tool Integration ---
from langchain.tools import tool as langchain_tool

# ============================================================================
# OLLAMA AUTO-DETECTION AND SETUP
# ============================================================================

def check_ollama_connection():
    """
    Check if Ollama is running and accessible
    Returns: (bool, str) - (is_connected, status_message)
    """
    print("\n🔍 Checking Ollama connection...")
    
    def is_ollama_installed():
        """Check if Ollama is installed"""
        try:
            # Try to run ollama --version
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode == 0
        except:
            return False
    
    def is_ollama_running():
        """Check if Ollama process is running"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'ollama' in proc.info['name'].lower():
                return True
        return False
    
    def can_connect_to_ollama():
        """Check if we can connect to Ollama API"""
        try:
            socket.create_connection(('localhost', 11434), timeout=3)
            return True
        except:
            return False
    
    def start_ollama():
        """Start Ollama service"""
        print("🚀 Starting Ollama service...")
        try:
            # Start Ollama in background
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NO_WINDOW,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for _ in range(15):
                time.sleep(1)
                if can_connect_to_ollama():
                    return True
            return False
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False
    
    # Check installation
    if not is_ollama_installed():
        print("❌ Ollama is not installed!")
        print("\n📥 To enable AI features, please install Ollama:")
        print("   1. Download from: https://ollama.ai")
        print("   2. Run the installer")
        print("   3. Open terminal and run: ollama pull qwen2.5:7b")
        print("   4. Restart JARVIS")
        
        # Ask user if they want to open browser
        response = input("\nOpen browser to download Ollama? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://ollama.ai')
        
        return False, "Ollama not installed"
    
    # Check if running
    if not is_ollama_running():
        print("⚡ Ollama not running, attempting to start...")
        if not start_ollama():
            print("❌ Could not start Ollama service")
            print("\n💡 Please manually start Ollama:")
            print("   - Open terminal and run: ollama serve")
            print("   - Wait for it to start, then restart JARVIS")
            return False, "Ollama service not running"
    
    # Check connection
    if not can_connect_to_ollama():
        print("❌ Cannot connect to Ollama API")
        print("\n💡 Troubleshooting steps:")
        print("   1. Make sure Ollama is running: ollama serve")
        print("   2. Check if port 11434 is available")
        print("   3. Restart Ollama service")
        return False, "Cannot connect to Ollama"
    
    print("✅ Ollama is connected and ready!")
    return True, "Ollama connected"

def check_ollama_model():
    """
    Check if required model exists
    Returns: (bool, str) - (model_exists, status_message)
    """
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode != 0:
            return False, "Cannot check models"
        
        output = result.stdout.lower()
        
        # Check for various model names
        model_names = ['qwen2.5', 'llama', 'mistral', 'codellama', 'phi']
        for model in model_names:
            if model in output:
                return True, f"Found model: {model}"
        
        return False, "No suitable model found"
        
    except Exception as e:
        return False, f"Error checking models: {str(e)}"

def setup_ollama_automatically():
    """
    Try to set up Ollama automatically for EXE users
    """
    print("\n" + "="*60)
    print("🤖 JARVIS AI - Ollama Setup Assistant")
    print("="*60)
    
    # Check connection
    connected, msg = check_ollama_connection()
    
    if not connected:
        print(f"\n⚠️ {msg}")
        print("\n📋 JARVIS will run in BASIC MODE")
        print("   You can still use all non-AI features:")
        print("   - File management")
        print("   - Screenshots")
        print("   - Automation tools")
        print("   - System control")
        print("   - And more...")
        print("\n💡 To enable AI features, install Ollama from https://ollama.ai")
        return False
    
    # Check model
    model_exists, model_msg = check_ollama_model()
    
    if not model_exists:
        print(f"\n📦 {model_msg}")
        response = input("\nDownload qwen2.5:7b model (4GB)? (y/n): ")
        
        if response.lower() == 'y':
            print("\n⏬ Downloading AI model... This may take 5-15 minutes...")
            print("   Download speed depends on your internet connection.")
            print("   Please wait...\n")
            
            try:
                process = subprocess.Popen(['ollama', 'pull', 'qwen2.5:7b'],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          text=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW,
                                          bufsize=1,
                                          universal_newlines=True)
                
                # Show progress
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        print(f"   {line}")
                
                process.wait()
                
                if process.returncode == 0:
                    print("\n✅ Model downloaded successfully!")
                    return True
                else:
                    print("\n⚠️ Model download had issues")
                    print("   You can manually run: ollama pull qwen2.5:7b")
                    return False
                    
            except Exception as e:
                print(f"\n❌ Download failed: {e}")
                print("   You can manually run: ollama pull qwen2.5:7b")
                return False
        else:
            print("\n⚠️ Running without AI model")
            print("   You can download later with: ollama pull qwen2.5:7b")
            return False
    
    print(f"\n✅ {model_msg}")
    return True

# ============================================================================
# BASIC COMMAND HANDLER (for when AI is not available)
# ============================================================================

def handle_basic_command(command: str) -> str:
    """Handle basic commands when AI is not available"""
    command_lower = command.lower()
    
    # Simple command matching
    if any(word in command_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm running in basic mode. Install Ollama from https://ollama.ai for full AI features."
    
    elif 'screenshot' in command_lower:
        return "I can take screenshots! Use the tools menu or say 'take screenshot' specifically."
    
    elif 'time' in command_lower:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    
    elif any(word in command_lower for word in ['open', 'launch']):
        # Extract app name
        words = command_lower.split()
        for i, word in enumerate(words):
            if word in ['open', 'launch'] and i + 1 < len(words):
                app_name = words[i + 1]
                return f"To open {app_name}, please use the tools menu or say 'open {app_name}' clearly."
    
    elif 'help' in command_lower or 'what can you do' in command_lower:
        return """I can help with:
• File management (search, organize, copy, delete files)
• Screenshots (full screen, windows, annotated)
• System control (open apps, run commands, check resources)
• Automation (type text, control mouse, keyboard shortcuts)
• And much more!

Right-click the orb and select 'Show Tools' to see all options.
Install Ollama for AI features: https://ollama.ai"""
    
    elif 'note' in command_lower or 'notepad' in command_lower:
        return "I can create notes! Use the tools menu or say 'open notepad' specifically."
    
    elif 'volume' in command_lower:
        return "I can control volume! Use the tools menu or say 'set volume to 50'."
    
    elif 'type' in command_lower:
        return "I can type text! Use the tools menu or say 'type Hello World'."
    
    elif 'click' in command_lower and 'mouse' in command_lower:
        return "I can control the mouse! Use the tools menu for precise control."
    
    return "I'm in basic mode. For AI conversation, please install Ollama from https://ollama.ai"

def create_dummy_tool(tool_name):
    """Create a dummy tool that explains it's not available"""
    @langchain_tool
    def dummy_func(*args, **kwargs) -> str:
        return f"⚠️ **{tool_name} not available**\nPlease check if the tool is properly installed in the tools directory."
    dummy_func.__name__ = tool_name
    dummy_func.name = tool_name
    return dummy_func

# Load all tools with error handling
print("🔧 Loading tools...")

# Basic tools
try:
    from tools.time_tool import get_time
    print("✅ time_tool loaded")
except ImportError as e:
    print(f"⚠️ time_tool: {e}")
    get_time = create_dummy_tool("get_time")

try:
    from tools.OCR import read_text_from_latest_image, read_text_from_image_file, ocr_to_file, read_screen_area
    print("✅ OCR tools loaded")
except ImportError as e:
    print(f"⚠️ OCR: {e}")
    read_text_from_latest_image = create_dummy_tool("read_text_from_latest_image")
    read_text_from_image_file = create_dummy_tool("read_text_from_image_file")
    ocr_to_file = create_dummy_tool("ocr_to_file")
    read_screen_area = create_dummy_tool("read_screen_area")

try:
    from tools.arp_scan import arp_scan_terminal
    print("✅ arp_scan loaded")
except ImportError as e:
    print(f"⚠️ arp_scan: {e}")
    arp_scan_terminal = create_dummy_tool("arp_scan_terminal")

try:
    from tools.duckduckgo import duckduckgo_search_tool
    print("✅ duckduckgo loaded")
except ImportError as e:
    print(f"⚠️ duckduckgo: {e}")
    duckduckgo_search_tool = create_dummy_tool("duckduckgo_search_tool")

try:
    from tools.matrix import matrix_mode
    print("✅ matrix loaded")
except ImportError as e:
    print(f"⚠️ matrix: {e}")
    matrix_mode = create_dummy_tool("matrix_mode")

try:
    from tools.screenshot import take_screenshot, screenshot_all_monitors, annotate_screenshot, screenshot_window
    print("✅ screenshot tools loaded")
except ImportError as e:
    print(f"⚠️ screenshot: {e}")
    take_screenshot = create_dummy_tool("take_screenshot")
    screenshot_all_monitors = create_dummy_tool("screenshot_all_monitors")
    annotate_screenshot = create_dummy_tool("annotate_screenshot")
    screenshot_window = create_dummy_tool("screenshot_window")

# PC Control tools
try:
    from tools.pc_control import (
        open_notepad_with_context, list_notes, quick_note,
        list_running_apps, execute_command,
        system_info, create_file_smart, test_note_creation
    )
    # Import new app launcher tools
    from tools.app_launcher import open_app, close_app, rescan_apps, list_installed_apps
    print("✅ pc_control tools loaded")
except ImportError as e:
    print(f"⚠️ pc_control: {e}")
    open_notepad_with_context = create_dummy_tool("open_notepad_with_context")
    list_notes = create_dummy_tool("list_notes")
    quick_note = create_dummy_tool("quick_note")
    open_app = create_dummy_tool("open_app")
    close_app = create_dummy_tool("close_app")
    list_running_apps = create_dummy_tool("list_running_apps")
    execute_command = create_dummy_tool("execute_command")
    system_info = create_dummy_tool("system_info")
    create_file_smart = create_dummy_tool("create_file_smart")
    test_note_creation = create_dummy_tool("test_note_creation")
    rescan_apps = create_dummy_tool("rescan_apps")
    list_installed_apps = create_dummy_tool("list_installed_apps")

# Automation tools
try:
    from tools.automation_tools import (
        type_text, press_key, copy_to_clipboard, paste_from_clipboard,
        click_mouse, move_mouse, get_mouse_position, scroll_screen,
        minimize_all_windows, switch_window, lock_computer, get_screen_size
    )
    print("✅ automation_tools loaded")
except ImportError as e:
    print(f"⚠️ automation_tools: {e}")
    type_text = create_dummy_tool("type_text")
    press_key = create_dummy_tool("press_key")
    copy_to_clipboard = create_dummy_tool("copy_to_clipboard")
    paste_from_clipboard = create_dummy_tool("paste_from_clipboard")
    click_mouse = create_dummy_tool("click_mouse")
    move_mouse = create_dummy_tool("move_mouse")
    get_mouse_position = create_dummy_tool("get_mouse_position")
    scroll_screen = create_dummy_tool("scroll_screen")
    minimize_all_windows = create_dummy_tool("minimize_all_windows")
    switch_window = create_dummy_tool("switch_window")
    lock_computer = create_dummy_tool("lock_computer")
    get_screen_size = create_dummy_tool("get_screen_size")

# File management tools
try:
    from tools.file_tools import (
        search_files, organize_files, create_zip, extract_zip,
        delete_file, rename_file, copy_file, get_file_info
    )
    print("✅ file_tools loaded")
except ImportError as e:
    print(f"⚠️ file_tools: {e}")
    search_files = create_dummy_tool("search_files")
    organize_files = create_dummy_tool("organize_files")
    create_zip = create_dummy_tool("create_zip")
    extract_zip = create_dummy_tool("extract_zip")
    delete_file = create_dummy_tool("delete_file")
    rename_file = create_dummy_tool("rename_file")
    copy_file = create_dummy_tool("copy_file")
    get_file_info = create_dummy_tool("get_file_info")

# Network and system monitoring tools
try:
    from tools.network_tools import (
        get_network_info, network_speed_test, list_connections,
        monitor_system_resources, list_processes, kill_process, get_battery_status
    )
    print("✅ network_tools loaded")
except ImportError as e:
    print(f"⚠️ network_tools: {e}")
    get_network_info = create_dummy_tool("get_network_info")
    network_speed_test = create_dummy_tool("network_speed_test")
    list_connections = create_dummy_tool("list_connections")
    monitor_system_resources = create_dummy_tool("monitor_system_resources")
    list_processes = create_dummy_tool("list_processes")
    kill_process = create_dummy_tool("kill_process")
    get_battery_status = create_dummy_tool("get_battery_status")

# Media tools
try:
    from tools.media_tools import (
        control_volume, play_sound, open_url, take_picture,
        record_audio, text_to_speech_file, get_clipboard_history
    )
    print("✅ media_tools loaded")
except ImportError as e:
    print(f"⚠️ media_tools: {e}")
    control_volume = create_dummy_tool("control_volume")
    play_sound = create_dummy_tool("play_sound")
    open_url = create_dummy_tool("open_url")
    take_picture = create_dummy_tool("take_picture")
    record_audio = create_dummy_tool("record_audio")
    text_to_speech_file = create_dummy_tool("text_to_speech_file")
    get_clipboard_history = create_dummy_tool("get_clipboard_history")

load_dotenv()

# --- Global Config ---
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30
MEMORY_FILE = "jarvis_memory.json"
CHAT_HISTORY_FILE = "chat_sessions.json"
SETTINGS_FILE = "jarvis_settings.json"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Speech control flags
speech_active = True
speech_paused = False

# Default settings
DEFAULT_SETTINGS = {
    "voice_rate": 180,
    "voice_volume": 0.9,
    "voice_id": 0,  # Default voice
    "microphone_index": None,  # None = default
    "speaker_index": None,  # None = default
    "orb_color": [0, 150, 255],  # RGB
    "glow_color": [100, 200, 255],  # RGB
    "ai_model": "qwen2.5:7b",
    "conversation_timeout": 30
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                logging.info("⚙️ Settings loaded")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logging.info("💾 Settings saved")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

# Initialize settings manager
settings_manager = SettingsManager()

print(f"\n{'='*60}")
print(f"🚀 JARVIS AI - ADVANCED HYPERREALISTIC ASSISTANT")
print(f"{'='*60}\n")

# ============================================================================
# ADVANCED MEMORY SYSTEM
# ============================================================================

@dataclass
class ConversationMemory:
    session_id: str
    timestamp: str
    title: str
    messages: List[Dict[str, str]]
    summary: str = ""
    tags: List[str] = None
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "title": self.title,
            "messages": self.messages,
            "summary": self.summary,
            "tags": self.tags or []
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            session_id=data["session_id"],
            timestamp=data["timestamp"],
            title=data["title"],
            messages=data["messages"],
            summary=data.get("summary", ""),
            tags=data.get("tags", [])
        )

class AdvancedMemoryManager:
    def __init__(self):
        self.conversations: Dict[str, ConversationMemory] = {}
        self.current_session: Optional[ConversationMemory] = None
        self.load_all_conversations()
    
    def create_session(self, initial_message: str = "") -> str:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        title = initial_message[:50] + "..." if len(initial_message) > 50 else initial_message or "New Chat"
        
        self.current_session = ConversationMemory(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            title=title,
            messages=[]
        )
        
        if initial_message:
            self.add_message("user", initial_message)
        
        self.save_conversation(self.current_session)
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        if session_id in self.conversations:
            self.current_session = self.conversations[session_id]
            return True
        return False
    
    def add_message(self, role: str, content: str):
        if self.current_session:
            self.current_session.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            if self.current_session.title == "New Chat" and role == "user" and len(content) > 10:
                self.current_session.title = content[:30] + "..."
            
            self.save_conversation(self.current_session)
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        if not self.current_session:
            return []
        return self.current_session.messages[-limit:]
    
    def save_conversation(self, conversation: ConversationMemory):
        self.conversations[conversation.session_id] = conversation
        self.save_all_conversations()
    
    def save_all_conversations(self):
        try:
            data = {
                "conversations": [conv.to_dict() for conv in self.conversations.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"💾 Saved {len(self.conversations)} conversations")
        except Exception as e:
            logging.error(f"Failed to save conversations: {e}")
    
    def load_all_conversations(self):
        try:
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.conversations = {}
                for conv_data in data.get("conversations", []):
                    conv = ConversationMemory.from_dict(conv_data)
                    self.conversations[conv.session_id] = conv
                
                logging.info(f"📂 Loaded {len(self.conversations)} conversation(s)")
            else:
                logging.info("No existing conversations found")
        except Exception as e:
            logging.error(f"Failed to load conversations: {e}")
            self.conversations = {}
    
    def delete_session(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            self.save_all_conversations()
            return True
        return False
    
    def get_session_list(self) -> List[Dict]:
        sessions = []
        for conv in self.conversations.values():
            sessions.append({
                "id": conv.session_id,
                "title": conv.title,
                "timestamp": conv.timestamp,
                "message_count": len(conv.messages),
                "summary": conv.summary
            })
        
        sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        return sessions
    
    def get_message_history(self, session_id: str):
        """Get message history for LangChain integration"""
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.messages import HumanMessage, AIMessage
        
        history = ChatMessageHistory()
        
        if session_id in self.conversations:
            conv = self.conversations[session_id]
            for msg in conv.messages:
                if msg["role"] == "user":
                    history.add_message(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    history.add_message(AIMessage(content=msg["content"]))
        
        return history

# Initialize memory manager
memory_manager = AdvancedMemoryManager()

# ============================================================================
# AI BRAIN SETUP WITH ALL TOOLS
# ============================================================================

# Global variables for model management
current_model = "qwen2.5:7b"
available_models = []
ai_mode_enabled = False  # Track if AI mode is available

def get_ollama_models():
    """Get list of installed Ollama models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    # Extract model name (first column)
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
        return []
    except Exception as e:
        logging.error(f"Failed to get Ollama models: {e}")
        return []

def initialize_llm(model_name=None):
    """Initialize or reinitialize the LLM with specified model"""
    global llm, executor, executor_with_history, current_model, ai_mode_enabled
    
    if model_name:
        current_model = model_name
    
    try:
        llm = ChatOllama(
            model=current_model,
            temperature=0,
            num_predict=512,
            top_p=0.9
        )
        
        # Recreate the agent with new LLM
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        
        # Recreate executor with history
        executor_with_history = RunnableWithMessageHistory(
            executor,
            lambda session_id: memory_manager.get_message_history(session_id),
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        
        ai_mode_enabled = True
        logging.info(f"🤖 LLM initialized with model: {current_model}")
        return llm
    except Exception as e:
        logging.error(f"Failed to initialize LLM: {e}")
        ai_mode_enabled = False
        return None

# Check Ollama on startup
ai_mode_enabled = setup_ollama_automatically()

# Get available models on startup
if ai_mode_enabled:
    available_models = get_ollama_models()
    if available_models:
        logging.info(f"📦 Found {len(available_models)} Ollama models: {', '.join(available_models)}")
    else:
        logging.warning("⚠️ No Ollama models found")

# Initialize LLM only if AI mode is enabled
llm = None
agent_executor = None
executor_with_history = None

if ai_mode_enabled:
    try:
        llm = ChatOllama(
            model=current_model,
            temperature=0,
            num_predict=512,
            top_p=0.9
        )
        print(f"✅ AI Model: {current_model} - Ready!")
    except Exception as e:
        print(f"⚠️ AI Model error: {e}")
        print("⚠️ Running in basic mode (AI features disabled)")
        ai_mode_enabled = False

# Complete tool list with ALL advanced capabilities
tools = [
    # Core PC Control
    open_notepad_with_context, quick_note, list_notes, test_note_creation,
    open_app, close_app, rescan_apps, list_installed_apps,
    list_running_apps, execute_command, system_info, create_file_smart,
    
    # Screenshot & OCR
    take_screenshot, screenshot_all_monitors, annotate_screenshot, screenshot_window,
    read_text_from_latest_image, read_text_from_image_file, ocr_to_file, read_screen_area,
    
    # Automation
    type_text, press_key, copy_to_clipboard, paste_from_clipboard,
    click_mouse, move_mouse, get_mouse_position, scroll_screen,
    minimize_all_windows, switch_window, lock_computer, get_screen_size,
    
    # File Management
    search_files, organize_files, create_zip, extract_zip,
    delete_file, rename_file, copy_file, get_file_info,
    
    # Network & System
    get_network_info, network_speed_test, list_connections,
    monitor_system_resources, list_processes, kill_process, get_battery_status,
    
    # Media & Audio
    control_volume, play_sound, open_url, take_picture,
    record_audio, text_to_speech_file, get_clipboard_history,
    
    # Misc
    get_time, arp_scan_terminal, duckduckgo_search_tool, matrix_mode
]

prompt = ChatPromptTemplate.from_messages([
    ("system", """YOU ARE JARVIS - AN ADVANCED HYPERREALISTIC AI ASSISTANT

**YOUR CAPABILITIES:**
You have access to 60+ powerful tools for complete system control:

📁 **File Management**: Search, organize, zip, copy, rename, delete files
🖥️ **System Control**: Open/close ANY app (auto-scans PC), run commands, monitor resources
⌨️ **Automation**: Type text, click mouse, keyboard shortcuts, window management
📸 **Screenshots & OCR**: Capture screens, read text from images
🌐 **Network**: Check connections, speed tests, network info, kill processes
🔊 **Media**: Control volume, record audio, play sounds, open URLs
🔐 **Security**: Lock computer, manage processes, system monitoring
📊 **Information**: Battery status, system info, time zones, web search

**IMPORTANT - APP CONTROL:**
- You can open/close ANY application installed on the PC
- The system automatically scans Windows for all installed apps
- Use 'open_app' for opening and 'close_app' for closing
- If an app can't be found, suggest using 'rescan_apps'
- Apps like Discord, Steam, Spotify, etc. are all supported

**CONVERSATION STYLE:**
- Be natural, friendly, and efficient like a personal butler
- Use "sir" occasionally but not excessively
- Respond conversationally for simple queries
- Use appropriate tools when user requests specific actions
- Keep responses concise but informative
- When using tools, don't read out all the formatted output - summarize briefly

**EXAMPLES:**
User: "hello" → "Hello sir! How may I assist you today?"
User: "what can you do?" → List your key capabilities briefly
User: "open chrome" → USE open_app tool
User: "open discord" → USE open_app tool  
User: "close spotify" → USE close_app tool
User: "type hello world" → USE type_text tool
User: "take screenshot" → USE take_screenshot tool
User: "find all python files" → USE search_files tool

Be smart, capable, and ACTUALLY HELPFUL!

Current chat: {recent_history}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Initialize agent only if AI mode is enabled
if ai_mode_enabled and llm:
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        max_iterations=3,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )
else:
    agent_executor = None
    print("⚠️ AI Mode: Disabled - Running in Basic Mode")

# LangChain memory
memory_store = {}

def get_session_history(session_id: str):
    if session_id not in memory_store:
        memory_store[session_id] = ChatMessageHistory()
        
        if memory_manager.current_session:
            for msg in memory_manager.current_session.messages:
                if msg["role"] == "user":
                    memory_store[session_id].add_user_message(msg["content"])
                else:
                    memory_store[session_id].add_ai_message(msg["content"])
    
    return memory_store[session_id]

# Initialize executor with history only if AI mode is enabled
if ai_mode_enabled and agent_executor:
    executor_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
else:
    executor_with_history = None

# ============================================================================
# ENHANCED RESPONSE HANDLER
# ============================================================================

def process_jarvis_command(user_input: str, orb) -> str:
    """Process command through AI with context"""
    try:
        # If AI mode is disabled, use basic command handler
        if not ai_mode_enabled or executor_with_history is None:
            return handle_basic_command(user_input)
        
        if not memory_manager.current_session:
            memory_manager.create_session(user_input)
        
        session_id = memory_manager.current_session.session_id
        recent_messages = memory_manager.get_recent_messages(5)
        recent_history = "\n".join([f"{m['role']}: {m['content']}" for m in recent_messages[-3:]])
        
        result = executor_with_history.invoke(
            {
                "input": user_input,
                "recent_history": recent_history
            },
            config={"configurable": {"session_id": session_id}}
        )
        
        output = result.get("output", "I'm not sure how to help with that, sir.")
        return output
    
    except Exception as e:
        logging.error(f"Command processing error: {e}")
        return f"I encountered an issue, sir: {str(e)}"

# ============================================================================
# COMPACT RED & BLACK TERMINAL CHAT UI
# ============================================================================

class ChatUI(QWidget):
    """Compact red & black terminal-style chat interface"""
    message_sent = pyqtSignal(str)
    add_message_signal = pyqtSignal(str, str, bool)
    
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.setup_ui()
        self.add_message_signal.connect(self.add_message_safe)
        
    def setup_ui(self):
        self.setWindowTitle("🔥 JARVIS TERMINAL")
        self.setGeometry(400, 200, 900, 600)  # Smaller size
        
        # COMPACT RED & BLACK THEME
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            QTextEdit {
                background-color: #000000;
                border: 1px solid #ff0000;
                border-radius: 5px;
                padding: 10px;
                color: #ff4444;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                selection-background-color: #ff0000;
            }
            QPushButton {
                background-color: #2a0a0a;
                color: #ff4444;
                border: 1px solid #ff0000;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                margin: 2px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: #000000;
            }
            QLineEdit {
                background-color: #111111;
                border: 1px solid #ff0000;
                border-radius: 15px;
                padding: 8px 15px;
                color: #ff4444;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }
            QLabel {
                color: #ff4444;
                font-size: 10px;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #1a1a1a;
            }
            QScrollBar::handle:vertical {
                background: #ff0000;
                border-radius: 3px;
            }
        """)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # ===== CHAT AREA =====
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setSpacing(6)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact header
        header = QLabel("JARVIS TERMINAL")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ff0000;
                padding: 8px;
                background-color: #1a0a0a;
                border-radius: 5px;
                border: 1px solid #ff0000;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chat_layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setHtml(self.get_terminal_welcome())
        chat_layout.addWidget(self.chat_area, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("└─❯ Enter command...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input, 1)
        
        send_btn = QPushButton("🚀")
        send_btn.setToolTip("Send message")
        send_btn.setFixedWidth(50)
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #000000;
                font-weight: bold;
            }
        """)
        input_layout.addWidget(send_btn)
        
        voice_btn = QPushButton("🎤")
        voice_btn.setToolTip("Voice input (Alt+V)")
        voice_btn.setFixedWidth(50)
        voice_btn.clicked.connect(self.start_voice_input)
        voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                color: #000000;
                font-weight: bold;
            }
        """)
        input_layout.addWidget(voice_btn)
        
        chat_layout.addLayout(input_layout)
        
        # ===== SIDE PANEL =====
        side_container = QWidget()
        side_container.setFixedWidth(180)  # Even narrower
        side_layout = QVBoxLayout(side_container)
        side_layout.setSpacing(6)
        side_layout.setContentsMargins(0, 0, 0, 0)
        
        # Quick Actions
        actions_label = QLabel("⚡ QUICK ACTIONS")
        actions_label.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(actions_label)
        
        # Compact action buttons
        quick_actions = [
            ("📁 Files", "search for files"),
            ("🖥️ System", "show system info"),
            ("📸 Screenshot", "take screenshot"),
            ("🌐 Web", "search web"),
            ("📊 Stats", "show resources"),
            ("🔍 Find", "find processes"),
            ("🎵 Volume", "control volume"),
            ("📝 Note", "create quick note"),
        ]
        
        for text, cmd in quick_actions:
            btn = QPushButton(text)
            btn.setToolTip(cmd)
            btn.clicked.connect(lambda checked, c=cmd: self.send_quick_command(c))
            side_layout.addWidget(btn)
        
        side_layout.addSpacing(10)
        
        # Tools
        tools_label = QLabel("🛠️ TOOLS")
        tools_label.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(tools_label)
        
        tools = [
            ("🖱️ Mouse", self.control_mouse),
            ("⌨️ Type", self.control_keyboard),
            ("🔒 Lock", self.lock_computer),
            ("📱 App", self.open_application),
        ]
        
        for text, func in tools:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            side_layout.addWidget(btn)
        
        side_layout.addSpacing(10)
        
        # Chat Controls
        chat_label = QLabel("💬 CHAT")
        chat_label.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(chat_label)
        
        chat_controls = QHBoxLayout()
        chat_controls.setSpacing(4)
        
        clear_btn = QPushButton("🗑️")
        clear_btn.setToolTip("Clear chat (Alt+C)")
        clear_btn.setFixedWidth(40)
        clear_btn.clicked.connect(self.clear_chat)
        chat_controls.addWidget(clear_btn)
        
        export_btn = QPushButton("💾")
        export_btn.setToolTip("Export log (Alt+E)")
        export_btn.setFixedWidth(40)
        export_btn.clicked.connect(self.export_chat)
        chat_controls.addWidget(export_btn)
        
        copy_btn = QPushButton("📋")
        copy_btn.setToolTip("Copy chat")
        copy_btn.setFixedWidth(40)
        copy_btn.clicked.connect(self.copy_chat)
        chat_controls.addWidget(copy_btn)
        
        reload_btn = QPushButton("🔄")
        reload_btn.setToolTip("Reload history")
        reload_btn.setFixedWidth(40)
        reload_btn.clicked.connect(self.load_chat_history)
        chat_controls.addWidget(reload_btn)
        
        side_layout.addLayout(chat_controls)
        
        side_layout.addStretch()
        
        # Status
        status = QLabel("🟢 Online")
        status.setStyleSheet("color: #00ff00; font-size: 9px; background: #1a1a1a; padding: 4px; border-radius: 3px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(status)
        
        # Close button
        close_btn = QPushButton("⛔ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #990000;
                color: white;
                font-size: 11px;
                padding: 6px;
            }
        """)
        side_layout.addWidget(close_btn)
        
        # Add to main layout
        main_layout.addWidget(chat_container, 3)  # 75% width
        main_layout.addWidget(side_container, 1)  # 25% width
        
        self.setLayout(main_layout)
        self.load_chat_history()
    
    def get_terminal_welcome(self):
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M")
        return f"""
        <div style='color: #ff0000; font-family: Consolas; padding: 8px; font-size: 11px;'>
            <span style='color: #00ff00;'>┌─[JARVIS]─[{time_str}]</span><br>
            <span style='color: #00ff00;'>├─❯</span> <span style='color: #ffffff;'>Terminal ready</span><br>
            <span style='color: #00ff00;'>└─❯</span> <span style='color: #ffff00;'>Type or use side panel</span><br><br>
            <div style='color: #888888; font-size: 10px;'>
                [Alt+V] Voice | [Alt+C] Clear | [Alt+E] Export | [Esc] Close
            </div>
            <hr style='border: none; border-top: 1px solid #222; margin: 10px 0;'>
        </div>
        """
    
    def add_message_safe(self, sender: str, message: str, is_user: bool = True):
        self.add_message(sender, message, is_user)
    
    def add_message(self, sender: str, message: str, is_user: bool = True):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        if is_user:
            color = "#00ff00"
            sender_name = "USER"
            prefix = "└─❯"
        else:
            color = "#ff0000"
            sender_name = "JARVIS"
            prefix = "[AI]─❯"
        
        msg_html = message.replace('\n', '<br>')
        message_html = (
            f"<div style='font-family: Consolas; margin: 6px 0; font-size: 11px;'>"
            f"<span style='color: #666;'>[{timestamp}]</span> "
            f"<span style='color: {color}; font-weight: bold;'>[{sender_name}]</span><br>"
            f"<span style='color: {color};'>{prefix}</span> "
            f"<span style='color: #ffffff;'>{msg_html}</span>"
            f"</div>"
            f"<hr style='border: none; border-top: 1px dashed #222; margin: 6px 0;'>"
        )
        
        self.chat_area.setHtml(self.chat_area.toHtml() + message_html)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
    
    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.add_message("USER", message, is_user=True)
            self.message_sent.emit(message)
            self.message_input.clear()
    
    def send_quick_command(self, command: str):
        self.add_message("SYSTEM", f"Exec: {command}", is_user=False)
        self.message_input.setText(command)
        self.send_message()
    
    def receive_message(self, message: str):
        self.add_message("JARVIS", message, is_user=False)
    
    def clear_chat(self):
        reply = QMessageBox.question(self, 'Clear', 'Clear chat?', 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_area.setHtml(self.get_terminal_welcome())
            self.add_message("SYSTEM", "Chat cleared", is_user=False)
    
    def export_chat(self):
        from datetime import datetime
        filename = f"jarvis_log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"JARVIS Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("="*40 + "\n\n")
                f.write(self.chat_area.toPlainText())
            
            self.add_message("SYSTEM", f"Exported: {filename}", is_user=False)
            QMessageBox.information(self, "Exported", f"Saved to:\n{filename}")
        except Exception as e:
            self.add_message("SYSTEM", f"Export failed: {str(e)}", is_user=False)
    
    def start_voice_input(self):
        import speech_recognition as sr
        
        try:
            self.message_input.setPlaceholderText("🎤 Listening...")
            self.message_input.setStyleSheet("""
                QLineEdit {
                    background-color: #111111;
                    border: 1px solid #00ff00;
                    color: #00ff00;
                }
            """)
            QApplication.processEvents()
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                self.message_input.setText(text)
                self.add_message("VOICE", f"Heard: {text}", is_user=False)
                self.send_message()
                
        except sr.WaitTimeoutError:
            self.message_input.setPlaceholderText("⏰ No speech")
            QTimer.singleShot(1500, lambda: self.message_input.setPlaceholderText("└─❯ Enter command..."))
        except Exception as e:
            self.add_message("SYSTEM", f"Voice error: {str(e)}", is_user=False)
        finally:
            self.message_input.setStyleSheet("""
                QLineEdit {
                    background-color: #111111;
                    border: 1px solid #ff0000;
                    color: #ff4444;
                }
            """)
            self.message_input.setPlaceholderText("└─❯ Enter command...")
    
    def load_chat_history(self):
        if self.memory_manager.current_session:
            messages = self.memory_manager.get_recent_messages(8)
            for msg in messages:
                is_user = msg["role"] == "user"
                self.add_message(msg["role"].upper(), msg["content"], is_user=is_user)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.start_voice_input()
        elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.clear_chat()
        elif event.key() == Qt.Key.Key_E and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.export_chat()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    # Tool functions
    def control_mouse(self):
        self.send_quick_command("control mouse")
    
    def control_keyboard(self):
        text, ok = QInputDialog.getText(self, "Type", "Text to type:")
        if ok and text:
            self.send_quick_command(f"type {text}")
    
    def lock_computer(self):
        self.send_quick_command("lock computer")
    
    def open_application(self):
        app, ok = QInputDialog.getText(self, "Open App", "App name:")
        if ok and app:
            self.send_quick_command(f"open {app}")
    
    def copy_chat(self):
        QApplication.clipboard().setText(self.chat_area.toPlainText())
        self.add_message("SYSTEM", "Copied to clipboard", is_user=False)
    
    # ===== Tool Functions =====
    
    def create_quick_note(self):
        """Create a quick note"""
        text, ok = QInputDialog.getText(self, "Quick Note", "Enter your note:")
        if ok and text:
            self.send_quick_command(f"Create note: {text}")
    
    def control_mouse(self):
        """Open mouse control dialog"""
        options = ["Move to center", "Left click", "Right click", "Get position"]
        choice, ok = QInputDialog.getItem(self, "Mouse Control", "Select action:", options, 0, False)
        if ok and choice:
            self.send_quick_command(f"Mouse {choice.lower()}")
    
    def control_keyboard(self):
        """Open keyboard control dialog"""
        text, ok = QInputDialog.getText(self, "Keyboard Control", "Enter text to type:")
        if ok and text:
            self.send_quick_command(f"Type {text}")
    
    def lock_computer(self):
        """Lock the computer"""
        reply = QMessageBox.question(self, "Lock Computer", 
                                    "Lock your computer now?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.send_quick_command("Lock computer")
    
    def open_application(self):
        """Open an application"""
        text, ok = QInputDialog.getText(self, "Open Application", "Enter application name:")
        if ok and text:
            self.send_quick_command(f"Open {text}")
    
    def close_application(self):
        """Close an application"""
        text, ok = QInputDialog.getText(self, "Close Application", "Enter application name:")
        if ok and text:
            self.send_quick_command(f"Close {text}")
    
    def test_voice(self):
        """Test TTS voice"""
        self.send_quick_command("Test voice output")
    
    def play_sound(self):
        """Play a test sound"""
        self.send_quick_command("Play test sound")
    
    def record_audio(self):
        """Record audio"""
        duration, ok = QInputDialog.getInt(self, "Record Audio", "Duration (seconds):", 5, 1, 60, 1)
        if ok:
            self.send_quick_command(f"Record audio for {duration} seconds")
    
    def copy_chat(self):
        """Copy chat to clipboard"""
        chat_text = self.chat_area.toPlainText()
        QApplication.clipboard().setText(chat_text)
        self.add_message("SYSTEM", "Chat copied to clipboard", is_user=False)
# ============================================================================
# HYPERREALISTIC ORB UI WITH TASKBAR ICON
# ============================================================================

class JarvisOrb(QWidget):
    # Add a signal for thread-safe chat updates
    update_chat_signal = pyqtSignal(str, str)
    
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.status_text = "🚀 Initializing..."
        self.chat_window = None
        
        # Connect the signal
        self.update_chat_signal.connect(self.add_conversation_to_chat)
        
        # Set window icon for taskbar
        try:
            self.setWindowIcon(QIcon("icon.ico"))
        except:
            # Create a simple icon if file doesn't exist
            self.setWindowIcon(self.create_default_icon())
        
        # Orb properties
        self.pulse_phase = 0
        self.rotation = 0
        self.pulse_speed = 0.05
        self.base_radius = 60
        self.current_radius = self.base_radius
        
        # Colors - load from settings
        saved_core = settings_manager.get('orb_color', [0, 150, 255])
        saved_glow = settings_manager.get('glow_color', [100, 200, 255])
        self.core_color = QColor(saved_core[0], saved_core[1], saved_core[2])
        self.glow_color = QColor(saved_glow[0], saved_glow[1], saved_glow[2])
        
        # Setup UI
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle("JARVIS AI")
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        
        # Make draggable
        self.dragging = False
        self.drag_started = False
        self.offset = QPoint()
    
    def create_default_icon(self):
        """Create a default icon if icon.ico doesn't exist"""
        from PyQt6.QtGui import QPixmap, QPainter
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 150, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return QIcon(pixmap)
    
    def add_conversation_to_chat(self, user_message: str, ai_response: str):
        """Thread-safe method to add conversation to chat"""
        # Add to memory manager
        if memory_manager.current_session:
            memory_manager.add_message("user", user_message)
            memory_manager.add_message("assistant", ai_response)
        
        # Add to chat UI if open (using thread-safe signal)
        if self.chat_window and self.chat_window.isVisible():
            self.chat_window.add_message_signal.emit("You", user_message, True)
            self.chat_window.add_message_signal.emit("JARVIS", ai_response, False)
        
        # Log the conversation
        logging.info(f"💬 Conversation: User: {user_message[:50]}... -> AI: {ai_response[:50]}...")
    
    def update_animation(self):
        self.pulse_phase += self.pulse_speed
        self.rotation += 2
        self.current_radius = self.base_radius + math.sin(self.pulse_phase) * 10
        self.update()
    
    def set_status(self, status: str):
        self.status_text = status
        
        # Change colors based on status
        if "error" in status.lower() or "❌" in status:
            self.core_color = QColor(255, 50, 50)
            self.glow_color = QColor(255, 100, 100)
        elif "listening" in status.lower() or "👂" in status:
            self.core_color = QColor(50, 255, 150)
            self.glow_color = QColor(100, 255, 200)
        elif "processing" in status.lower() or "🔍" in status:
            self.core_color = QColor(255, 200, 50)
            self.glow_color = QColor(255, 220, 100)
        elif "basic" in status.lower():
            self.core_color = QColor(150, 150, 150)
            self.glow_color = QColor(200, 200, 200)
        else:
            self.core_color = QColor(0, 150, 255)
            self.glow_color = QColor(100, 200, 255)
        
        self.update()
    
    def stop_speaking(self):
        """Stop current speech output"""
        stop_speech()
        self.set_status("🔇 Speech Stopped")
        QTimer.singleShot(1000, lambda: self.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode"))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2 - 20
        
        # Animated pulse effect
        pulse_offset = math.sin(self.pulse_phase) * 10
        
        # Multiple layered outer glow rings for depth
        for i in range(8):
            glow_radius = self.current_radius + pulse_offset + (i * 12)
            alpha = max(0, 80 - (i * 10))
            gradient = QRadialGradient(center_x, center_y, glow_radius)
            gradient.setColorAt(0, QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), alpha))
            gradient.setColorAt(0.7, QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), alpha // 3))
            gradient.setColorAt(1, QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)
        
        # Main orb with 3D effect
        gradient = QRadialGradient(center_x - 15, center_y - 15, self.current_radius * 1.5)
        gradient.setColorAt(0, QColor(255, 255, 255, 250))  # Bright highlight
        gradient.setColorAt(0.3, self.core_color)
        gradient.setColorAt(0.7, QColor(self.core_color.red()//2, self.core_color.green()//2, self.core_color.blue()//2))
        gradient.setColorAt(1, QColor(self.core_color.red()//3, self.core_color.green()//3, self.core_color.blue()//3))
        painter.setBrush(QBrush(gradient))
        
        # Glowing edge
        painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
        painter.drawEllipse(QPointF(center_x, center_y), self.current_radius, self.current_radius)
        
        # Inner glow ring
        inner_ring_radius = self.current_radius - 10
        inner_gradient = QRadialGradient(center_x, center_y, inner_ring_radius)
        inner_gradient.setColorAt(0, QColor(255, 255, 255, 0))
        inner_gradient.setColorAt(0.8, QColor(255, 255, 255, 0))
        inner_gradient.setColorAt(1, QColor(255, 255, 255, 100))
        painter.setBrush(QBrush(inner_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), inner_ring_radius, inner_ring_radius)
        
        # Rotating arc effect
        arc_path = QPainterPath()
        arc_rect = QRectF(center_x - self.current_radius - 5, center_y - self.current_radius - 5,
                         (self.current_radius + 5) * 2, (self.current_radius + 5) * 2)
        arc_path.arcMoveTo(arc_rect, self.rotation)
        arc_path.arcTo(arc_rect, self.rotation, 120)
        
        painter.setPen(QPen(QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), 200), 4))
        painter.drawPath(arc_path)
        
        # Status text with shadow
        painter.setPen(QColor(0, 0, 0, 150))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        text_rect_shadow = QRectF(1, center_y + self.current_radius + 21, self.width(), 40)
        painter.drawText(text_rect_shadow, Qt.AlignmentFlag.AlignCenter, self.status_text)
        
        painter.setPen(QColor(255, 255, 255))
        text_rect = QRectF(0, center_y + self.current_radius + 20, self.width(), 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.status_text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_started = False
            self.offset = event.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_menu(event.globalPosition().toPoint())
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.drag_started = True
            self.move(self.pos() + event.pos() - self.offset)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Only stop speech if we didn't drag
            if not self.drag_started:
                self.stop_speaking()
            self.dragging = False
            self.drag_started = False
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.show_chat_ui()
        elif event.key() == Qt.Key.Key_Escape:
            if self.chat_window and self.chat_window.isVisible():
                self.chat_window.close()
        else:
            super().keyPressEvent(event)
    
    def show_menu(self, pos):
        menu = QMenu()
        
        # Add chat UI option
        menu.addAction("💬 Open Chat UI", self.show_chat_ui)
        
        # Show AI status in menu
        if ai_mode_enabled:
            menu.addAction(f"🤖 AI Mode: Enabled ({current_model})")
        else:
            ai_action = menu.addAction("⚠️ AI Mode: Disabled")
            ai_action.setEnabled(False)
            menu.addAction("📥 Install Ollama", lambda: webbrowser.open('https://ollama.ai'))
        
        menu.addSeparator()
        menu.addAction("⚙️ Settings", lambda: self.show_settings_dialog())
        menu.addAction("📊 System Info", lambda: self.show_info())
        
        if ai_mode_enabled:
            menu.addAction("🤖 Change AI Model", lambda: self.show_model_selector())
        
        menu.addAction("💾 Memory Manager", lambda: self.show_memory_dialog())
        menu.addAction("🎨 Change Color", lambda: self.change_color())
        menu.addAction("📋 Show Tools", lambda: self.show_tools())
        menu.addSeparator()
        menu.addAction("❌ Exit", self.close)
        menu.exec(pos)
    
    def show_chat_ui(self):
        """Show interactive chat window"""
        if not self.chat_window:
            self.chat_window = ChatUI(self.memory_manager)
            self.chat_window.message_sent.connect(self.handle_chat_message)
        
        # Connect chat window to JARVIS responses
        if not hasattr(self, 'chat_connected'):
            self.chat_window.receive_message("Hello! I'm ready to chat. How can I help you?")
            self.chat_connected = True
        
        self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()
    
    def handle_chat_message(self, message: str):
        """Handle message from chat UI"""
        # Process through JARVIS
        response = process_jarvis_command(message, self)
        
        # Add to chat and speak (using thread-safe method)
        self.add_conversation_to_chat(message, response)
        
        # Speak the response
        speak_text(response, self)
    
    def show_info(self):
        import platform
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        info = f"""🖥️ JARVIS SYSTEM STATUS
        
{'='*40}
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
AI Mode: {'✅ Enabled' if ai_mode_enabled else '⚠️ Disabled'}
Model: {current_model if ai_mode_enabled else 'Not available'}
CPU Usage: {cpu}%
Memory: {mem}%
Sessions: {len(self.memory_manager.conversations)}
Tools Loaded: {len(tools)}
{'='*40}"""
        
        QMessageBox.information(self, "System Info", info)
    
    def show_model_selector(self):
        """Show dialog to select Ollama model"""
        global available_models, current_model
        
        if not ai_mode_enabled:
            QMessageBox.warning(self, "AI Disabled", 
                              "AI mode is disabled. Please install Ollama first.")
            return
        
        # Refresh models list
        self.set_status("🔄 Scanning models...")
        available_models = get_ollama_models()
        
        if not available_models:
            QMessageBox.warning(self, "No Models Found", 
                              "No Ollama models found!\n\n"
                              "Make sure Ollama is running and you have models installed.\n"
                              "Install models with: ollama pull <model_name>")
            self.set_status("⚠️ No models")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select AI Model")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Current model info
        current_label = QLabel(f"🤖 Current Model: <b>{current_model}</b>")
        current_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(current_label)
        
        # Model list
        layout.addWidget(QLabel("📦 Available Ollama Models:"))
        model_list = QListWidget()
        
        for model in available_models:
            item = QListWidgetItem(f"🔹 {model}")
            if model == current_model:
                item.setBackground(QColor(200, 255, 200))
                item.setText(f"✅ {model} (Current)")
            model_list.addItem(item)
        
        layout.addWidget(model_list)
        
        # Info label
        info_label = QLabel("💡 Tip: Larger models (70b) are smarter but slower.\n"
                           "Smaller models (7b-13b) are faster but less capable.")
        info_label.setStyleSheet("font-size: 11px; color: gray; padding: 5px;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QHBoxLayout()
        select_btn = QPushButton("✅ Select Model")
        refresh_btn = QPushButton("🔄 Refresh")
        close_btn = QPushButton("✖️ Close")
        
        def select_model():
            selected_item = model_list.currentItem()
            if selected_item:
                # Extract model name (remove emoji and markers)
                model_text = selected_item.text()
                model_name = model_text.replace('🔹 ', '').replace('✅ ', '').replace(' (Current)', '')
                
                if model_name != current_model:
                    self.set_status(f"🔄 Switching to {model_name}...")
                    try:
                        initialize_llm(model_name)
                        QMessageBox.information(self, "Success", 
                                              f"✅ Switched to model: {model_name}\n\n"
                                              "The new model will be used for all future responses.")
                        dialog.close()
                        self.set_status("✅ Model changed")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", 
                                           f"Failed to switch model:\n{str(e)}")
                        self.set_status("⚠️ Switch failed")
                else:
                    QMessageBox.information(self, "Already Selected", 
                                          f"Model {model_name} is already active.")
        
        def refresh_models():
            self.set_status("🔄 Refreshing...")
            model_list.clear()
            available_models = get_ollama_models()
            for model in available_models:
                item = QListWidgetItem(f"🔹 {model}")
                if model == current_model:
                    item.setBackground(QColor(200, 255, 200))
                    item.setText(f"✅ {model} (Current)")
                model_list.addItem(item)
            self.set_status("✅ Refreshed")
        
        select_btn.clicked.connect(select_model)
        refresh_btn.clicked.connect(refresh_models)
        close_btn.clicked.connect(dialog.close)
        
        buttons.addWidget(select_btn)
        buttons.addWidget(refresh_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
        self.set_status("✅ Ready")
    
    def show_memory_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Memory Manager")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        sessions_list = QListWidget()
        for session in self.memory_manager.get_session_list():
            item_text = f"{session['title']} - {session['message_count']} messages"
            sessions_list.addItem(item_text)
        
        layout.addWidget(QLabel("📚 Conversation Sessions:"))
        layout.addWidget(sessions_list)
        
        buttons = QHBoxLayout()
        clear_btn = QPushButton("🗑️ Clear All")
        close_btn = QPushButton("✖️ Close")
        
        clear_btn.clicked.connect(lambda: self.clear_memory(dialog))
        close_btn.clicked.connect(dialog.close)
        
        buttons.addWidget(clear_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def clear_memory(self, dialog):
        reply = QMessageBox.question(self, 'Clear Memory', 
                                     'Are you sure you want to clear all conversations?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.memory_manager.conversations.clear()
            self.memory_manager.current_session = None
            self.memory_manager.save_all_conversations()
            QMessageBox.information(self, "Success", "All conversations cleared!")
            dialog.close()
    
    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.core_color = color
            self.glow_color = QColor(
                min(color.red() + 50, 255),
                min(color.green() + 50, 255),
                min(color.blue() + 50, 255)
            )
            # Save color to settings
            settings_manager.set('orb_color', [color.red(), color.green(), color.blue()])
            settings_manager.set('glow_color', [self.glow_color.red(), self.glow_color.green(), self.glow_color.blue()])
            self.update()
    
    def show_settings_dialog(self):
        """Show comprehensive settings dialog"""
        from PyQt6.QtWidgets import QSlider, QComboBox, QSpinBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ JARVIS Settings")
        dialog.setMinimumSize(600, 700)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("⚙️ JARVIS CONFIGURATION")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # === VOICE SETTINGS ===
        voice_group = QLabel("🎤 Voice Settings")
        voice_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        scroll_layout.addWidget(voice_group)
        
        # Voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        voice_combo = QComboBox()
        
        # Get available voices
        try:
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty('voices')
            for i, voice in enumerate(voices):
                voice_combo.addItem(f"{i}: {voice.name}", i)
            voice_combo.setCurrentIndex(settings_manager.get('voice_id', 0))
            temp_engine.stop()
            del temp_engine
        except:
            voice_combo.addItem("Default Voice", 0)
        
        voice_layout.addWidget(voice_combo)
        scroll_layout.addLayout(voice_layout)
        
        # Voice rate
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Speech Rate:"))
        rate_slider = QSlider(Qt.Orientation.Horizontal)
        rate_slider.setMinimum(100)
        rate_slider.setMaximum(300)
        rate_slider.setValue(settings_manager.get('voice_rate', 180))
        rate_label = QLabel(f"{rate_slider.value()}")
        rate_slider.valueChanged.connect(lambda v: rate_label.setText(f"{v}"))
        rate_layout.addWidget(rate_slider)
        rate_layout.addWidget(rate_label)
        scroll_layout.addLayout(rate_layout)
        
        # Voice volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)
        volume_slider.setValue(int(settings_manager.get('voice_volume', 0.9) * 100))
        volume_label = QLabel(f"{volume_slider.value()}%")
        volume_slider.valueChanged.connect(lambda v: volume_label.setText(f"{v}%"))
        volume_layout.addWidget(volume_slider)
        volume_layout.addWidget(volume_label)
        scroll_layout.addLayout(volume_layout)
        
        # === AUDIO DEVICE SETTINGS ===
        audio_group = QLabel("🎧 Audio Devices")
        audio_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        scroll_layout.addWidget(audio_group)
        
        # Microphone selection
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("Microphone:"))
        mic_combo = QComboBox()
        
        try:
            # Get available microphones
            for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
                mic_combo.addItem(f"{i}: {mic_name}", i)
            current_mic = settings_manager.get('microphone_index')
            if current_mic is not None:
                mic_combo.setCurrentIndex(current_mic)
        except Exception as e:
            mic_combo.addItem("Default Microphone", None)
            logging.error(f"Failed to list microphones: {e}")
        
        mic_layout.addWidget(mic_combo)
        scroll_layout.addLayout(mic_layout)
        
        # === CONVERSATION SETTINGS ===
        conv_group = QLabel("💬 Conversation")
        conv_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        scroll_layout.addWidget(conv_group)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        timeout_spin = QSpinBox()
        timeout_spin.setMinimum(10)
        timeout_spin.setMaximum(120)
        timeout_spin.setValue(settings_manager.get('conversation_timeout', 30))
        timeout_layout.addWidget(timeout_spin)
        scroll_layout.addLayout(timeout_layout)
        
        # === APPEARANCE ===
        appear_group = QLabel("🎨 Appearance")
        appear_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        scroll_layout.addWidget(appear_group)
        
        # Color buttons
        color_layout = QHBoxLayout()
        core_color_btn = QPushButton("Change Orb Color")
        core_color_btn.clicked.connect(self.change_color)
        color_layout.addWidget(core_color_btn)
        scroll_layout.addLayout(color_layout)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        test_voice_btn = QPushButton("🔊 Test Voice")
        close_btn = QPushButton("❌ Close")
        
        def save_settings():
            settings_manager.set('voice_id', voice_combo.currentData())
            settings_manager.set('voice_rate', rate_slider.value())
            settings_manager.set('voice_volume', volume_slider.value() / 100.0)
            settings_manager.set('microphone_index', mic_combo.currentData())
            settings_manager.set('conversation_timeout', timeout_spin.value())
            
            QMessageBox.information(dialog, "✅ Success", "Settings saved successfully!\nRestart JARVIS for some changes to take effect.")
        
        def test_voice():
            # Temporarily save settings
            settings_manager.set('voice_id', voice_combo.currentData())
            settings_manager.set('voice_rate', rate_slider.value())
            settings_manager.set('voice_volume', volume_slider.value() / 100.0)
            
            # Test speech
            speak_text("Hello sir, this is a voice test. How do I sound?", self)
        
        save_btn.clicked.connect(save_settings)
        test_voice_btn.clicked.connect(test_voice)
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(test_voice_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_tools(self):
        """Show interactive tool browser with clickable tools"""
        dialog = QDialog(self)
        dialog.setWindowTitle("JARVIS Tools Browser")
        dialog.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🛠️ JARVIS TOOL CAPABILITIES")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create scrollable area
        from PyQt6.QtWidgets import QScrollArea, QGridLayout
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        
        # Define all tools by category with their actual tool names
        tool_categories = {
            "📁 FILE MANAGEMENT": [
                ("Search Files", "search_files", "Find files by pattern"),
                ("Organize Files", "organize_files", "Auto-organize by type"),
                ("Create ZIP", "create_zip", "Create archive"),
                ("Extract ZIP", "extract_zip", "Extract archive"),
                ("Delete File", "delete_file", "Remove files"),
                ("Rename File", "rename_file", "Rename files"),
                ("Copy File", "copy_file", "Copy files"),
                ("File Info", "get_file_info", "Get file details"),
            ],
            "🖥️ SYSTEM CONTROL": [
                ("Open App", "open_app", "Open any application"),
                ("Close App", "close_app", "Close application"),
                ("Rescan Apps", "rescan_apps", "Scan PC for apps"),
                ("List Apps", "list_installed_apps", "Show all apps"),
                ("Running Apps", "list_running_apps", "List processes"),
                ("Execute Command", "execute_command", "Run command"),
                ("System Info", "system_info", "System stats"),
            ],
            "⌨️ AUTOMATION": [
                ("Type Text", "type_text", "Automated typing"),
                ("Press Key", "press_key", "Keyboard shortcuts"),
                ("Click Mouse", "click_mouse", "Mouse clicks"),
                ("Move Mouse", "move_mouse", "Cursor movement"),
                ("Mouse Position", "get_mouse_position", "Get position"),
                ("Scroll Screen", "scroll_screen", "Scroll control"),
                ("Copy Clipboard", "copy_to_clipboard", "Copy text"),
                ("Paste Clipboard", "paste_from_clipboard", "Get clipboard"),
                ("Minimize Windows", "minimize_all_windows", "Show desktop"),
                ("Switch Window", "switch_window", "Alt+Tab"),
                ("Lock Computer", "lock_computer", "Lock system"),
                ("Screen Size", "get_screen_size", "Display info"),
            ],
            "📸 SCREENSHOTS & OCR": [
                ("Screenshot", "take_screenshot", "Capture screen"),
                ("All Monitors", "screenshot_all_monitors", "All screens"),
                ("Annotate Screenshot", "annotate_screenshot", "With timestamp"),
                ("Window Screenshot", "screenshot_window", "Active window"),
                ("Read Screenshot", "read_text_from_latest_image", "OCR latest"),
                ("Read Image", "read_text_from_image_file", "OCR any image"),
                ("OCR to File", "ocr_to_file", "Save OCR text"),
                ("Read Screen Area", "read_screen_area", "Region OCR"),
            ],
            "🌐 NETWORK": [
                ("Network Info", "get_network_info", "Network details"),
                ("Speed Test", "network_speed_test", "Test speed"),
                ("Connections", "list_connections", "Active connections"),
                ("System Resources", "monitor_system_resources", "CPU/RAM/Disk"),
                ("List Processes", "list_processes", "Running processes"),
                ("Kill Process", "kill_process", "Terminate process"),
                ("Battery Status", "get_battery_status", "Battery info"),
            ],
            "🔊 MEDIA & AUDIO": [
                ("Control Volume", "control_volume", "Volume control"),
                ("Play Sound", "play_sound", "System sounds"),
                ("Open URL", "open_url", "Open browser"),
                ("Take Picture", "take_picture", "Webcam capture"),
                ("Record Audio", "record_audio", "Mic recording"),
                ("Text-to-Speech File", "text_to_speech_file", "TTS file"),
                ("Clipboard History", "get_clipboard_history", "Windows clipboard"),
            ],
            "📝 NOTES": [
                ("Quick Note", "quick_note", "Fast note"),
                ("Open Notepad", "open_notepad_with_context", "Contextual note"),
                ("List Notes", "list_notes", "View all notes"),
                ("Create File", "create_file_smart", "Smart file creation"),
            ],
            "🔧 UTILITIES": [
                ("Get Time", "get_time", "World time zones"),
                ("Web Search", "duckduckgo_search_tool", "Search web"),
                ("Matrix Mode", "matrix_mode", "Matrix effect"),
                ("ARP Scan", "arp_scan_terminal", "Network scan"),
            ],
        }
        
        row = 0
        for category, tools_list in tool_categories.items():
            # Category header
            category_label = QLabel(category)
            category_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            category_label.setStyleSheet("color: #0096FF; padding: 5px;")
            grid.addWidget(category_label, row, 0, 1, 3)
            row += 1
            
            # Tools in this category
            for i, (tool_name, tool_func, tool_desc) in enumerate(tools_list):
                btn = QPushButton(f"🔹 {tool_name}")
                btn.setToolTip(tool_desc)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        color: white;
                        border: 1px solid #0096FF;
                        border-radius: 5px;
                        padding: 8px;
                        text-align: left;
                        font-size: 10pt;
                    }
                    QPushButton:hover {
                        background-color: #0096FF;
                        border: 1px solid white;
                    }
                    QPushButton:pressed {
                        background-color: #0066CC;
                    }
                """)
                
                # Connect button to execute tool
                btn.clicked.connect(lambda checked, t=tool_func, n=tool_name: self.execute_tool(t, n, dialog))
                
                # Arrange in 3 columns
                col = i % 3
                tool_row = row + (i // 3)
                grid.addWidget(btn, tool_row, col)
            
            row += ((len(tools_list) - 1) // 3) + 2
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Info label
        info_label = QLabel(f"💡 Click any tool to use it | Total: {sum(len(t) for t in tool_categories.values())} tools available")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(info_label)
        
        # Close button
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def execute_tool(self, tool_name: str, display_name: str, parent_dialog: QDialog):
        """Execute a tool when its button is clicked"""
        try:
            # Tools that need parameters - show input dialog
            tools_need_input = {
                "search_files": "Enter search pattern (e.g., *.pdf):",
                "organize_files": "Enter directory path:",
                "create_zip": "Enter source directory:",
                "extract_zip": "Enter ZIP file path:",
                "delete_file": "Enter file path to delete:",
                "rename_file": "Enter old file path:",
                "copy_file": "Enter source file path:",
                "get_file_info": "Enter file path:",
                "open_app": "Enter application name:",
                "close_app": "Enter application name:",
                "list_installed_apps": "Enter search term (or leave empty):",
                "execute_command": "Enter command to execute:",
                "type_text": "Enter text to type:",
                "press_key": "Enter key combination (e.g., ctrl+c):",
                "click_mouse": "Enter coordinates (e.g., 500,300):",
                "move_mouse": "Enter coordinates (e.g., 500,300):",
                "scroll_screen": "Enter amount to scroll:",
                "copy_to_clipboard": "Enter text to copy:",
                "read_text_from_image_file": "Enter image file path:",
                "ocr_to_file": "Enter image file path:",
                "read_screen_area": "Enter x,y,width,height:",
                "quick_note": "Enter note content:",
                "open_notepad_with_context": "Enter note context/content:",
                "control_volume": "Enter action (set/up/down/mute/unmute) and level:",
                "open_url": "Enter URL:",
                "record_audio": "Enter duration in seconds:",
                "text_to_speech_file": "Enter text to convert:",
                "get_time": "Enter city name:",
                "duckduckgo_search_tool": "Enter search query:",
                "kill_process": "Enter process name or PID:",
            }
            
            # If tool needs input, show dialog
            if tool_name in tools_need_input:
                text, ok = QInputDialog.getText(parent_dialog, f"Execute {display_name}", 
                                               tools_need_input[tool_name])
                if not ok or not text:
                    return
                
                # Build voice command
                command = f"{display_name} {text}"
            else:
                # No input needed
                command = display_name
            
            # Close the dialog
            parent_dialog.close()
            
            # Show executing status
            self.set_status(f"🔧 Executing: {display_name}...")
            
            # Process the command through JARVIS
            try:
                ai_response = process_jarvis_command(command, self)
                memory_manager.add_message("user", command)
                memory_manager.add_message("assistant", ai_response)
                
                # Show result in message box
                QMessageBox.information(self, f"✅ {display_name}", 
                                      f"{ai_response[:500]}..." if len(ai_response) > 500 else ai_response)
            except Exception as e:
                QMessageBox.warning(self, "⚠️ Error", f"Failed to execute tool:\n{str(e)}")
            
            self.set_status("✅ Ready")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error executing tool:\n{str(e)}")

# ============================================================================
# TEXT-TO-SPEECH WITH CLEANUP
# ============================================================================

speech_active = False
speech_paused = False
current_engine = None

def speak_text(text: str, orb: JarvisOrb = None):
    """Speak text using TTS - reinitializes engine each time for thread safety"""
    global speech_active, speech_paused, current_engine
    
    try:
        print(f"🔊 Attempting to speak: {text[:50]}...")
        speech_active = True
        speech_paused = False
        
        # Reinitialize engine each time for thread safety
        current_engine = pyttsx3.init()
        
        # Apply voice settings from settings_manager
        current_engine.setProperty('rate', settings_manager.get('voice_rate', 180))
        current_engine.setProperty('volume', settings_manager.get('voice_volume', 0.9))
        
        # Set voice if available
        voices = current_engine.getProperty('voices')
        voice_id = settings_manager.get('voice_id', 0)
        if voices and 0 <= voice_id < len(voices):
            current_engine.setProperty('voice', voices[voice_id].id)
        
        # Clean text
        clean_text = text
        clean_text = clean_text.replace('```', '')
        clean_text = re.sub(r'http\S+', '', clean_text)
        clean_text = re.sub(r'[^\w\s.,!?\-:;()\[\]{}]', ' ', clean_text)
        clean_text = ' '.join(clean_text.split())
        
        if len(clean_text) > 300:
            speak_text_content = clean_text[:300] + "..."
        else:
            speak_text_content = clean_text
        
        if not speak_text_content.strip():
            print("⚠️ No text to speak after cleaning")
            speech_active = False
            current_engine = None
            return
        
        print(f"🔊 Speaking: {speak_text_content[:50]}...")
        current_engine.say(speak_text_content)
        current_engine.runAndWait()
        
        # Clean up engine
        try:
            current_engine.stop()
            del current_engine
            current_engine = None
        except:
            pass
            
        print("✅ Speech completed")
        speech_active = False
        
        # Small delay to let audio device release
        time.sleep(0.2)
        
        if orb:
            orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
            
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        logging.error(f"TTS Error: {e}")
        import traceback
        traceback.print_exc()
        speech_active = False
        current_engine = None
        if orb:
            orb.set_status("⚠️ TTS Error")

def stop_speech():
    """Stop the current speech immediately"""
    global speech_active, current_engine, speech_paused
    try:
        if current_engine and speech_active:
            current_engine.stop()
            speech_active = False
            speech_paused = False
            current_engine = None
            print("🔇 Speech stopped")
    except Exception as e:
        print(f"Error stopping speech: {e}")
        speech_active = False
        speech_paused = False

# ============================================================================
# MAIN JARVIS ENGINE WITH CHAT INTEGRATION
# ============================================================================

def run_jarvis_engine(orb: JarvisOrb):
    global speech_active
    
    recognizer = sr.Recognizer()
    
    # Use configured microphone or default
    mic_index = settings_manager.get('microphone_index')
    if mic_index is not None:
        mic = sr.Microphone(device_index=mic_index)
        print(f"🎤 Using microphone index: {mic_index}")
    else:
        mic = sr.Microphone()
        print("🎤 Using default microphone")
    
    conversation_mode = False
    last_interaction = time.time()
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Set status based on AI availability
        if ai_mode_enabled:
            orb.set_status("✅ Online (AI Mode)")
            welcome_msg = "Jarvis AI advanced system ready. Say 'Jarvis' to begin."
            speak_text(welcome_msg, orb)
            
            # Add welcome to chat (thread-safe)
            if orb.chat_window and orb.chat_window.isVisible():
                orb.chat_window.add_message_signal.emit("JARVIS", welcome_msg, False)
        else:
            orb.set_status("🛠️ Basic Mode")
            welcome_msg = "Jarvis basic mode active. Install Ollama for AI features. Say 'Jarvis' to begin."
            speak_text(welcome_msg, orb)
            
            # Add welcome to chat (thread-safe)
            if orb.chat_window and orb.chat_window.isVisible():
                orb.chat_window.add_message_signal.emit("JARVIS", welcome_msg, False)
        
        while True:
            try:
                if conversation_mode and (time.time() - last_interaction > CONVERSATION_TIMEOUT):
                    conversation_mode = False
                    orb.set_status("💤 Standby")
                    standby_msg = "Returning to standby."
                    speak_text(standby_msg, orb)
                    orb.update_chat_signal.emit("[Timeout]", standby_msg)
                
                print("👂 Listening for audio...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                print("🎤 Audio captured, recognizing...")
                text = recognizer.recognize_google(audio).lower()
                logging.info(f"🎤 Detected: {text}")
                
                orb.set_status("🔍 Processing...")
                
                if TRIGGER_WORD in text or conversation_mode:
                    orb.set_status("🤔 Analyzing...")
                    
                    if TRIGGER_WORD in text:
                        text = text.replace(TRIGGER_WORD, "").strip()
                    
                    if not text and not conversation_mode:
                        response = "Yes sir? How can I help?"
                        speak_text(response, orb)
                        
                        # Add to chat (thread-safe)
                        orb.update_chat_signal.emit("Jarvis", response)
                        
                        orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
                        conversation_mode = True
                        last_interaction = time.time()
                        continue
                    
                    if not text and conversation_mode:
                        orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
                        continue
                    
                    command = text
                    ai_response = process_jarvis_command(command, orb)
                    
                    # Add to chat and speak (thread-safe)
                    orb.update_chat_signal.emit(command, ai_response)
                    
                    orb.set_status("🗣️ Responding...")
                    logging.info(f"🤖 Response: {ai_response[:100]}...")
                    
                    speak_text(ai_response, orb)
                    
                    conversation_mode = True
                    last_interaction = time.time()
                    orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
                continue
            except Exception as e:
                logging.error(f"Engine Error: {e}")
                orb.set_status("⚠️ Error")
                time.sleep(1)
                orb.set_status("👂 Listening..." if ai_mode_enabled else "🛠️ Basic Mode")
                continue

# ============================================================================
# MAIN ENTRY
# ============================================================================

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("tools", exist_ok=True)
    os.makedirs("Jarvis_Notes", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set high DPI awareness for Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    orb = JarvisOrb(memory_manager)
    orb.show()
    
    # Start engine in a separate thread
    engine_thread = threading.Thread(target=run_jarvis_engine, args=(orb,), daemon=True)
    engine_thread.start()
    
    # Auto-save timer
    def auto_save():
        if memory_manager.current_session:
            memory_manager.save_all_conversations()
    
    save_timer = QTimer()
    save_timer.timeout.connect(auto_save)
    save_timer.start(300000)  # 5 minutes
    
    # Exit handler
    def on_exit():
        if memory_manager.current_session:
            memory_manager.save_all_conversations()
        app.quit()
    
    app.aboutToQuit.connect(on_exit)
    
    print("\n" + "="*70)
    print("🚀 JARVIS AI - HYPERREALISTIC ASSISTANT STARTED SUCCESSFULLY!")
    print("="*70)
    print("🎯 ADVANCED FEATURES:")
    print("   • 60+ powerful tools for complete system control")
    print("   • File management, automation, OCR, network monitoring")
    print("   • Volume control, screenshots, process management")
    print("   • Mouse & keyboard automation, clipboard control")
    print("   • Advanced memory system with conversation history")
    print("   • Hyperrealistic orb interface with taskbar icon")
    print("   • Cool interactive chat UI (Ctrl+C to open)")
    print("="*70)
    print(f"🤖 AI Mode: {'✅ ENABLED' if ai_mode_enabled else '⚠️ DISABLED (Install Ollama)'}")
    if ai_mode_enabled:
        print(f"📦 AI Model: {current_model}")
        print(f"📦 Available Models: {len(available_models)} ({', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''})")
    print(f"🔧 Loaded {len(tools)} tools successfully!")
    print("💡 SAY COMMANDS:")
    print("   • 'Jarvis' followed by your command")
    print("   • Click orb to pause speech")
    print("   • Right-click for menu")
    print("   • Ctrl+C to open chat interface")
    print("="*70 + "\n")
    
    sys.exit(app.exec())
