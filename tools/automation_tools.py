"""
Advanced System Automation Tools for Jarvis AI
Provides clipboard, keyboard, mouse control, window management, and automation features
"""

from langchain.tools import tool
import platform
import subprocess
import time
import pyautogui
import pyperclip
from typing import Optional
import json
import os

# Configure pyautogui safety
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True


@tool("type_text", return_direct=True)
def type_text(text: str, interval: float = 0.05) -> str:
    """
    Type text as if using keyboard. Useful for automation.
    
    Examples:
    - "Type 'Hello World'"
    - "Type my email address"
    - "Enter this text into the form"
    """
    try:
        time.sleep(0.5)
        pyautogui.write(text, interval=interval)
        return f"✅ **Typed text successfully!**\n📝 **Text:** {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        return f"❌ Failed to type text: {str(e)}"


@tool("press_key", return_direct=True)
def press_key(key_combination: str) -> str:
    """
    Press a key or key combination.
    
    Examples:
    - "Press enter"
    - "Press ctrl+c"
    - "Press alt+tab"
    """
    try:
        keys = key_combination.lower().split('+')
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
        return f"✅ **Pressed key:** {key_combination}"
    except Exception as e:
        return f"❌ Failed to press key: {str(e)}"


@tool("copy_to_clipboard", return_direct=True)
def copy_to_clipboard(text: str) -> str:
    """Copy text to system clipboard."""
    try:
        pyperclip.copy(text)
        return f"✅ **Copied to clipboard!**\n📋 **Text:** {text[:100]}{'...' if len(text) > 100 else ''}"
    except Exception as e:
        return f"❌ Failed to copy: {str(e)}"


@tool("paste_from_clipboard", return_direct=True)
def paste_from_clipboard() -> str:
    """Get text from system clipboard."""
    try:
        text = pyperclip.paste()
        if not text:
            return "📋 **Clipboard is empty**"
        return f"📋 **Clipboard contents:**\n{text[:500]}{'...' if len(text) > 500 else ''}"
    except Exception as e:
        return f"❌ Failed to read clipboard: {str(e)}"


@tool("click_mouse", return_direct=True)
def click_mouse(x: int, y: int, clicks: int = 1, button: str = "left") -> str:
    """Click mouse at specific coordinates."""
    try:
        pyautogui.click(x, y, clicks=clicks, button=button)
        return f"✅ **Mouse clicked!**\n📍 **Position:** ({x}, {y})\n🖱️ **Button:** {button}"
    except Exception as e:
        return f"❌ Failed to click: {str(e)}"


@tool("move_mouse", return_direct=True)
def move_mouse(x: int, y: int, duration: float = 0.5) -> str:
    """Move mouse to specific coordinates."""
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"✅ **Mouse moved to:** ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to move mouse: {str(e)}"


@tool("get_mouse_position", return_direct=True)
def get_mouse_position() -> str:
    """Get current mouse cursor position."""
    try:
        x, y = pyautogui.position()
        return f"🖱️ **Mouse Position:** X: {x}, Y: {y}"
    except Exception as e:
        return f"❌ Failed to get position: {str(e)}"


@tool("scroll_screen", return_direct=True)
def scroll_screen(amount: int, direction: str = "down") -> str:
    """Scroll the screen up or down."""
    try:
        scroll_amount = amount if direction.lower() == "down" else -amount
        pyautogui.scroll(scroll_amount * 100)
        return f"✅ **Scrolled {direction}!** Amount: {amount}"
    except Exception as e:
        return f"❌ Failed to scroll: {str(e)}"


@tool("minimize_all_windows", return_direct=True)
def minimize_all_windows() -> str:
    """Minimize all open windows (show desktop)."""
    try:
        system = platform.system()
        if system == "Windows":
            pyautogui.hotkey('win', 'd')
        elif system == "Darwin":
            pyautogui.hotkey('command', 'option', 'h', 'm')
        else:
            pyautogui.hotkey('ctrl', 'alt', 'd')
        return "✅ **All windows minimized!**"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("switch_window", return_direct=True)
def switch_window() -> str:
    """Switch to next window (Alt+Tab)."""
    try:
        system = platform.system()
        if system == "Darwin":
            pyautogui.hotkey('command', 'tab')
        else:
            pyautogui.hotkey('alt', 'tab')
        return "✅ **Switched to next window!**"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("lock_computer", return_direct=True)
def lock_computer() -> str:
    """Lock the computer."""
    try:
        system = platform.system()
        if system == "Windows":
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
        elif system == "Darwin":
            subprocess.run(['pmset', 'displaysleepnow'])
        else:
            subprocess.run(['xdg-screensaver', 'lock'])
        return "🔒 **Computer locked!**"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("get_screen_size", return_direct=True)
def get_screen_size() -> str:
    """Get screen resolution."""
    try:
        width, height = pyautogui.size()
        return f"🖥️ **Screen Resolution:** {width}x{height}px"
    except Exception as e:
        return f"❌ Failed: {str(e)}"
