"""
Advanced Media and Audio Control Tools for Jarvis AI
"""

from langchain.tools import tool
import platform
import subprocess
import os
from typing import Optional


@tool("control_volume", return_direct=True)
def control_volume(action: str, level: int = None) -> str:
    """
    Control system volume.
    
    Examples:
    - "Set volume to 50"
    - "Increase volume"
    - "Mute"
    
    Args:
        action: 'set', 'up', 'down', 'mute', 'unmute'
        level: Volume level 0-100 (for 'set' action)
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            if action == "mute":
                subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], check=False)
                return "🔇 **Volume muted!**"
            elif action == "unmute":
                subprocess.run(['nircmd.exe', 'mutesysvolume', '0'], check=False)
                return "🔊 **Volume unmuted!**"
            elif action == "up":
                subprocess.run(['nircmd.exe', 'changesysvolume', '2000'], check=False)
                return "🔊 **Volume increased!**"
            elif action == "down":
                subprocess.run(['nircmd.exe', 'changesysvolume', '-2000'], check=False)
                return "🔉 **Volume decreased!**"
            elif action == "set" and level is not None:
                # NirCmd uses 0-65535 scale
                nircmd_level = int((level / 100) * 65535)
                subprocess.run(['nircmd.exe', 'setsysvolume', str(nircmd_level)], check=False)
                return f"🔊 **Volume set to {level}%!**"
        
        elif system == "Darwin":  # macOS
            if action == "set" and level is not None:
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'])
                return f"🔊 **Volume set to {level}%!**"
            elif action == "mute":
                subprocess.run(['osascript', '-e', 'set volume output muted true'])
                return "🔇 **Volume muted!**"
            elif action == "unmute":
                subprocess.run(['osascript', '-e', 'set volume output muted false'])
                return "🔊 **Volume unmuted!**"
        
        else:  # Linux
            if action == "set" and level is not None:
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'])
                return f"🔊 **Volume set to {level}%!**"
            elif action == "mute":
                subprocess.run(['amixer', 'set', 'Master', 'mute'])
                return "🔇 **Volume muted!**"
            elif action == "unmute":
                subprocess.run(['amixer', 'set', 'Master', 'unmute'])
                return "🔊 **Volume unmuted!**"
        
        return "⚠️ **Action not supported on this platform**"
    except Exception as e:
        return f"❌ Failed: {str(e)}\n💡 Tip: On Windows, NirCmd may be required"


@tool("play_sound", return_direct=True)
def play_sound(sound_type: str = "beep") -> str:
    """
    Play system sounds.
    
    Examples:
    - "Play a beep"
    - "Make a sound"
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            import winsound
            if sound_type == "beep":
                winsound.Beep(1000, 500)
            elif sound_type == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif sound_type == "warning":
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif sound_type == "info":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            return f"🔊 **Played {sound_type} sound!**"
        
        elif system == "Darwin":
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
            return "🔊 **Played system sound!**"
        
        else:  # Linux
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/bell.oga'], check=False)
            return "🔊 **Played system sound!**"
    
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("open_url", return_direct=True)
def open_url(url: str) -> str:
    """
    Open a URL in the default browser.
    
    Examples:
    - "Open google.com"
    - "Go to youtube.com"
    """
    try:
        import webbrowser
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return f"🌐 **Opened in browser:** {url}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("take_picture", return_direct=True)
def take_picture(camera_index: int = 0) -> str:
    """
    Take a picture using webcam.
    
    Examples:
    - "Take a picture"
    - "Capture webcam"
    """
    try:
        import cv2
        from datetime import datetime
        
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return "❌ **Could not access camera**"
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "❌ **Failed to capture image**"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pictures_dir = os.path.join(os.getcwd(), "pictures")
        os.makedirs(pictures_dir, exist_ok=True)
        
        filename = f"picture_{timestamp}.jpg"
        filepath = os.path.join(pictures_dir, filename)
        
        cv2.imwrite(filepath, frame)
        
        return f"📸 **Picture captured!**\n📁 **Saved to:** {filepath}"
    except ImportError:
        return "❌ **OpenCV not installed.** Install with: pip install opencv-python"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("record_audio", return_direct=True)
def record_audio(duration: int = 5) -> str:
    """
    Record audio from microphone.
    
    Examples:
    - "Record audio for 10 seconds"
    - "Start recording"
    
    Args:
        duration: Recording duration in seconds
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        from datetime import datetime
        import numpy as np
        
        sample_rate = 44100
        
        print(f"🎤 Recording for {duration} seconds...")
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=2, 
                          dtype=np.int16)
        sd.wait()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recordings_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(recordings_dir, filename)
        
        sf.write(filepath, recording, sample_rate)
        
        return f"🎤 **Audio recorded!**\n⏱️ **Duration:** {duration}s\n📁 **Saved to:** {filepath}"
    except ImportError:
        return "❌ **Required libraries not installed.** Install with: pip install sounddevice soundfile"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("text_to_speech_file", return_direct=True)
def text_to_speech_file(text: str, filename: str = None) -> str:
    """
    Convert text to speech and save as audio file.
    
    Examples:
    - "Save 'Hello World' as audio"
    - "Convert this text to speech file"
    """
    try:
        import pyttsx3
        from datetime import datetime
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}.mp3"
        
        if not filename.endswith(('.mp3', '.wav')):
            filename += '.mp3'
        
        tts_dir = os.path.join(os.getcwd(), "tts_files")
        os.makedirs(tts_dir, exist_ok=True)
        filepath = os.path.join(tts_dir, filename)
        
        engine = pyttsx3.init()
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        
        return f"🔊 **Text-to-speech file created!**\n📝 **Text:** {text[:50]}...\n📁 **Saved to:** {filepath}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("get_clipboard_history", return_direct=True)
def get_clipboard_history() -> str:
    """
    Get clipboard history (Windows 10+).
    
    Examples:
    - "Show clipboard history"
    - "What's in my clipboard history?"
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # On Windows 10+, Win+V opens clipboard history
            import pyautogui
            pyautogui.hotkey('win', 'v')
            return "✅ **Clipboard history opened!** (Windows clipboard panel)"
        else:
            return "⚠️ **Clipboard history is a Windows 10+ feature**"
    except Exception as e:
        return f"❌ Failed: {str(e)}"
