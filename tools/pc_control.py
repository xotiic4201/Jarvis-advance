from langchain.tools import tool
import os
import sys
import subprocess
import platform
import time
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import psutil
import pyautogui
import keyboard
import webbrowser
import shutil
from pathlib import Path

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
        import win32process
        import win32com.client
        import winreg
    except ImportError:
        pass

# Constants
NOTES_DIR = "Jarvis_Notes"
CONTEXT_FILE = "notepad_context.json"
logging.basicConfig(level=logging.INFO)

# Get current directory for file operations
CURRENT_DIR = os.getcwd()
TOOLS_DIR = os.path.join(CURRENT_DIR, "tools")
os.makedirs(TOOLS_DIR, exist_ok=True)

# Application database with commands
APP_DATABASE = {
    "notepad": {
        "windows": "notepad.exe",
        "linux": "gedit",
        "mac": "open -a TextEdit"
    },
    "calculator": {
        "windows": "calc.exe",
        "linux": "gnome-calculator",
        "mac": "open -a Calculator"
    },
    "chrome": {
        "windows": "chrome.exe",
        "linux": "google-chrome",
        "mac": "open -a 'Google Chrome'"
    },
    "firefox": {
        "windows": "firefox.exe",
        "linux": "firefox",
        "mac": "open -a Firefox"
    },
    "edge": {
        "windows": "msedge.exe",
        "linux": "microsoft-edge",
        "mac": "open -a 'Microsoft Edge'"
    },
    "vscode": {
        "windows": "code.cmd",
        "linux": "code",
        "mac": "open -a 'Visual Studio Code'"
    },
    "pycharm": {
        "windows": "pycharm64.exe",
        "linux": "pycharm.sh",
        "mac": "open -a PyCharm"
    },
    "terminal": {
        "windows": "cmd.exe",
        "linux": "gnome-terminal",
        "mac": "open -a Terminal"
    },
    "powershell": {
        "windows": "powershell.exe",
        "linux": "powershell",
        "mac": "pwsh"
    },
    "explorer": {
        "windows": "explorer.exe",
        "linux": "nautilus",
        "mac": "open ."
    },
    "task manager": {
        "windows": "taskmgr.exe",
        "linux": "gnome-system-monitor",
        "mac": "open -a 'Activity Monitor'"
    },
    "settings": {
        "windows": "ms-settings:",
        "linux": "gnome-control-center",
        "mac": "open -a 'System Preferences'"
    },
    "discord": {
        "windows": "discord.exe",
        "linux": "discord",
        "mac": "open -a Discord"
    },
    "spotify": {
        "windows": "spotify.exe",
        "linux": "spotify",
        "mac": "open -a Spotify"
    }
}

# File Cache for pending operations
class FileCache:
    """Cache system for pending file operations"""
    _pending_file = None
    _pending_content = None
    
    @classmethod
    def set_pending_file(cls, filepath: str, content: str):
        """Store a pending file for later save"""
        cls._pending_file = filepath
        cls._pending_content = content
        logging.info(f"Cached pending file: {filepath}")
    
    @classmethod
    def get_pending_file(cls) -> Optional[tuple]:
        """Get pending file if exists"""
        if cls._pending_file and cls._pending_content:
            return (cls._pending_file, cls._pending_content)
        return None
    
    @classmethod
    def clear_pending(cls):
        """Clear pending file"""
        cls._pending_file = None
        cls._pending_content = None

# Helper functions
def ensure_notes_dir():
    """Ensure the notes directory exists"""
    notes_path = os.path.join(CURRENT_DIR, NOTES_DIR)
    os.makedirs(notes_path, exist_ok=True)
    return notes_path

def save_context_to_json(filepath: str, context: str = "", content_preview: str = ""):
    """Save context information about the notepad file"""
    try:
        notes_dir = ensure_notes_dir()
        context_file = os.path.join(notes_dir, CONTEXT_FILE)
        
        # Load existing context
        context_data = {}
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
            except json.JSONDecodeError:
                context_data = {}
        
        # Add new entry
        filename = os.path.basename(filepath)
        context_data[filename] = {
            "filepath": filepath,
            "context": context,
            "content_preview": content_preview[:100] + "..." if content_preview and len(content_preview) > 100 else content_preview or "",
            "created": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "tags": extract_tags(context)
        }
        
        # Save back
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved context for {filename}")
    
    except Exception as e:
        logging.error(f"Failed to save context: {e}")

