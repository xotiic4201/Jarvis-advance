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
                            QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import (QPainter, QPainterPath, QRadialGradient, QLinearGradient, 
                        QColor, QFont, QPen, QBrush, QFontMetrics)

# --- Speech & TTS ---
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# --- Tool Integration ---
def create_dummy_tool(tool_name):
    """Create a dummy tool that explains it's not available"""
    def dummy_func(*args, **kwargs):
        return f"⚠️ **{tool_name} not available**\nPlease check if the tool is properly installed in the tools directory."
    dummy_func.__name__ = tool_name
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
    from tools.OCR import read_text_from_latest_image, read_image_file, ocr_to_file, read_screen_area
    print("✅ OCR tools loaded")
except ImportError as e:
    print(f"⚠️ OCR: {e}")
    read_text_from_latest_image = create_dummy_tool("read_text_from_latest_image")
    read_image_file = create_dummy_tool("read_image_file")
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
        open_application, close_application,
        list_running_apps, execute_command,
        system_info, create_file_smart, test_note_creation
    )
    print("✅ pc_control tools loaded")
except ImportError as e:
    print(f"⚠️ pc_control: {e}")
    open_notepad_with_context = create_dummy_tool("open_notepad_with_context")
    list_notes = create_dummy_tool("list_notes")
    quick_note = create_dummy_tool("quick_note")
    open_application = create_dummy_tool("open_application")
    close_application = create_dummy_tool("close_application")
    list_running_apps = create_dummy_tool("list_running_apps")
    execute_command = create_dummy_tool("execute_command")
    system_info = create_dummy_tool("system_info")
    create_file_smart = create_dummy_tool("create_file_smart")
    test_note_creation = create_dummy_tool("test_note_creation")

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

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.7,
    num_predict=512,
    top_p=0.9
)

# Complete tool list with ALL advanced capabilities
tools = [
    # Core PC Control
    open_notepad_with_context, quick_note, list_notes, test_note_creation,
    open_application, close_application, list_running_apps,
    execute_command, system_info, create_file_smart,
    
    # Screenshot & OCR
    take_screenshot, screenshot_all_monitors, annotate_screenshot, screenshot_window,
    read_text_from_latest_image, read_image_file, ocr_to_file, read_screen_area,
    
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
🖥️ **System Control**: Open/close apps, run commands, monitor resources
⌨️ **Automation**: Type text, click mouse, keyboard shortcuts, window management
📸 **Screenshots & OCR**: Capture screens, read text from images
🌐 **Network**: Check connections, speed tests, network info, kill processes
🔊 **Media**: Control volume, record audio, play sounds, open URLs
🔐 **Security**: Lock computer, manage processes, system monitoring
📊 **Information**: Battery status, system info, time zones, web search

**CONVERSATION STYLE:**
- Be natural, friendly, and efficient like a personal butler
- Use "sir" occasionally but not excessively
- Respond conversationally for simple queries
- Use appropriate tools when user requests specific actions
- Keep responses concise but informative

**EXAMPLES:**
User: "hello" → "Hello sir! How may I assist you today?"
User: "what can you do?" → List your key capabilities
User: "open chrome" → USE open_application tool
User: "type hello world" → USE type_text tool
User: "take screenshot" → USE take_screenshot tool
User: "find all python files" → USE search_files tool
User: "what's my IP?" → USE get_network_info tool
User: "set volume to 50" → USE control_volume tool

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
        self.speech_paused = False
        
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
    
    def pause_speech(self):
        global speech_paused
        speech_paused = True
        self.speech_paused = True
        self.set_status("⏸️ Speech Paused")
    
    def resume_speech(self):
        global speech_paused
        speech_paused = False
        self.speech_paused = False
        self.set_status("▶️ Speech Resumed")
    
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
            self.offset = event.pos()
            # Pause speech when clicked
            self.pause_speech()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_menu(event.globalPosition().toPoint())
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.pos() - self.offset)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
    
    def show_menu(self, pos):
        menu = QMenu()
        menu.addAction("📊 System Info", lambda: self.show_info())
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
CPU Usage: {cpu}%
Memory: {mem}%
Sessions: {len(self.memory_manager.conversations)}
Tools Loaded: {len(tools)}
{'='*40}"""
        
        QMessageBox.information(self, "System Info", info)
    
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
        tools_text = """🛠️ JARVIS TOOL CAPABILITIES:

📁 FILE MANAGEMENT:
• Search, organize, zip, copy, rename files
• Create and extract archives

🖥️ SYSTEM CONTROL:
• Open/close applications
• Execute commands
• Monitor system resources

⌨️ AUTOMATION:
• Type text automatically
• Control mouse and keyboard
• Window management

📸 SCREENSHOTS & OCR:
• Capture screens
• Read text from images
• Annotate screenshots

🌐 NETWORK:
• Network information
• Speed tests
• Connection monitoring

🔊 MEDIA & AUDIO:
• Volume control
• Record audio
• Text-to-speech files

🔐 SECURITY:
• Lock computer
• Kill processes
• Battery monitoring

And 40+ more tools!"""
        
        QMessageBox.information(self, "Jarvis Tools", tools_text)

# ============================================================================
# TEXT-TO-SPEECH WITH CLEANUP
# ============================================================================

def speak_text(text: str, orb: JarvisOrb = None):
    global speech_paused
    
    if speech_paused:
        return
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.9)
        
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
        
        engine.say(speak_text_content)
        engine.runAndWait()
        
        if orb and not orb.speech_paused:
            orb.set_status("👂 Listening...")
            
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        if orb:
            orb.set_status("⚠️ TTS Error")

# ============================================================================
# MAIN JARVIS ENGINE
# ============================================================================

def run_jarvis_engine(orb: JarvisOrb):
    global speech_active, speech_paused
    
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
                if speech_paused:
                    time.sleep(0.5)
                    continue
                
                if conversation_mode and (time.time() - last_interaction > CONVERSATION_TIMEOUT):
                    conversation_mode = False
                    orb.set_status("💤 Standby")
                    speak_text("Returning to standby.", orb)
                
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = recognizer.recognize_google(audio).lower()
                logging.info(f"🎤 Detected: {text}")
                
                orb.set_status("🔍 Processing...")
                
                if "keep going" in text or "continue" in text or "resume" in text:
                    orb.resume_speech()
                    speak_text("Resuming speech.", orb)
                    conversation_mode = True
                    last_interaction = time.time()
                    continue
                
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
                    orb.set_status("✅ Ready")
                    
                    conversation_mode = True
                    last_interaction = time.time()
                
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
    print(f"📦 Loaded {len(tools)} tools successfully!")
    print("💡 Say 'Jarvis' followed by your command")
    print("   • Click orb to pause speech")
    print("   • Right-click for menu")
    print("   • Say 'keep going' to resume")
    print("="*70 + "\n")
    
    sys.exit(app.exec())
