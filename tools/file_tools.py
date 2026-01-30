"""
Advanced File Management Tools for Jarvis AI
"""

from langchain.tools import tool
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import zipfile


@tool("search_files", return_direct=True)
def search_files(pattern: str, directory: str = None, recursive: bool = True) -> str:
    """
    Search for files matching a pattern.
    
    Examples:
    - "Find all Python files"
    - "Search for documents"
    """
    try:
        if directory is None:
            directory = os.getcwd()
        directory = os.path.expanduser(directory)
        matches = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if pattern.lower() in filename.lower() or pattern == "*":
                        full_path = os.path.join(root, filename)
                        size = os.path.getsize(full_path)
                        modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                        matches.append({
                            'path': full_path,
                            'name': filename,
                            'size': size,
                            'modified': modified.strftime('%Y-%m-%d %H:%M')
                        })
        else:
            for filename in os.listdir(directory):
                if pattern.lower() in filename.lower():
                    full_path = os.path.join(directory, filename)
                    if os.path.isfile(full_path):
                        size = os.path.getsize(full_path)
                        modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                        matches.append({
                            'path': full_path,
                            'name': filename,
                            'size': size,
                            'modified': modified.strftime('%Y-%m-%d %H:%M')
                        })
        
        if not matches:
            return f"❌ **No files found matching:** {pattern}"
        
        result = f"🔍 **Found {len(matches)} file(s):**\n" + "═" * 60 + "\n"
        for i, match in enumerate(matches[:20], 1):
            result += f"{i}. **{match['name']}**\n"
            result += f"   📁 {match['path']}\n"
            result += f"   📏 {match['size']:,} bytes | 📅 {match['modified']}\n"
            result += "   " + "─" * 55 + "\n"
        
        if len(matches) > 20:
            result += f"\n... and {len(matches) - 20} more files"
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("organize_files", return_direct=True)
def organize_files(directory: str) -> str:
    """
    Organize files in a directory by extension.
    
    Examples:
    - "Organize my downloads"
    - "Sort files by type"
    """
    try:
        directory = os.path.expanduser(directory)
        if not os.path.exists(directory):
            return f"❌ Directory not found: {directory}"
        
        files_moved = 0
        folders_created = set()
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1][1:].lower() or 'no_extension'
                ext_folder = os.path.join(directory, ext.upper())
                
                if not os.path.exists(ext_folder):
                    os.makedirs(ext_folder)
                    folders_created.add(ext.upper())
                
                new_path = os.path.join(ext_folder, filename)
                if not os.path.exists(new_path):
                    shutil.move(filepath, new_path)
                    files_moved += 1
        
        result = "✅ **Files organized!**\n"
        result += f"📦 **Files moved:** {files_moved}\n"
        result += f"📁 **Folders created:** {len(folders_created)}\n"
        if folders_created:
            result += f"🗂️ **Types:** {', '.join(sorted(folders_created))}"
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("create_zip", return_direct=True)
def create_zip(source_dir: str, output_name: str = None) -> str:
    """
    Create a ZIP archive of a directory.
    
    Examples:
    - "Zip the folder Documents"
    - "Create archive of my project"
    """
    try:
        source_dir = os.path.expanduser(source_dir)
        if not os.path.exists(source_dir):
            return f"❌ Directory not found: {source_dir}"
        
        if output_name is None:
            output_name = f"{os.path.basename(source_dir)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        if not output_name.endswith('.zip'):
            output_name += '.zip'
        
        output_path = os.path.join(os.path.dirname(source_dir), output_name)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        size = os.path.getsize(output_path)
        return f"✅ **ZIP created!**\n📦 **File:** {output_name}\n📁 **Location:** {output_path}\n📏 **Size:** {size:,} bytes"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("extract_zip", return_direct=True)
def extract_zip(zip_path: str, extract_to: str = None) -> str:
    """
    Extract a ZIP archive.
    
    Examples:
    - "Extract archive.zip"
    - "Unzip the file"
    """
    try:
        zip_path = os.path.expanduser(zip_path)
        if not os.path.exists(zip_path):
            return f"❌ ZIP file not found: {zip_path}"
        
        if extract_to is None:
            extract_to = os.path.dirname(zip_path)
        else:
            extract_to = os.path.expanduser(extract_to)
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_to)
            file_count = len(zipf.namelist())
        
        return f"✅ **ZIP extracted!**\n📂 **Files extracted:** {file_count}\n📁 **Location:** {extract_to}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("delete_file", return_direct=True)
def delete_file(filepath: str) -> str:
    """
    Delete a file.
    
    Examples:
    - "Delete file temp.txt"
    - "Remove the file"
    """
    try:
        filepath = os.path.expanduser(filepath)
        if not os.path.exists(filepath):
            return f"❌ File not found: {filepath}"
        
        os.remove(filepath)
        return f"✅ **File deleted:** {os.path.basename(filepath)}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("rename_file", return_direct=True)
def rename_file(old_path: str, new_name: str) -> str:
    """
    Rename a file.
    
    Examples:
    - "Rename report.txt to final_report.txt"
    """
    try:
        old_path = os.path.expanduser(old_path)
        if not os.path.exists(old_path):
            return f"❌ File not found: {old_path}"
        
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)
        
        os.rename(old_path, new_path)
        return f"✅ **File renamed!**\n📄 **From:** {os.path.basename(old_path)}\n📄 **To:** {new_name}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("copy_file", return_direct=True)
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file to another location.
    
    Examples:
    - "Copy file.txt to Documents"
    """
    try:
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)
        
        if not os.path.exists(source):
            return f"❌ Source file not found: {source}"
        
        if os.path.isdir(destination):
            destination = os.path.join(destination, os.path.basename(source))
        
        shutil.copy2(source, destination)
        return f"✅ **File copied!**\n📄 **From:** {source}\n📁 **To:** {destination}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("get_file_info", return_direct=True)
def get_file_info(filepath: str) -> str:
    """
    Get detailed information about a file.
    
    Examples:
    - "Get info about document.pdf"
    - "Tell me about this file"
    """
    try:
        filepath = os.path.expanduser(filepath)
        if not os.path.exists(filepath):
            return f"❌ File not found: {filepath}"
        
        stats = os.stat(filepath)
        size = stats.st_size
        created = datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.fromtimestamp(stats.st_mtime)
        accessed = datetime.fromtimestamp(stats.st_atime)
        
        result = f"📄 **File Information:**\n"
        result += "═" * 60 + "\n"
        result += f"📝 **Name:** {os.path.basename(filepath)}\n"
        result += f"📁 **Path:** {filepath}\n"
        result += f"📏 **Size:** {size:,} bytes ({size/(1024**2):.2f} MB)\n"
        result += f"📅 **Created:** {created.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"✏️ **Modified:** {modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"👁️ **Accessed:** {accessed.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"🔧 **Extension:** {os.path.splitext(filepath)[1]}\n"
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"
