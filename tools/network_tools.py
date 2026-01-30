"""
Advanced Network and System Monitoring Tools for Jarvis AI
"""

from langchain.tools import tool
import platform
import subprocess
import socket
import psutil
import requests
from datetime import datetime
import json


@tool("get_network_info", return_direct=True)
def get_network_info() -> str:
    """
    Get network information including IP addresses and connections.
    
    Examples:
    - "Show my network info"
    - "What's my IP address?"
    """
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Get public IP
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=3).text
        except:
            public_ip = "Unable to fetch"
        
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        
        result = "🌐 **Network Information:**\n"
        result += "═" * 60 + "\n"
        result += f"🖥️ **Hostname:** {hostname}\n"
        result += f"🏠 **Local IP:** {local_ip}\n"
        result += f"🌍 **Public IP:** {public_ip}\n\n"
        result += "**Network Interfaces:**\n"
        
        for interface_name, addresses in list(interfaces.items())[:5]:
            result += f"\n📡 **{interface_name}:**\n"
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    result += f"   IPv4: {addr.address}\n"
                elif addr.family == socket.AF_INET6:
                    result += f"   IPv6: {addr.address[:30]}...\n"
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("network_speed_test", return_direct=True)
def network_speed_test() -> str:
    """
    Test network connectivity and latency.
    
    Examples:
    - "Test my network speed"
    - "Check network performance"
    """
    try:
        # Ping test
        def ping_host(host):
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '4', host]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if "time=" in result.stdout or "Average" in result.stdout:
                    return "✅ Connected"
                return "❌ Failed"
            except:
                return "❌ Timeout"
        
        hosts = {
            "Google": "8.8.8.8",
            "Cloudflare": "1.1.1.1",
        }
        
        result = "⚡ **Network Speed Test:**\n"
        result += "═" * 60 + "\n"
        
        for name, host in hosts.items():
            status = ping_host(host)
            result += f"📡 **{name} ({host}):** {status}\n"
        
        # Network stats
        net_io = psutil.net_io_counters()
        result += f"\n📊 **Network Statistics:**\n"
        result += f"📤 **Sent:** {net_io.bytes_sent / (1024**2):.2f} MB\n"
        result += f"📥 **Received:** {net_io.bytes_recv / (1024**2):.2f} MB\n"
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("list_connections", return_direct=True)
def list_connections() -> str:
    """
    List active network connections.
    
    Examples:
    - "Show active connections"
    - "What's connected to my computer?"
    """
    try:
        connections = psutil.net_connections(kind='inet')
        
        result = "🔌 **Active Network Connections:**\n"
        result += "═" * 60 + "\n"
        
        count = 0
        for conn in connections[:15]:
            if conn.status == 'ESTABLISHED':
                local = f"{conn.laddr.ip}:{conn.laddr.port}"
                remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                result += f"📡 **Connection {count+1}:**\n"
                result += f"   Local: {local}\n"
                result += f"   Remote: {remote}\n"
                result += f"   Status: {conn.status}\n"
                result += "   " + "─" * 55 + "\n"
                count += 1
        
        if count == 0:
            result += "No established connections found.\n"
        
        result += f"\n📊 **Total connections:** {len(connections)}"
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("monitor_system_resources", return_direct=True)
def monitor_system_resources() -> str:
    """
    Monitor CPU, memory, and disk usage in real-time.
    
    Examples:
    - "Monitor system resources"
    - "Check system performance"
    """
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Processes
        process_count = len(psutil.pids())
        
        result = "📊 **System Resource Monitor:**\n"
        result += "═" * 60 + "\n"
        
        result += "🔥 **CPU:**\n"
        result += f"   Usage: {cpu_percent}%\n"
        result += f"   Cores: {cpu_count}\n"
        if cpu_freq:
            result += f"   Frequency: {cpu_freq.current:.0f} MHz\n"
        
        result += "\n💾 **Memory:**\n"
        result += f"   Total: {memory.total / (1024**3):.1f} GB\n"
        result += f"   Used: {memory.used / (1024**3):.1f} GB ({memory.percent}%)\n"
        result += f"   Available: {memory.available / (1024**3):.1f} GB\n"
        
        result += "\n💿 **Disk:**\n"
        result += f"   Total: {disk.total / (1024**3):.1f} GB\n"
        result += f"   Used: {disk.used / (1024**3):.1f} GB ({disk.percent}%)\n"
        result += f"   Free: {disk.free / (1024**3):.1f} GB\n"
        
        if disk_io:
            result += f"   Read: {disk_io.read_bytes / (1024**2):.1f} MB\n"
            result += f"   Write: {disk_io.write_bytes / (1024**2):.1f} MB\n"
        
        result += f"\n🔧 **Processes:** {process_count} running\n"
        
        # Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                result += "\n🌡️ **Temperature:**\n"
                for name, entries in list(temps.items())[:2]:
                    for entry in entries[:1]:
                        result += f"   {name}: {entry.current}°C\n"
        except:
            pass
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("list_processes", return_direct=True)
def list_processes(sort_by: str = "memory") -> str:
    """
    List running processes sorted by CPU or memory usage.
    
    Examples:
    - "Show top processes"
    - "List processes by memory"
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        
        # Sort processes
        if sort_by.lower() == "cpu":
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        
        result = f"🔧 **Top Processes (by {sort_by}):**\n"
        result += "═" * 60 + "\n"
        
        for i, proc in enumerate(processes[:15], 1):
            result += f"{i}. **{proc['name']}** (PID: {proc['pid']})\n"
            result += f"   CPU: {proc.get('cpu_percent', 0):.1f}% | "
            result += f"Memory: {proc.get('memory_percent', 0):.1f}%\n"
            result += "   " + "─" * 55 + "\n"
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("kill_process", return_direct=True)
def kill_process(pid_or_name: str) -> str:
    """
    Kill a process by PID or name.
    
    Examples:
    - "Kill process 1234"
    - "Terminate chrome"
    """
    try:
        killed_count = 0
        
        # Try as PID first
        try:
            pid = int(pid_or_name)
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            killed_count = 1
            return f"✅ **Process terminated!**\n🔧 **Name:** {proc_name}\n🆔 **PID:** {pid}"
        except ValueError:
            # It's a process name
            for proc in psutil.process_iter(['pid', 'name']):
                if pid_or_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed_count += 1
            
            if killed_count > 0:
                return f"✅ **Terminated {killed_count} process(es) matching:** {pid_or_name}"
            else:
                return f"❌ **No processes found matching:** {pid_or_name}"
        
    except Exception as e:
        return f"❌ Failed: {str(e)}"


@tool("get_battery_status", return_direct=True)
def get_battery_status() -> str:
    """
    Get battery information (for laptops).
    
    Examples:
    - "Check battery"
    - "Battery status"
    """
    try:
        battery = psutil.sensors_battery()
        
        if battery is None:
            return "🔌 **No battery detected** (Desktop or AC powered)"
        
        percent = battery.percent
        plugged = battery.power_plugged
        time_left = battery.secsleft
        
        result = "🔋 **Battery Status:**\n"
        result += "═" * 60 + "\n"
        result += f"⚡ **Charge:** {percent}%\n"
        result += f"🔌 **Plugged in:** {'Yes' if plugged else 'No'}\n"
        
        if time_left != psutil.POWER_TIME_UNLIMITED and time_left != psutil.POWER_TIME_UNKNOWN:
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            result += f"⏱️ **Time remaining:** {hours}h {minutes}m\n"
        
        # Battery icon based on percentage
        if percent > 80:
            icon = "🟢"
        elif percent > 50:
            icon = "🟡"
        elif percent > 20:
            icon = "🟠"
        else:
            icon = "🔴"
        
        result += f"\n{icon} **Status:** "
        if plugged:
            result += "Charging" if percent < 100 else "Fully Charged"
        else:
            result += "Discharging"
        
        return result
    except Exception as e:
        return f"❌ Failed: {str(e)}"