def extract_tags(context: str) -> List[str]:
    """Extract meaningful tags from context"""
    if not context:
        return []
    
    tags = []
    words = context.lower().split()
    
    # Common categories
    categories = {
        "meeting": ["meeting", "discussion", "call", "conference"],
        "project": ["project", "task", "assignment", "work"],
        "code": ["python", "code", "programming", "script", "function"],
        "idea": ["idea", "concept", "thought", "brainstorm"],
        "todo": ["todo", "task", "reminder", "action", "pending"],
        "note": ["note", "memo", "record", "document"],
        "plan": ["plan", "schedule", "agenda", "timeline"],
        "personal": ["personal", "private", "diary", "journal"]
    }
    
    for word in words:
        for category, keywords in categories.items():
            if word in keywords and category not in tags:
                tags.append(category)
    
    # Add time-based tag
    hour = datetime.now().hour
    if hour < 12:
        tags.append("morning")
    elif hour < 17:
        tags.append("afternoon")
    else:
        tags.append("evening")
    
    return tags[:5]

def open_file_in_notepad(filepath: str):
    """Open a file in the appropriate text editor"""
    system = platform.system()
    try:
        if system == "Windows":
            # Try multiple methods to open notepad
            try:
                # Method 1: Using os.startfile
                os.startfile(filepath)
            except:
                # Method 2: Using subprocess
                subprocess.Popen(['notepad.exe', filepath], shell=True)
            return True
        elif system == "Darwin":
            subprocess.run(["open", "-a", "TextEdit", filepath])
            return True
        else:
            subprocess.run(["xdg-open", filepath])
            return True
    except Exception as e:
        logging.error(f"Failed to open file: {e}")
        return False

# ========== FIXED NOTEPAD TOOL ==========

@tool("open_notepad_with_context", return_direct=True)
def open_notepad_with_context(command_text: str = "") -> str:
    """
    Open Notepad with intelligent context handling - FIXED VERSION.
    This actually works and opens real Notepad with your content.
    
    Examples:
    - "open notepad with meeting notes"
    - "create a note about python projects"
    - "make a note that says I have to"
    - "write hello world to notepad"
    - "open notepad"
    """
    try:
        system = platform.system()
        notes_dir = ensure_notes_dir()
        
        # Parse the command to extract intent and content
        command_lower = command_text.lower() if command_text else ""
        
        # Default values
        content = ""
        context = ""
        
        # Extract content from common patterns
        if "that says" in command_lower:
            parts = command_lower.split("that says")
            if len(parts) > 1:
                content = parts[1].strip()
                context = parts[0].replace("make a note", "").replace("create a note", "").strip()
        elif "write" in command_lower and "to notepad" in command_lower:
            parts = command_lower.split("write")[1].split("to notepad")
            if len(parts) > 0:
                content = parts[0].strip()
        elif "about" in command_lower:
            parts = command_lower.split("about")
            if len(parts) > 1:
                content = parts[1].strip()
                context = parts[0].replace("create a note", "").replace("make a note", "").strip()
        elif command_lower:
            # If the command contains actual text, use it as content
            if len(command_lower.split()) > 2:  # If it's more than just "open notepad"
                content = command_lower
                # Try to extract context from beginning
                if "note" in command_lower:
                    context_parts = command_lower.split("note")
                    if len(context_parts) > 1:
                        context = context_parts[0].strip()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if context:
            safe_context = re.sub(r'[^\w\s-]', '', context.lower())
            safe_context = re.sub(r'[-\s]+', '_', safe_context)
            filename = f"note_{safe_context}_{timestamp}.txt"
        elif content:
            # Use first few words of content for filename
            safe_content = re.sub(r'[^\w\s]', '', content[:30].lower())
            words = safe_content.split()[:3]
            if words:
                filename_base = "_".join(words)
                filename = f"note_{filename_base}_{timestamp}.txt"
            else:
                filename = f"note_{timestamp}.txt"
        else:
            filename = f"note_{timestamp}.txt"
        
        # Ensure .txt extension
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        full_path = os.path.join(notes_dir, filename)
        
        # Determine final content
        final_content = ""
        if content:
            final_content = f"Note: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            final_content += "=" * 40 + "\n\n"
            final_content += f"{content}\n\n"
            final_content += "=" * 40
        else:
            final_content = f"Empty Note - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            final_content += "=" * 40 + "\n\n"
            final_content += "Write your notes here...\n\n"
            final_content += "- \n- \n- \n\n"
            final_content += "=" * 40
        
        # Create the file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Save context
            save_context_to_json(full_path, context or "General note", content or "")
        except Exception as e:
            return f"❌ Failed to create file: {str(e)}"
        
        # Open notepad with the file - USE MULTIPLE METHODS FOR RELIABILITY
        success = False
        error_messages = []
        
        if system == "Windows":
            # Try multiple methods
            methods = [
                lambda: os.startfile(full_path),
                lambda: subprocess.Popen(['notepad.exe', full_path], shell=True),
                lambda: subprocess.Popen(f'start notepad.exe "{full_path}"', shell=True),
                lambda: subprocess.run(['cmd', '/c', 'start', 'notepad.exe', full_path], shell=True)
            ]
            
            for method in methods:
                try:
                    method()
                    success = True
                    break
                except Exception as e:
                    error_messages.append(str(e))
                    continue
        
        elif system == "Darwin":
            try:
                subprocess.Popen(['open', '-a', 'TextEdit', full_path])
                success = True
            except Exception as e:
                error_messages.append(str(e))
        
        elif system == "Linux":
            try:
                subprocess.Popen(['gedit', full_path])
                success = True
            except Exception as e:
                try:
                    subprocess.Popen(['xed', full_path])
                    success = True
                except Exception as e2:
                    error_messages.append(f"gedit: {e}, xed: {e2}")
        
        if success:
            return f"📝 **Notepad opened successfully!**\n" \
                   f"📄 **File:** `{filename}`\n" \
                   f"📁 **Location:** `{full_path}`\n" \
                   f"📏 **Size:** {len(final_content)} characters\n" \
                   f"✅ **Real Notepad window is now open with your note!**"
        else:
            return f"📝 **Note created (editor might not open):**\n" \
                   f"📄 **File:** `{filename}`\n" \
                   f"📁 **Location:** `{full_path}`\n" \
                   f"📏 **Size:** {len(final_content)} characters\n" \
                   f"⚠️ **Editor errors:** {', '.join(error_messages[:2])}"
    
    except Exception as e:
        return f"❌ **Failed to create note:** {str(e)}"

