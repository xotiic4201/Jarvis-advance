# 🚀 JARVIS AI - Quick Start Guide

## ⚡ Fast Setup (5 Minutes)

### Step 1: Install Python
Make sure you have Python 3.8+ installed:
```bash
python --version
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Ollama
1. Go to https://ollama.ai
2. Download and install Ollama
3. Open terminal and run:
```bash
ollama pull qwen2.5:7b
```

### Step 4: Install Tesseract (OCR)
**Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
**Mac:** `brew install tesseract`
**Linux:** `sudo apt-get install tesseract-ocr`

### Step 5: Run JARVIS
```bash
python main.py
```

## 🎯 First Commands to Try

Once JARVIS is running, try these:

1. **Say "Jarvis"** - Activate the assistant
2. **Say "Hello"** - Test basic conversation
3. **Say "What can you do?"** - See capabilities
4. **Say "Take a screenshot"** - Test screenshot tool
5. **Say "Open Chrome"** - Test app control
6. **Say "What time is it in London?"** - Test time tool

## 💡 Pro Tips

### Voice Commands
- Speak clearly and at normal pace
- Wait for the blue orb to pulse before speaking
- Say "Jarvis" to wake up, then give your command
- Click the orb to pause speech
- Say "keep going" or "resume" to continue

### Interface Controls
- **Left Click Orb**: Pause speech
- **Right Click Orb**: Open menu
- **Drag Orb**: Move around screen
- **Menu Options**:
  - System Info
  - Memory Manager
  - Change Color
  - Show Tools
  - Exit

### Common Issues

**Microphone Not Working:**
```bash
# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Ollama Not Running:**
```bash
# Start Ollama
ollama serve

# Verify model
ollama list
```

**Permission Errors (Linux/Mac):**
```bash
# Give microphone permissions in system settings
# For automation features, may need accessibility permissions
```

## 📚 Example Commands

### File Management
```
"Find all PDF files"
"Organize my downloads"
"Create a zip of Documents folder"
"Delete temp.txt"
"Copy report.pdf to Desktop"
```

### System Control
```
"Open Firefox"
"Close Spotify"
"Show system info"
"List running processes"
"Check battery"
```

### Automation
```
"Type Hello World"
"Press Ctrl+C"
"Move mouse to 500, 300"
"Minimize all windows"
"Lock computer"
```

### Screenshots & OCR
```
"Take screenshot"
"Screenshot all monitors"
"Read the latest screenshot"
"Extract text from image.png"
```

### Network & Info
```
"What's my IP?"
"Test network speed"
"Show connections"
"What time is it in Tokyo?"
```

### Media
```
"Set volume to 50"
"Mute"
"Open youtube.com"
"Record audio for 10 seconds"
```

## 🎨 Customization

### Change Wake Word
Edit `main.py`:
```python
TRIGGER_WORD = "jarvis"  # Change to your preferred word
```

### Adjust Voice Speed
Edit `main.py`:
```python
engine.setProperty('rate', 180)  # Adjust number (150-200)
```

### Change Orb Color
Right-click orb → "Change Color" → Select color

## 🔧 Troubleshooting Quick Fixes

### Issue: Can't hear Jarvis
- Check system volume
- Verify speakers/headphones
- Test with: `python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"`

### Issue: Jarvis doesn't hear me
- Check microphone settings
- Test with speech_recognition
- Ensure microphone permissions granted

### Issue: Tools not working
- Reinstall: `pip install -r requirements.txt --force-reinstall`
- Check tool-specific requirements (Tesseract for OCR, etc.)

### Issue: Ollama errors
- Restart Ollama: `ollama serve`
- Re-pull model: `ollama pull qwen2.5:7b`

## 📞 Getting Help

1. Check README.md for detailed documentation
2. Review troubleshooting section
3. Check error logs in terminal
4. Create GitHub issue with error details

## 🎯 Next Steps

Once comfortable with basics:
1. Explore all 60+ tools
2. Create custom automation sequences
3. Customize the UI
4. Add your own tools in the `tools/` directory
5. Experiment with different Ollama models

## 🌟 Best Practices

1. **Clear Commands**: Be specific in what you want
2. **Wait for Response**: Let Jarvis finish before next command
3. **Use Tools**: Ask "What can you do?" to discover features
4. **Save Sessions**: Jarvis remembers conversations
5. **Regular Updates**: Keep dependencies updated

---

**Enjoy your hyperrealistic AI assistant! 🚀**

Say "Jarvis, what can you do?" to get started!
