# 🚀 JARVIS AI - Advanced Hyperrealistic Assistant

<div align="center">

**The Ultimate AI-Powered Personal Assistant with 60+ Tools**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

</div>

## ✨ Overview

JARVIS AI is an advanced, hyperrealistic AI assistant that provides complete system control through natural voice commands. With 60+ powerful tools, JARVIS can automate tasks, manage files, control your computer, and much more - all through simple voice interactions.

## 🎯 Key Features

### 🖥️ **Complete System Control**
- Open/close applications
- Execute system commands
- Monitor system resources (CPU, RAM, Disk)
- Process management (list, kill processes)
- Battery monitoring

### 📁 **Advanced File Management**
- Search files with patterns
- Organize files by extension/type
- Create and extract ZIP archives
- Copy, move, rename, delete files
- Get detailed file information

### ⌨️ **Automation & Control**
- Type text automatically
- Control mouse (click, move, scroll)
- Press keyboard shortcuts
- Window management (minimize, maximize, switch)
- Lock computer

### 📸 **Screenshots & OCR**
- Capture full screen or specific windows
- Multi-monitor support
- Annotate screenshots with timestamps
- Extract text from images (OCR)
- Read text from specific screen areas

### 🌐 **Network & Connectivity**
- Get IP addresses (local and public)
- Network speed tests
- List active connections
- Ping tests
- ARP scanning

### 🔊 **Media & Audio Control**
- Control system volume (set, mute, unmute)
- Record audio
- Play system sounds
- Text-to-speech file generation
- Take pictures with webcam

### 🔐 **Security & Privacy**
- Lock computer
- Kill suspicious processes
- Clipboard management
- System monitoring

### 🤖 **AI & Memory**
- Natural conversational AI
- Conversation history and memory
- Session management
- Context-aware responses

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Windows/macOS/Linux
- Microphone for voice commands
- Ollama with qwen2.5:7b model

### Step 1: Clone the Repository
```bash
git clone https://github.com/xotiic4201/Jarvis-advance.git
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Ollama and Model
```bash
# Install Ollama from https://ollama.ai

