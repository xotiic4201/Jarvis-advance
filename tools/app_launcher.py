"""
Improved Application Launcher for JARVIS
Scans Windows PC for installed applications and provides reliable open/close functionality
"""

from langchain.tools import tool
import os
import subprocess
import platform
import psutil
import json
import time
import logging
from pathlib import Path

APP_CACHE_FILE = "installed_apps_cache.json"

def scan_installed_applications():
    """Scan Windows for installed applications"""
    apps_dict = {}
    system = platform.system()
    
    if system == "Windows":
        print("🔍 Scanning PC for installed applications...")
        
        # Common installation directories
        search_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expanduser("~\\Desktop")
        ]
        
        # Scan directories for executables
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Skip deep nesting for performance
                    depth = root[len(search_dir):].count(os.sep)
                    if depth > 3:
                        continue
                        
                    for file in files:
                        if file.lower().endswith(('.exe', '.lnk')):
                            app_name = os.path.splitext(file)[0].lower()
                            full_path = os.path.join(root, file)
                            
                            # Store the path for this app (prefer shorter paths)
                            if app_name not in apps_dict or len(full_path) < len(apps_dict[app_name]):
                                apps_dict[app_name] = full_path
            except (PermissionError, OSError):
                continue
        
        # Check Windows Registry for installed apps
        try:
            import winreg
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
            ]
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    i = 0
                    while True:
                        try:
                            app_key = winreg.EnumKey(key, i)
                            app_name = os.path.splitext(app_key)[0].lower()
                            
                            try:
                                subkey = winreg.OpenKey(key, app_key)
                                path, _ = winreg.QueryValueEx(subkey, "")
                                if os.path.exists(path):
                                    apps_dict[app_name] = path
                                winreg.CloseKey(subkey)
                            except:
                                pass
                            
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
                except:
                    pass
        except:
            pass
        
        print(f"✅ Found {len(apps_dict)} applications")
    
    # Save cache
    try:
        with open(APP_CACHE_FILE, 'w') as f:
            json.dump(apps_dict, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save app cache: {e}")
    
    return apps_dict

def load_app_cache():
    """Load cached application paths"""
    # If cache doesn't exist or is old, rescan
    if not os.path.exists(APP_CACHE_FILE):
        return scan_installed_applications()
    
    # Check if cache is older than 24 hours
    cache_age = time.time() - os.path.getmtime(APP_CACHE_FILE)
    if cache_age > 86400:  # 24 hours
        return scan_installed_applications()
    
    # Load existing cache
    try:
        with open(APP_CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return scan_installed_applications()


@tool("open_app", return_direct=True)
def open_app(app_name: str) -> str:
    """
    Open any application installed on the PC.
    
    Examples:
    - "open chrome"
    - "open discord"
    - "open steam"
    - "open notepad"
    - "launch spotify"
    """
    try:
        app_name_lower = app_name.lower()
        
        # Load app cache
        apps = load_app_cache()
        
        # Try to find the app
        app_path = None
        
        # Direct match
        if app_name_lower in apps:
            app_path = apps[app_name_lower]
        else:
            # Fuzzy match - check if app name contains the search term
            for name, path in apps.items():
                if app_name_lower in name or name in app_name_lower:
                    app_path = path
                    break
        
        if app_path:
            # Launch the app
            if app_path.endswith('.lnk'):
                # For shortcuts, use os.startfile
                os.startfile(app_path)
            else:
                # For executables, use subprocess
                subprocess.Popen([app_path], shell=True)
            
            return f"✅ **{app_name.title()} opened successfully!**"
        else:
            # Try generic Windows opening
            subprocess.Popen(app_name, shell=True)
            return f"✅ **Attempting to open {app_name}...**"
    
    except Exception as e:
        return f"❌ **Failed to open {app_name}:** {str(e)}\n💡 Try: 'rescan apps' to update the application database"


@tool("close_app", return_direct=True)
def close_app(app_name: str) -> str:
    """
    Close any running application.
    
    Examples:
    - "close chrome"
    - "close discord"
    - "terminate spotify"
    - "kill steam"
    """
    try:
        app_name_lower = app_name.lower()
        closed_count = 0
        closed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                # Check if the app name is in the process name
                if app_name_lower in proc_name or proc_name.startswith(app_name_lower):
                    proc.terminate()
                    closed_processes.append(proc.info['name'])
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return f"✅ **Closed {app_name.title()}!**\n📊 **Processes terminated:** {closed_count}\n🔻 {', '.join(set(closed_processes))}"
        else:
            return f"⚠️ **{app_name.title()} is not running.**"
    
    except Exception as e:
        return f"❌ **Error closing {app_name}:** {str(e)}"


@tool("rescan_apps", return_direct=True)
def rescan_apps() -> str:
    """
    Rescan the PC for installed applications to update the database.
    
    Use this when:
    - A new application was installed
    - An app can't be found
    - First time using JARVIS
    """
    try:
        apps = scan_installed_applications()
        return f"✅ **PC scan complete!**\n📦 **Found {len(apps)} applications**\n💡 You can now open/close these apps by name"
    except Exception as e:
        return f"❌ **Scan failed:** {str(e)}"


@tool("list_installed_apps", return_direct=True)
def list_installed_apps(search: str = "") -> str:
    """
    List all installed applications (or search for specific ones).
    
    Examples:
    - "list installed apps"
    - "show all programs"
    - "find apps with 'game' in the name"
    """
    try:
        apps = load_app_cache()
        
        if search:
            search_lower = search.lower()
            filtered_apps = {name: path for name, path in apps.items() if search_lower in name}
        else:
            filtered_apps = apps
        
        if not filtered_apps:
            return f"❌ **No applications found matching '{search}'**"
        
        # Limit to 50 apps for readability
        apps_list = list(filtered_apps.keys())[:50]
        
        result = f"📦 **Installed Applications ({len(filtered_apps)} total):**\n"
        result += "═" * 60 + "\n"
        
        for i, app_name in enumerate(sorted(apps_list), 1):
            result += f"{i}. {app_name.title()}\n"
        
        if len(filtered_apps) > 50:
            result += f"\n... and {len(filtered_apps) - 50} more applications"
        
        result += f"\n\n💡 **Usage:** Say 'open [app name]' to launch any app"
        
        return result
    
    except Exception as e:
        return f"❌ **Failed to list apps:** {str(e)}"
