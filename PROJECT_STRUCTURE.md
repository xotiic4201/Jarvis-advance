# 📁 JARVIS AI - Project Structure

## Directory Layout

```
jarvis-ai/
│
├── main.py                      # Main application entry point
├── setup.py                     # Automated setup script
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md               # Quick start guide
├── .env                        # Environment configuration (auto-generated)
│
├── tools/                      # Tool modules directory
│   ├── __init__.py
│   │
│   ├── pc_control.py          # Computer control tools
│   ├── automation_tools.py    # Keyboard/mouse automation
│   ├── file_tools.py          # File management
│   ├── network_tools.py       # Network & system monitoring
│   ├── screenshot.py          # Screenshot capabilities
│   ├── OCR.py                 # Optical character recognition
│   ├── media_tools.py         # Audio/video control
│   ├── time_tool.py           # Time zone utilities
│   ├── duckduckgo.py          # Web search
│   ├── matrix.py              # Matrix mode effect
│   └── arp_scan.py            # Network scanning
│
├── Jarvis_Notes/              # Notes storage (auto-created)
├── screenshots/               # Screenshot storage (auto-created)
├── recordings/                # Audio recordings (auto-created)
├── pictures/                  # Webcam pictures (auto-created)
├── extracted_text/            # OCR output (auto-created)
├── tts_files/                 # Text-to-speech files (auto-created)
├── macros/                    # Automation macros (auto-created)
│
├── chat_sessions.json         # Conversation history (auto-generated)
├── jarvis_memory.json         # Memory storage (auto-generated)
└── notepad_context.json       # Note context (auto-generated)
```

## Core Files

### `main.py` (1000+ lines)
The main application file containing:
- **JarvisOrb Class**: Hyperrealistic UI with animated orb
- **Memory Management**: Advanced conversation tracking
- **AI Engine**: LangChain integration with Ollama
- **Speech Recognition**: Voice command processing
- **Text-to-Speech**: Natural voice responses
- **Agent Executor**: Tool selection and execution

### `setup.py` (300+ lines)
Automated setup script that:
- Checks Python version
- Installs dependencies
- Verifies Ollama installation
- Checks Tesseract OCR
- Creates necessary directories
- Tests microphone
- Validates imports
- Creates environment file

## Tool Modules

### `pc_control.py` (700+ lines)
**Purpose**: Core computer control and file operations
**Tools**:
- `open_notepad_with_context` - Create contextual notes
- `quick_note` - Fast note creation
- `list_notes` - View all notes
- `open_application` - Launch applications
- `close_application` - Terminate applications
- `execute_command` - Run system commands
- `system_info` - System statistics
- `list_running_apps` - Process list
- `create_file_smart` - Smart file creation

### `automation_tools.py` (300+ lines)
**Purpose**: Keyboard and mouse automation
**Tools**:
- `type_text` - Automated typing
- `press_key` - Keyboard shortcuts
- `click_mouse` - Mouse clicks
- `move_mouse` - Cursor movement
- `get_mouse_position` - Cursor location
- `scroll_screen` - Scroll control
- `copy_to_clipboard` - Clipboard write
- `paste_from_clipboard` - Clipboard read
- `minimize_all_windows` - Desktop view
- `switch_window` - Window switching
- `lock_computer` - Security lock
- `get_screen_size` - Display info

### `file_tools.py` (400+ lines)
**Purpose**: Advanced file management
**Tools**:
- `search_files` - Find files by pattern
- `organize_files` - Auto-organize by type
- `create_zip` - Create archives
- `extract_zip` - Extract archives
- `delete_file` - Remove files
- `rename_file` - Rename files
- `copy_file` - Copy files
- `get_file_info` - File metadata

### `network_tools.py` (500+ lines)
**Purpose**: Network and system monitoring
**Tools**:
- `get_network_info` - Network details
- `network_speed_test` - Connection test
- `list_connections` - Active connections
- `monitor_system_resources` - Resource usage
- `list_processes` - Running processes
- `kill_process` - Terminate process
- `get_battery_status` - Battery info

### `screenshot.py` (200+ lines)
**Purpose**: Screen capture functionality
**Tools**:
- `take_screenshot` - Full screen capture
- `screenshot_all_monitors` - Multi-monitor
- `annotate_screenshot` - Timestamped capture
- `screenshot_window` - Active window

### `OCR.py` (300+ lines)
**Purpose**: Text extraction from images
**Tools**:
- `read_text_from_latest_image` - Latest screenshot OCR
- `read_image_file` - Any image OCR
- `ocr_to_file` - Save OCR to file
- `read_screen_area` - Region OCR
- `detect_language` - Language detection

