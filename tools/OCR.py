"""
Enhanced OCR (Optical Character Recognition) Tool for Jarvis AI
"""

from langchain.tools import tool
from PIL import Image
import pytesseract
import os
from datetime import datetime
import glob


@tool("read_latest_screenshot", return_direct=True)
def read_text_from_latest_image() -> str:
    """
    Reads and extracts text from the most recent screenshot.
    
    Use this tool when the user says:
    - "Read the screen"
    - "What does the screenshot say?"
    - "Extract text from the image"
    """
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        
        if not os.path.exists(screenshots_dir):
            return "❌ **Screenshots directory not found.** Take a screenshot first!"
        
        # Find the most recent screenshot
        screenshots = glob.glob(os.path.join(screenshots_dir, "*.png"))
        
        if not screenshots:
            return "❌ **No screenshots found.** Take a screenshot first!"
        
        latest_screenshot = max(screenshots, key=os.path.getmtime)
        
        img = Image.open(latest_screenshot)
        text = pytesseract.image_to_string(img)
        
        if not text.strip():
            return f"📄 **No readable text found** in {os.path.basename(latest_screenshot)}"
        
        return f"📖 **Text extracted from {os.path.basename(latest_screenshot)}:**\n" \
               f"{'═' * 60}\n{text.strip()}\n{'═' * 60}"
    
    except Exception as e:
        return f"❌ Failed to extract text: {str(e)}\n💡 Make sure tesseract is installed"


@tool("read_image_file", return_direct=True)
def read_text_from_image_file(image_path: str) -> str:
    """
    Extract text from any image file.
    
    Examples:
    - "Read text from document.png"
    - "Extract text from the image"
    """
    try:
        image_path = os.path.expanduser(image_path)
        
        if not os.path.exists(image_path):
            return f"❌ **Image not found:** {image_path}"
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        if not text.strip():
            return f"📄 **No readable text found** in {os.path.basename(image_path)}"
        
        # Save extracted text to file
        text_dir = os.path.join(os.getcwd(), "extracted_text")
        os.makedirs(text_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_file = os.path.join(text_dir, f"extracted_{timestamp}.txt")
        
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return f"📖 **Text extracted from {os.path.basename(image_path)}:**\n" \
               f"{'═' * 60}\n{text.strip()[:500]}{'...' if len(text) > 500 else ''}\n{'═' * 60}\n" \
               f"💾 **Full text saved to:** {text_file}"
    
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("ocr_to_file", return_direct=True)
def ocr_to_file(image_path: str, output_file: str = None) -> str:
    """
    Extract text from image and save to text file.
    
    Examples:
    - "OCR this image and save to file"
    - "Extract text to document.txt"
    """
    try:
        image_path = os.path.expanduser(image_path)
        
        if not os.path.exists(image_path):
            return f"❌ **Image not found:** {image_path}"
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        if not text.strip():
            return f"📄 **No readable text found** in {os.path.basename(image_path)}"
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ocr_output_{timestamp}.txt"
        
        if not output_file.endswith('.txt'):
            output_file += '.txt'
        
        output_path = os.path.join(os.getcwd(), output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"OCR Extraction from: {image_path}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(text)
        
        word_count = len(text.split())
        return f"✅ **OCR completed!**\n" \
               f"📄 **Source:** {os.path.basename(image_path)}\n" \
               f"💾 **Saved to:** {output_path}\n" \
               f"📊 **Words extracted:** {word_count}"
    
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("read_screen_area", return_direct=True)
def read_screen_area(x: int, y: int, width: int, height: int) -> str:
    """
    Take screenshot of specific area and extract text.
    
    Examples:
    - "Read text from area 100,100 with size 500x300"
    """
    try:
        import pyautogui
        
        # Capture specific area
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Extract text
        text = pytesseract.image_to_string(screenshot)
        
        if not text.strip():
            return f"📄 **No readable text found** in the specified area"
        
        return f"📖 **Text from region ({x},{y}) - {width}x{height}:**\n" \
               f"{'═' * 60}\n{text.strip()}\n{'═' * 60}"
    
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("detect_language", return_direct=True)
def detect_text_language(image_path: str) -> str:
    """
    Detect language in image text.
    
    Examples:
    - "What language is in this image?"
    - "Detect language in screenshot"
    """
    try:
        image_path = os.path.expanduser(image_path)
        
        if not os.path.exists(image_path):
            return f"❌ **Image not found:** {image_path}"
        
        img = Image.open(image_path)
        
        # Get OCR data with language info
        data = pytesseract.image_to_osd(img)
        
        return f"🌍 **Language Detection Results:**\n" \
               f"{'═' * 60}\n{data}\n{'═' * 60}"
    
    except Exception as e:
        return f"❌ Failed: {str(e)}\n💡 This feature requires tesseract with language support"