# Download the model
ollama pull qwen2.5:7b
```

### Step 4: Install Tesseract (for OCR)
**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 5: Run JARVIS
```bash
python main.py
```

## 🎮 Usage

### Voice Commands

#### **General**
- "Jarvis" - Activate assistant
- "Hello" - Greet Jarvis
- "What can you do?" - List capabilities
- "Keep going" / "Resume" - Resume speech

#### **File Operations**
- "Find all Python files"
- "Organize my downloads"
- "Create a zip of this folder"
- "Delete file temp.txt"
- "Rename file to report.pdf"

#### **System Control**
- "Open Chrome"
- "Close Spotify"
- "Show system information"
- "List running processes"
- "Check battery status"

#### **Automation**
- "Type Hello World"
- "Press Ctrl+C"
- "Click mouse at 500, 300"
- "Minimize all windows"
- "Lock my computer"

#### **Screenshots & OCR**
- "Take a screenshot"
- "Screenshot all monitors"
- "Read the latest screenshot"
- "Extract text from image.png"

#### **Network**
- "What's my IP address?"
- "Test network speed"
- "Show active connections"
- "Scan network devices"

#### **Media**
- "Set volume to 50"
- "Mute volume"
- "Record audio for 10 seconds"
- "Open youtube.com"

#### **Search & Information**
- "Search for Python tutorials"
- "What time is it in London?"
- "Get weather in Paris"

## 🛠️ Tools List

### Core Tools (60+)

**PC Control:**
- `open_notepad_with_context` - Create notes with context
- `quick_note` - Quick text notes
- `list_notes` - View all notes
- `open_application` - Open any application
- `close_application` - Close applications
- `execute_command` - Run system commands
- `system_info` - System information
- `list_running_apps` - List processes

**Automation:**
- `type_text` - Type text automatically
- `press_key` - Press keyboard shortcuts
- `click_mouse` - Click at coordinates
- `move_mouse` - Move cursor
- `get_mouse_position` - Get cursor position
- `scroll_screen` - Scroll up/down
- `copy_to_clipboard` - Copy to clipboard
- `paste_from_clipboard` - Get clipboard contents
- `minimize_all_windows` - Show desktop
- `switch_window` - Alt+Tab
- `lock_computer` - Lock system
- `get_screen_size` - Screen resolution

**Screenshots & OCR:**
- `take_screenshot` - Capture screen
- `screenshot_all_monitors` - All monitors
- `annotate_screenshot` - With timestamp
- `screenshot_window` - Active window
- `read_text_from_latest_image` - Read screenshot
- `read_image_file` - Read any image
- `ocr_to_file` - Save OCR to text file
- `read_screen_area` - Specific region

**File Management:**
- `search_files` - Find files
- `organize_files` - Sort by type
- `create_zip` - Create archive
- `extract_zip` - Extract archive
- `delete_file` - Remove file
- `rename_file` - Rename file
- `copy_file` - Copy file
- `get_file_info` - File details

**Network & System:**
- `get_network_info` - Network details
- `network_speed_test` - Speed test
- `list_connections` - Active connections
- `monitor_system_resources` - CPU/RAM/Disk
- `list_processes` - Running processes
- `kill_process` - Terminate process
- `get_battery_status` - Battery info

**Media & Audio:**
- `control_volume` - Volume control
- `play_sound` - System sounds
- `open_url` - Open in browser
- `take_picture` - Webcam capture
- `record_audio` - Record from mic
- `text_to_speech_file` - TTS to file

**Utilities:**
- `get_time` - World time zones
- `duckduckgo_search_tool` - Web search
- `matrix_mode` - Matrix effect
- `arp_scan_terminal` - Network scanning

## 🎨 User Interface

### Hyperrealistic Orb
- **Animated orb** with pulsing effects
- **Status indicators** (listening, processing, error)
- **Color-coded** states
- **Draggable** interface
- **Right-click menu** for settings

### Features
- Click orb to pause speech
- Right-click for menu
- Visual status feedback
- Memory manager interface
- System information display

## ⚙️ Configuration

### Environment Variables
Create a `.env` file:
```env
# Optional configurations
OLLAMA_HOST=http://localhost:11434
TRIGGER_WORD=jarvis
CONVERSATION_TIMEOUT=30
```

### Customization
Edit `main.py` to customize:
- `TRIGGER_WORD` - Wake word
- `CONVERSATION_TIMEOUT` - Conversation timeout
- LLM model and parameters
- Voice settings

## 📋 Requirements

### Python Packages
- `langchain` - AI framework
- `langchain-ollama` - Ollama integration
- `PyQt6` - GUI interface
- `pyttsx3` - Text-to-speech
- `SpeechRecognition` - Voice recognition
- `pyautogui` - Automation
- `pyperclip` - Clipboard
- `psutil` - System monitoring
- `requests` - HTTP requests
- `mss` - Screenshots
- `pytesseract` - OCR
- `Pillow` - Image processing
- `python-dotenv` - Environment variables
- `duckduckgo-search` - Web search
- `pytz` - Timezones

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Microphone**: Required for voice commands
- **Internet**: Required for AI model and web features

## 🔧 Troubleshooting

### Common Issues

**Voice recognition not working:**
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Ollama connection error:**
```bash
# Check Ollama is running
ollama list

# Restart Ollama
ollama serve
```

**OCR not working:**
- Ensure Tesseract is installed and in PATH
- Test: `tesseract --version`

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain for AI framework
- Ollama for local LLM
- PyQt6 for GUI
- All open-source contributors

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎯 Roadmap

- [ ] Web interface
- [ ] Mobile app integration
- [ ] Cloud synchronization
- [ ] Plugin system
- [ ] Multi-language support
- [ ] Voice cloning
- [ ] Custom wake words
- [ ] Advanced automation macros

---

<div align="center">

**Made with ❤️ by the JARVIS AI Team**

⭐ Star us on GitHub!

</div>
