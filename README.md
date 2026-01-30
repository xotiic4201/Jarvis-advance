
# 🚀 JARVIS AI - Advanced Hyperrealistic Assistant

<div align="center">

**The Ultimate AI-Powered Personal Assistant with 60+ Tools**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/xotiic4201/Jarvis-advance)
[![Windows](https://img.shields.io/badge/Windows-Supported-blue)](https://github.com/xotiic4201/Jarvis-advance/releases)
[![Release](https://img.shields.io/badge/Download-Installer-green)](https://github.com/xotiic4201/Jarvis-advance/releases)

</div>

## ✨ Overview

JARVIS AI is an advanced, hyperrealistic AI assistant that provides complete system control through natural voice commands. With 60+ powerful tools, JARVIS can automate tasks, manage files, control your computer, and much more - all through simple voice interactions.

**NEW: Now available as a single EXE installer!** No Python required!

## 🎯 Key Features

### 🖥️ **Complete System Control**
- Open/close any Windows application
- Execute system commands
- Monitor system resources (CPU, RAM, Disk)
- Process management (list, kill processes)
- Battery monitoring
- Real-time system information

### 📁 **Advanced File Management**
- Search files with patterns
- Organize files by extension/type
- Create and extract ZIP archives
- Copy, move, rename, delete files
- Get detailed file information
- Smart file operations

### ⌨️ **Automation & Control**
- Type text automatically
- Control mouse (click, move, scroll)
- Press keyboard shortcuts
- Window management (minimize, maximize, switch)
- Lock computer
- Clipboard automation

### 📸 **Screenshots & OCR**
- Capture full screen or specific windows
- Multi-monitor support
- Annotate screenshots with timestamps
- Extract text from images (OCR)
- Read text from specific screen areas
- Save OCR to text files

### 🌐 **Network & Connectivity**
- Get IP addresses (local and public)
- Network speed tests
- List active connections
- Ping tests
- ARP scanning
- Real-time network monitoring

### 🔊 **Media & Audio Control**
- Control system volume (set, mute, unmute)
- Record audio from microphone
- Play system sounds
- Text-to-speech file generation
- Take pictures with webcam
- Open URLs in browser

### 🔐 **Security & Privacy**
- Lock computer instantly
- Kill suspicious processes
- Clipboard management
- System monitoring
- Local AI processing (no cloud)

### 🤖 **AI & Memory**
- Natural conversational AI with Ollama
- Conversation history and memory
- Session management
- Context-aware responses
- Multiple AI model support

## 🚀 Quick Installation (Windows)

### **Option 1: Easy Installer (Recommended)**
1. Download `JARVIS_AI_Setup.exe` from [Releases](https://github.com/xotiic4201/Jarvis-advance/releases)
2. Run the installer
3. Launch JARVIS from Start Menu or Desktop

### **Option 2: Manual Setup**
#### Prerequisites
- Python 3.8 or higher
- Windows 10/11
- Microphone for voice commands

#### Step 1: Clone the Repository
```bash
git clone https://github.com/xotiic4201/Jarvis-advance.git
cd Jarvis-advance
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Install Ollama (for AI features)
1. Download Ollama from https://ollama.ai
2. Install and run Ollama
3. Download the model:
```bash
ollama pull qwen2.5:7b
```

#### Step 4: Install Tesseract (for OCR)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

#### Step 5: Run JARVIS
```bash
python main.py
```

## 🎮 Usage

### **First Launch**
1. Start JARVIS
2. Say "Jarvis" to activate
3. Wait for "Online" status
4. Start giving commands!

### **Voice Commands Examples**

#### **General Commands**
- "Jarvis, hello" - Start conversation
- "What can you do?" - See capabilities
- "Keep going" / "Resume" - Resume speech
- "Stop speaking" - Pause speech

#### **File Operations**
- "Find all PDF files"
- "Organize my downloads folder"
- "Create a zip of Documents folder"
- "Delete temp.txt"
- "Copy report.pdf to Desktop"

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

#### **Network & Information**
- "What's my IP address?"
- "Test network speed"
- "Show active connections"
- "What time is it in Tokyo?"

#### **Media Control**
- "Set volume to 50"
- "Mute volume"
- "Record audio for 10 seconds"
- "Open youtube.com"

## 🛠️ Interface Guide

### **Hyperrealistic Orb**
- **Blue Orb**: Ready/Loading
- **Green Orb**: Listening
- **Yellow Orb**: Processing
- **Red Orb**: Error

### **Controls**
- **Left Click**: Pause/Resume speech
- **Right Click**: Open settings menu
- **Drag**: Move orb anywhere on screen
- **Double Click**: Show system info

### **Menu Options**
- **Settings**: Configure voice, AI model, colors
- **Memory Manager**: View conversation history
- **Tools Browser**: See all 60+ available tools
- **System Info**: View system status
- **Change AI Model**: Switch between Ollama models
- **Change Color**: Customize orb appearance

## 🔧 Building from Source

### **Create EXE (for distribution)**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico --name="JARVIS" --add-data="requirements.txt;." --add-data="README.md;." --hidden-import=pyttsx3.drivers --hidden-import=pyttsx3.drivers.sapi5 --hidden-import=speech_recognition --hidden-import=PyQt6 --hidden-import=pyautogui --hidden-import=psutil --hidden-import=mss --hidden-import=langchain --collect-all=pyttsx3 --collect-all=PyQt6 main.py

# Copy tools folder
xcopy /E /I /Y tools dist\tools
```

### **Create Installer**
1. Use Inno Setup Compiler
2. Load `JARVIS_Setup.iss`
3. Compile to create `JARVIS_AI_Setup.exe`

## 📋 System Requirements

### **Minimum**
- **OS**: Windows 10/11 (64-bit)
- **CPU**: Intel i3 / AMD Ryzen 3 or better
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Microphone**: Required

### **Recommended**
- **OS**: Windows 11
- **CPU**: Intel i5 / AMD Ryzen 5 or better
- **RAM**: 8GB+
- **GPU**: Dedicated GPU for better AI performance
- **Storage**: 5GB+ for AI models

## 🐛 Troubleshooting

### **Common Issues & Solutions**

**Voice not working:**
```
1. Check microphone permissions
2. Test with: python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
3. Ensure microphone is set as default device
```

**Ollama errors:**
```
1. Verify Ollama is running: ollama list
2. Restart Ollama: ollama serve
3. Pull model: ollama pull qwen2.5:7b
```

**OCR not working:**
```
1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Add to System PATH
3. Restart computer
```

**Import errors:**
```
1. Update pip: python -m pip install --upgrade pip
2. Reinstall: pip install -r requirements.txt --force-reinstall
3. Check Python version (3.8+ required)
```

**GUI not showing:**
```
1. Install VC++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reinstall PyQt6: pip install --force-reinstall PyQt6
```

## 📁 Project Structure

```
Jarvis-advance/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
├── README.md              # This file
├── icon.ico               # Application icon
├── LICENSE.txt            # License file
├── tools/                 # 60+ tools
│   ├── pc_control.py     # PC control tools
│   ├── app_launcher.py   # Application launcher
│   ├── automation_tools.py # Automation
│   ├── file_tools.py     # File management
│   ├── network_tools.py  # Network tools
│   ├── screenshot.py     # Screenshots
│   ├── media_tools.py    # Media control
│   ├── OCR.py           # OCR functionality
│   └── ...               # More tools
├── dist/                  # Built executables
└── Output/               # Installer output
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** changes: `git commit -m 'Add AmazingFeature'`
4. **Push** to branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=xotiic4201/Jarvis-advance&type=Date)](https://star-history.com/#xotiic4201/Jarvis-advance&Date)

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/xotiic4201/Jarvis-advance/issues)
- **Discussions**: [GitHub Discussions](https://github.com/xotiic4201/Jarvis-advance/discussions)
- **Wiki**: [Documentation](https://github.com/xotiic4201/Jarvis-advance/wiki)

## 🚀 Quick Start Video

[![Watch the video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtube.com/YOUR_VIDEO_LINK)

---

<div align="center">

### **Made with ❤️ by xotiic**

**⭐ Star this repo if you find it useful!**

[![GitHub stars](https://img.shields.io/github/stars/xotiic4201/Jarvis-advance?style=social)](https://github.com/xotiic4201/Jarvis-advance/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/xotiic4201/Jarvis-advance?style=social)](https://github.com/xotiic4201/Jarvis-advance/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/xotiic4201/Jarvis-advance?style=social)](https://github.com/xotiic4201/Jarvis-advance/watchers)

</div>