# ========== QUICK NOTE TOOL (SIMPLIFIED) ==========

@tool("quick_note", return_direct=True)
def quick_note(content: str = "") -> str:
    """
    Quickly create a note without opening notepad.
    
    Examples:
    - "quick note: meeting tomorrow at 10am"
    - "save this: project deadline is friday"
    - "note: buy milk"
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a simple filename
        if content:
            words = content.split()[:3]
            if words:
                safe_words = [re.sub(r'[^\w]', '', w.lower()) for w in words]
                filename_base = "_".join(safe_words)
                filename = f"quick_{filename_base}_{timestamp}.txt"
            else:
                filename = f"quick_note_{timestamp}.txt"
        else:
            filename = f"quick_note_{timestamp}.txt"
        
        notes_dir = ensure_notes_dir()
        filepath = os.path.join(notes_dir, filename)
        
        # Write content
        note_content = f"Quick Note - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        note_content += "=" * 40 + "\n\n"
        note_content += content if content else "[No content provided]"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        # Save context
        save_context_to_json(filepath, "Quick note", content[:50] if content else "")
        
        return f"✅ **Quick note saved!**\n" \
               f"📄 **File:** {filename}\n" \
               f"📁 **Location:** {filepath}\n" \
               f"📏 **Size:** {len(note_content)} characters"
    
    except Exception as e:
        return f"❌ Failed to create quick note: {str(e)}"

# ========== LIST NOTES ==========

@tool("list_notes", return_direct=True)
def list_notes() -> str:
    """
    List all notes created with notepad.
    
    Examples:
    - "list my notes"
    - "show all notes"
    - "what notes do I have"
    """
    try:
        notes_dir = ensure_notes_dir()
        
        # List all .txt files in notes directory
        notes = [f for f in os.listdir(notes_dir) if f.endswith('.txt')]
        
        if not notes:
            return "📭 No notes found. Create one with 'open notepad' or 'create note'."
        
        result = "📚 **Your Notes:**\n"
        result += "═" * 50 + "\n"
        
        for i, note in enumerate(sorted(notes), 1):
            note_path = os.path.join(notes_dir, note)
            size = os.path.getsize(note_path)
            modified = datetime.fromtimestamp(os.path.getmtime(note_path)).strftime("%Y-%m-%d %H:%M")
            
            # Try to read first line for preview
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    preview = first_line[:50] + "..." if len(first_line) > 50 else first_line
            except:
                preview = "Could not read preview"
            
            result += f"{i}. **{note}**\n"
            result += f"   📅 Modified: {modified}\n"
            result += f"   📏 Size: {size} bytes\n"
            result += f"   📄 Preview: {preview}\n"
            result += "   ────────────────────────────────\n"
        
        result += f"\n📊 **Total notes:** {len(notes)}"
        result += f"\n📁 **Location:** {notes_dir}"
        return result
    
    except Exception as e:
        return f"❌ Failed to list notes: {str(e)}"

# ========== TEST FUNCTION ==========

@tool("test_note_creation", return_direct=True)
def test_note_creation() -> str:
    """
    Test if note creation works.
    """
    return open_notepad_with_context.func("Test note: This is a test to verify note creation is working.")

# ========== OTHER TOOLS (keep existing) ==========

@tool("list_running_apps", return_direct=True)
def list_running_apps() -> str:
    """List currently running applications."""
    try:
        result = "🖥️ **Running Applications:**\n"
        result += "═" * 50 + "\n"
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
            try:
                info = proc.info
                result += f"📟 **{info['name']}** (PID: {info['pid']})\n"
                result += f"   👤 User: {info['username']}\n"
                result += f"   💾 Memory: {info['memory_percent']:.1f}%\n"
                result += "   ────────────────────────────────\n"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return result
    
    except Exception as e:
        return f"❌ Failed to list running apps: {str(e)}"

@tool("system_info", return_direct=True)
def system_info() -> str:
    """Get detailed system information."""
    try:
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024**3)
        memory_used_gb = memory.used / (1024**3)
        memory_percent = memory.percent
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)
        disk_percent = disk.percent
        
        # Network info
        net_io = psutil.net_io_counters()
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        result = "💻 **System Information:**\n"
        result += "═" * 60 + "\n"
        result += f"🏷️ **OS:** {platform.system()} {platform.release()}\n"
        result += f"🖥️ **Processor:** {platform.processor()}\n"
        result += f"🔢 **CPU Cores:** {cpu_count}\n"
        result += f"📊 **CPU Usage:** {cpu_percent}%\n"
        result += f"💾 **Memory:** {memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB ({memory_percent}%)\n"
        result += f"💿 **Disk:** {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({disk_percent}%)\n"
        result += f"📡 **Network Sent:** {net_io.bytes_sent / (1024**2):.1f} MB\n"
        result += f"📡 **Network Received:** {net_io.bytes_recv / (1024**2):.1f} MB\n"
        result += f"⏰ **Boot Time:** {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"🕐 **Uptime:** {str(uptime).split('.')[0]}\n"
        result += "═" * 60
        
        return result
    
    except Exception as e:
        return f"❌ Failed to get system info: {str(e)}"

@tool("open_application", return_direct=True)
def open_application(app_name: str) -> str:
    """Open an application by name."""
    try:
        system = platform.system()
        app_name_lower = app_name.lower()
        
        if app_name_lower in APP_DATABASE:
            app_info = APP_DATABASE[app_name_lower]
            command = app_info.get(system.lower(), app_name_lower)
            
            if system == "Windows":
                subprocess.Popen(command, shell=True)
            elif system == "Darwin":
                subprocess.Popen(command.split())
            else:  # Linux
                subprocess.Popen([command])
            
            return f"✅ **Opening {app_name.title()}...**\n🚀 Application launched!"
        else:
            # Try generic opening
            if system == "Windows":
                subprocess.Popen(app_name, shell=True)
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            
            return f"✅ **Trying to open {app_name}...**"
    
    except Exception as e:
        return f"❌ **Failed to open {app_name}:** {str(e)}"

@tool("close_application", return_direct=True)
def close_application(app_name: str) -> str:
    """Close an application by name."""
    try:
        app_name_lower = app_name.lower()
        closed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if app_name_lower in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return f"✅ **Closed {app_name.title()}!**\n📊 **Processes terminated:** {closed_count}"
        else:
            return f"⚠️ **{app_name.title()} not found running.**"
    
    except Exception as e:
        return f"❌ **Error closing {app_name}:** {str(e)}"

@tool("execute_command", return_direct=True)
def execute_command(command: str) -> str:
    """Execute a system command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )
        
        output = result.stdout.strip()[:500]
        error = result.stderr.strip()[:500]
        
        response = f"💻 **Command:** `{command}`\n\n"
        if output:
            response += f"📤 **Output:**\n```\n{output}\n```\n"
        if error:
            response += f"❌ **Error:**\n```\n{error}\n```\n"
        response += f"📟 **Exit code:** {result.returncode}"
        
        return response
    
    except subprocess.TimeoutExpired:
        return "⏰ **Command timed out after 20 seconds**"
    except Exception as e:
        return f"❌ **Failed to execute command:** {str(e)}"

@tool("create_file_smart", return_direct=True)
def create_file_smart(filename: str, content: str = "") -> str:
    """Create a file with smart preview."""
    try:
        if '.' not in filename:
            filename = f"{filename}.txt"
        
        if not os.path.isabs(filename):
            filename = os.path.join(CURRENT_DIR, filename)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if os.path.exists(filename):
            return f"⚠️ File already exists: {os.path.basename(filename)}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(filename)
        
        return f"✅ **File created:** `{os.path.basename(filename)}`\n" \
               f"📁 **Location:** {filename}\n" \
               f"📏 **Size:** {file_size} bytes"
    
    except Exception as e:
        return f"❌ Failed to create file: {str(e)}"