### `media_tools.py` (400+ lines)
**Purpose**: Audio, video, and media control
**Tools**:
- `control_volume` - Volume management
- `play_sound` - System sounds
- `open_url` - Browser control
- `take_picture` - Webcam capture
- `record_audio` - Audio recording
- `text_to_speech_file` - TTS file generation
- `get_clipboard_history` - Windows clipboard

### `time_tool.py` (100 lines)
**Purpose**: World time zones
**Tools**:
- `get_time` - Time in any city

### `duckduckgo.py` (50 lines)
**Purpose**: Web search
**Tools**:
- `duckduckgo_search_tool` - Search the web

### `matrix.py` (150 lines)
**Purpose**: Visual effects
**Tools**:
- `matrix_mode` - Matrix rain effect

### `arp_scan.py` (50 lines)
**Purpose**: Network scanning
**Tools**:
- `arp_scan_terminal` - Network device discovery

## Data Files

### `chat_sessions.json`
Stores conversation history:
```json
{
  "conversations": [
    {
      "session_id": "session_20240130_120000",
      "timestamp": "2024-01-30T12:00:00",
      "title": "Hello Jarvis",
      "messages": [...],
      "summary": "Greeting conversation",
      "tags": ["casual", "morning"]
    }
  ],
  "last_updated": "2024-01-30T12:30:00"
}
```

### `jarvis_memory.json`
Long-term memory storage (future use)

### `notepad_context.json`
Context for created notes:
```json
{
  "note_20240130.txt": {
    "filepath": "/path/to/note.txt",
    "context": "Meeting notes",
    "content_preview": "Discussion about...",
    "created": "2024-01-30T12:00:00",
    "tags": ["meeting", "work"]
  }
}
```

## Configuration

### `.env` File
Environment variables:
```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Assistant Configuration
TRIGGER_WORD=jarvis
CONVERSATION_TIMEOUT=30
```

## Auto-Created Directories

| Directory | Purpose |
|-----------|---------|
| `Jarvis_Notes/` | Storage for notes created by assistant |
| `screenshots/` | Screenshot captures |
| `recordings/` | Audio recordings |
| `pictures/` | Webcam pictures |
| `extracted_text/` | OCR output text files |
| `tts_files/` | Text-to-speech audio files |
| `macros/` | Automation macros |

## Key Features by File

### User Interface (`main.py`)
- Animated orb with pulsing effects
- Color-coded status indicators
- Drag-and-drop positioning
- Right-click context menu
- Memory manager dialog
- System info display

### Memory System (`main.py`)
- Session-based conversations
- Message history tracking
- Auto-save functionality
- Session management
- Context preservation

### AI Integration (`main.py`)
- Ollama LLM integration
- LangChain agent framework
- Tool calling system
- Smart response routing
- Error handling

## Dependencies

### Core Dependencies
- **LangChain**: AI framework
- **Ollama**: Local LLM
- **PyQt6**: GUI framework
- **pyttsx3**: Text-to-speech
- **SpeechRecognition**: Voice input

### Automation Dependencies
- **pyautogui**: GUI automation
- **pyperclip**: Clipboard
- **keyboard**: Keyboard control
- **mouse**: Mouse control

### System Dependencies
- **psutil**: System monitoring
- **requests**: HTTP client
- **mss**: Screenshots
- **pytesseract**: OCR
- **Pillow**: Image processing

## Extension Points

### Adding New Tools
1. Create tool file in `tools/`
2. Import in `main.py`
3. Add to `tools` list
4. Update system prompt

### Custom Commands
Modify the system prompt in `main.py` to add custom behavior patterns.

### UI Customization
Edit `JarvisOrb` class in `main.py` to change:
- Colors
- Animations
- Size
- Effects

## Performance Considerations

### Memory Usage
- Conversation history pruned automatically
- Sessions saved incrementally
- Tool imports lazy-loaded

### CPU Usage
- Ollama runs locally (CPU/GPU)
- PyQt6 UI thread separate
- Speech recognition async

### Disk Usage
- Screenshots: ~1-5MB each
- Audio recordings: ~1MB per minute
- Chat history: <1MB per 100 messages
- Notes: Minimal

## Security Notes

- No external API calls (except web search)
- All data stored locally
- No telemetry
- Open source and auditable

## Troubleshooting Reference

| Issue | File to Check | Solution |
|-------|---------------|----------|
| Import errors | `requirements.txt` | Reinstall packages |
| Tool not working | `tools/*.py` | Check tool imports |
| Voice not working | `main.py` | Check microphone |
| Ollama errors | `.env` | Check Ollama running |
| UI issues | `main.py` | Check PyQt6 install |

---

**Total Project Size**: ~4,000 lines of code
**Tools Available**: 60+
**Supported Platforms**: Windows, macOS, Linux
