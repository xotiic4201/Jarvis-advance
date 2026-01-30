"""
Enhanced Screenshot Tool for Jarvis AI
"""

from datetime import datetime
from langchain.tools import tool
import os
import mss
import mss.tools
from PIL import Image, ImageDraw, ImageFont
import pyautogui


@tool("capture_screenshot", return_direct=True)
def take_screenshot() -> str:
    """
    Captures the current screen and saves it to 'screenshot.png' in the current directory.
    
    Use this tool when the user says:
    - "Take a screenshot"
    - "Capture the screen"
    - "Save a screenshot"
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=image_path)

        file_size = os.path.getsize(image_path)
        return f"✅ **Screenshot captured!**\n" \
               f"📸 **File:** {os.path.basename(image_path)}\n" \
               f"📁 **Location:** {image_path}\n" \
               f"💾 **Size:** {file_size:,} bytes\n" \
               f"📏 **Resolution:** {screenshot.width}x{screenshot.height}"
    except Exception as e:
        return f"❌ Failed to capture screenshot: {str(e)}"


@tool("screenshot_all_monitors", return_direct=True)
def screenshot_all_monitors() -> str:
    """
    Capture all monitors at once.
    
    Examples:
    - "Screenshot all monitors"
    - "Capture all screens"
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with mss.mss() as sct:
            # Monitor 0 captures all monitors
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)
            image_path = os.path.join(screenshots_dir, f"all_monitors_{timestamp}.png")
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=image_path)

        file_size = os.path.getsize(image_path)
        return f"✅ **All monitors captured!**\n" \
               f"📸 **File:** {os.path.basename(image_path)}\n" \
               f"📁 **Location:** {image_path}\n" \
               f"💾 **Size:** {file_size:,} bytes"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("annotate_screenshot", return_direct=True)
def annotate_screenshot(text: str = None) -> str:
    """
    Take screenshot with annotation/timestamp.
    
    Examples:
    - "Take annotated screenshot"
    - "Screenshot with timestamp"
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(screenshots_dir, f"temp_{timestamp}.png")
        final_path = os.path.join(screenshots_dir, f"annotated_{timestamp}.png")

        # Capture screenshot
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=temp_path)
        
        # Add annotation
        img = Image.open(temp_path)
        draw = ImageDraw.Draw(img)
        
        # Add timestamp
        annotation = text or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simple text annotation (no custom font needed)
        position = (10, 10)
        draw.text(position, annotation, fill='red')
        
        img.save(final_path)
        os.remove(temp_path)
        
        file_size = os.path.getsize(final_path)
        return f"✅ **Annotated screenshot captured!**\n" \
               f"📸 **File:** {os.path.basename(final_path)}\n" \
               f"📝 **Annotation:** {annotation}\n" \
               f"📁 **Location:** {final_path}\n" \
               f"💾 **Size:** {file_size:,} bytes"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("screenshot_window", return_direct=True)
def screenshot_window() -> str:
    """
    Screenshot only the active window.
    
    Examples:
    - "Screenshot this window"
    - "Capture active window"
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(screenshots_dir, f"window_{timestamp}.png")
        
        # Get active window using pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(image_path)
        
        file_size = os.path.getsize(image_path)
        return f"✅ **Window screenshot captured!**\n" \
               f"📸 **File:** {os.path.basename(image_path)}\n" \
               f"📁 **Location:** {image_path}\n" \
               f"💾 **Size:** {file_size:,} bytes"
    except Exception as e:
        return f"❌ Failed: {str(e)}"
