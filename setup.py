#!/usr/bin/env python3
"""
JARVIS AI - Automated Setup Script
This script helps you set up JARVIS AI with minimal effort
"""

import os
import sys
import subprocess
import platform
import shutil

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(number, text):
    print(f"\n🔹 Step {number}: {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install Python requirements"""
    print_step(1, "Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print_success("All Python packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install Python packages")
        return False

def check_ollama():
    """Check if Ollama is installed"""
    print_step(2, "Checking for Ollama...")
    if shutil.which("ollama"):
        print_success("Ollama is installed")
        return True
    else:
        print_warning("Ollama not found")
        print("\n📥 Please install Ollama:")
        print("   Visit: https://ollama.ai")
        print("   Download and install, then run: ollama pull qwen2.5:7b")
        return False

def check_ollama_model():
    """Check if required Ollama model is downloaded"""
    print_step(3, "Checking for Ollama model...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "qwen2.5:7b" in result.stdout or "qwen2.5" in result.stdout:
            print_success("Ollama model qwen2.5:7b is ready")
            return True
        else:
            print_warning("Model not found. Downloading...")
            subprocess.check_call(["ollama", "pull", "qwen2.5:7b"])
            print_success("Model downloaded successfully")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Could not verify Ollama model")
        print("   Run: ollama pull qwen2.5:7b")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print_step(4, "Checking for Tesseract OCR...")
    if shutil.which("tesseract"):
        print_success("Tesseract is installed")
        return True
    else:
        print_warning("Tesseract not found")
        system = platform.system()
        if system == "Windows":
            print("\n📥 Windows: Download from")
            print("   https://github.com/UB-Mannheim/tesseract/wiki")
        elif system == "Darwin":
            print("\n📥 macOS: Install with Homebrew")
            print("   brew install tesseract")
        else:
            print("\n📥 Linux: Install with package manager")
            print("   sudo apt-get install tesseract-ocr")
        return False

def create_directories():
    """Create necessary directories"""
    print_step(5, "Creating directories...")
    directories = [
        "tools",
        "Jarvis_Notes",
        "screenshots",
        "recordings",
        "pictures",
        "extracted_text",
        "tts_files",
        "macros"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print_success("All directories created")
    return True

def check_microphone():
    """Check if microphone is available"""
    print_step(6, "Checking microphone...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mics = sr.Microphone.list_microphone_names()
        if mics:
            print_success(f"Found {len(mics)} microphone(s)")
            print(f"   Default: {mics[0] if mics else 'None'}")
            return True
        else:
            print_warning("No microphones detected")
            return False
    except:
        print_warning("Could not check microphone")
        return False

def test_imports():
    """Test if key imports work"""
    print_step(7, "Testing imports...")
    
    imports = [
        ("langchain", "LangChain"),
        ("PyQt6", "PyQt6"),
        ("pyttsx3", "Text-to-Speech"),
        ("speech_recognition", "Speech Recognition"),
        ("pyautogui", "PyAutoGUI"),
        ("psutil", "PSUtil"),
        ("mss", "MSS"),
        ("PIL", "Pillow")
    ]
    
    all_good = True
    for module, name in imports:
        try:
            __import__(module)
            print_success(f"{name} imported successfully")
        except ImportError:
            print_error(f"{name} import failed")
            all_good = False
    
    return all_good

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_step(8, "Creating environment file...")
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# JARVIS AI Environment Configuration\n\n")
            f.write("# Ollama Configuration\n")
            f.write("OLLAMA_HOST=http://localhost:11434\n\n")
            f.write("# Assistant Configuration\n")
            f.write("TRIGGER_WORD=jarvis\n")
            f.write("CONVERSATION_TIMEOUT=30\n")
        print_success(".env file created")
    else:
        print_success(".env file already exists")
    return True

def main():
    """Main setup function"""
    print_header("JARVIS AI - Automated Setup")
    print("This script will help you set up JARVIS AI\n")
    
    system_info = platform.system()
    print(f"🖥️  Detected OS: {system_info}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Run all checks
    checks = []
    
    checks.append(("Python Version", check_python_version()))
    
    if not checks[0][1]:
        print_error("Setup cannot continue without Python 3.8+")
        return
    
    checks.append(("Python Packages", install_requirements()))
    checks.append(("Ollama", check_ollama()))
    checks.append(("Ollama Model", check_ollama_model()))
    checks.append(("Tesseract OCR", check_tesseract()))
    checks.append(("Directories", create_directories()))
    checks.append(("Microphone", check_microphone()))
    checks.append(("Imports", test_imports()))
    checks.append(("Environment", create_env_file()))
    
    # Summary
    print_header("Setup Summary")
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    for check_name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
    
    print(f"\n📊 Status: {passed}/{total} checks passed")
    
    if passed == total:
        print_header("🎉 Setup Complete!")
        print("All components are ready to go!\n")
        print("🚀 To start JARVIS, run:")
        print("   python main.py\n")
        print("💡 First time? Check out QUICKSTART.md\n")
    elif passed >= total - 2:
        print_header("⚠️  Setup Mostly Complete")
        print("JARVIS should work, but some features may be limited.\n")
        print("🚀 Try running:")
        print("   python main.py\n")
        print("📋 Review failed checks above and install missing components.\n")
    else:
        print_header("❌ Setup Incomplete")
        print("Several components are missing.\n")
        print("📋 Please install the missing components listed above.")
        print("💡 Check README.md for detailed instructions.\n")
    
    print("="*70)
    print("\n📚 Documentation:")
    print("   README.md - Full documentation")
    print("   QUICKSTART.md - Quick start guide")
    print("\n🆘 Need help? Check the troubleshooting section in README.md\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup error: {e}")
        sys.exit(1)
