import subprocess
import platform

def ping_host(host, timeout=3):
    """Testa se um host está respondendo com timeout."""
    try:
        # Comando ping compatível com Windows e Linux
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', str(timeout * 1000), host]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return {"status": True, "error": None}
        else:
            return {"status": False, "error": "host_unreachable"}
    except subprocess.TimeoutExpired:
        return {"status": False, "error": "timeout"}
    except OSError as e:
        return {"status": False, "error": f"system_error: {str(e)}"}
    except Exception as e:
        return {"status": False, "error": f"unexpected_error: {str(e)}"}

def ping_gateway(host="192.168.1.1"):
    """Testa se o gateway está respondendo."""
    return ping_host(host)

def ping_dns(host="8.8.8.8"):
    """Testa se o DNS (8.8.8.8) está respondendo."""
    return ping_host(host)