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
                            QListWidget, QListWidgetItem, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import (QPainter, QPainterPath, QRadialGradient, QLinearGradient, 
                        QColor, QFont, QPen, QBrush, QFontMetrics)

# --- Speech & TTS ---
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# --- Tool Integration ---
from langchain.tools import tool as langchain_tool

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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Speech control flags
speech_active = True
speech_paused = False

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

# Initialize memory manager
memory_manager = AdvancedMemoryManager()

# ============================================================================
# AI BRAIN SETUP WITH ALL TOOLS
# ============================================================================

# Global variables for model management
current_model = "qwen2.5:7b"
available_models = []

def get_ollama_models():
    """Get list of installed Ollama models"""
    try:
        import subprocess
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
    global llm, executor, executor_with_history, current_model
    
    if model_name:
        current_model = model_name
    
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
    
    logging.info(f"🤖 LLM initialized with model: {current_model}")
    return llm

# Get available models on startup
available_models = get_ollama_models()
if available_models:
    logging.info(f"📦 Found {len(available_models)} Ollama models: {', '.join(available_models)}")
else:
    logging.warning("⚠️ No Ollama models found or Ollama not running")

llm = ChatOllama(
    model=current_model,
    temperature=0,
    num_predict=512,
    top_p=0.9
)

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

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    max_iterations=3,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)

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

executor_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# ============================================================================
# ENHANCED RESPONSE HANDLER
# ============================================================================

def process_jarvis_command(user_input: str, orb) -> str:
    """Process command through AI with context"""
    try:
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
# HYPERREALISTIC ORB UI (ENHANCED)
# ============================================================================

class JarvisOrb(QWidget):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.status_text = "🚀 Initializing..."
        
        # Orb properties
        self.pulse_phase = 0
        self.rotation = 0
        self.pulse_speed = 0.05
        self.base_radius = 60
        self.current_radius = self.base_radius
        
        # Colors
        self.core_color = QColor(0, 150, 255)
        self.glow_color = QColor(100, 200, 255)
        
        # Setup UI
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle("JARVIS")
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        
        # Make draggable
        self.dragging = False
        self.drag_started = False
        self.offset = QPoint()
    
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
        else:
            self.core_color = QColor(0, 150, 255)
            self.glow_color = QColor(100, 200, 255)
        
        self.update()
    
    def stop_speaking(self):
        """Stop current speech output"""
        stop_speech()
        self.set_status("🔇 Speech Stopped")
        QTimer.singleShot(1000, lambda: self.set_status("👂 Listening..."))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2 - 20
        
        # Outer glow
        for i in range(5):
            glow_radius = self.current_radius + (i * 15)
            alpha = 50 - (i * 10)
            gradient = QRadialGradient(center_x, center_y, glow_radius)
            gradient.setColorAt(0, QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), alpha))
            gradient.setColorAt(1, QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)
        
        # Core orb
        gradient = QRadialGradient(center_x, center_y, self.current_radius)
        gradient.setColorAt(0, QColor(255, 255, 255, 200))
        gradient.setColorAt(0.5, self.core_color)
        gradient.setColorAt(1, QColor(self.core_color.red()//2, self.core_color.green()//2, self.core_color.blue()//2))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.drawEllipse(QPointF(center_x, center_y), self.current_radius, self.current_radius)
        
        # Status text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
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
    
    def show_menu(self, pos):
        menu = QMenu()
        menu.addAction("📊 System Info", lambda: self.show_info())
        menu.addAction("🤖 Change AI Model", lambda: self.show_model_selector())
        menu.addAction("💾 Memory Manager", lambda: self.show_memory_dialog())
        menu.addAction("🎨 Change Color", lambda: self.change_color())
        menu.addAction("📋 Show Tools", lambda: self.show_tools())
        menu.addAction("❌ Exit", self.close)
        menu.exec(pos)
    
    def show_info(self):
        import platform
        import psutil
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        info = f"""🖥️ JARVIS SYSTEM STATUS
        
{'='*40}
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
AI Model: {current_model}
CPU Usage: {cpu}%
Memory: {mem}%
Sessions: {len(self.memory_manager.conversations)}
Tools Loaded: {len(tools)}
{'='*40}"""
        
        QMessageBox.information(self, "System Info", info)
    
    def show_model_selector(self):
        """Show dialog to select Ollama model"""
        global available_models, current_model
        
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
            self.update()
    
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
        current_engine.setProperty('rate', 180)
        current_engine.setProperty('volume', 0.9)
        
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
            orb.set_status("👂 Listening...")
            
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
# MAIN JARVIS ENGINE
# ============================================================================

def run_jarvis_engine(orb: JarvisOrb):
    global speech_active
    
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    conversation_mode = False
    last_interaction = time.time()
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        orb.set_status("✅ Online")
        speak_text("Jarvis AI advanced system ready. Say 'Jarvis' to begin.", orb)
        
        while True:
            try:
                if conversation_mode and (time.time() - last_interaction > CONVERSATION_TIMEOUT):
                    conversation_mode = False
                    orb.set_status("💤 Standby")
                    speak_text("Returning to standby.", orb)
                
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
                        memory_manager.add_message("user", "jarvis")
                        memory_manager.add_message("assistant", response)
                        orb.set_status("👂 Listening...")
                        conversation_mode = True
                        last_interaction = time.time()
                        continue
                    
                    if not text and conversation_mode:
                        orb.set_status("👂 Listening...")
                        continue
                    
                    command = text
                    memory_manager.add_message("user", command)
                    
                    ai_response = process_jarvis_command(command, orb)
                    memory_manager.add_message("assistant", ai_response)
                    
                    orb.set_status("🗣️ Responding...")
                    logging.info(f"🤖 Response: {ai_response[:100]}...")
                    
                    speak_text(ai_response, orb)
                    
                    conversation_mode = True
                    last_interaction = time.time()
                    orb.set_status("👂 Listening...")
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                orb.set_status("👂 Listening...")
                continue
            except Exception as e:
                logging.error(f"Engine Error: {e}")
                orb.set_status("⚠️ Error")
                time.sleep(1)
                orb.set_status("👂 Listening...")
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
    
    orb = JarvisOrb(memory_manager)
    orb.show()
    
    engine_thread = threading.Thread(target=run_jarvis_engine, args=(orb,), daemon=True)
    engine_thread.start()
    
    # Auto-save timer
    def auto_save():
        if memory_manager.current_session:
            memory_manager.save_all_conversations()
    
    save_timer = QTimer()
    save_timer.timeout.connect(auto_save)
    save_timer.start(300000)
    
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
    print("   • Hyperrealistic orb interface")
    print("="*70)
    print(f"🤖 AI Model: {current_model}")
    print(f"📦 Available Models: {len(available_models)} ({', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''})")
    print(f"🔧 Loaded {len(tools)} tools successfully!")
    print("💡 Say 'Jarvis' followed by your command")
    print("   • Click orb to pause speech")
    print("   • Right-click for menu → Change AI Model")
    print("   • Say 'keep going' to resume")
    print("="*70 + "\n")
    
    sys.exit(app.exec())
