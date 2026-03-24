import os

def ping_gateway(host="192.168.1.1"):
    """Testa se o gateway está respondendo."""
    response = os.system(f"ping -c 1 {host} > /dev/null 2>&1")
    return response == 0

def ping_dns(host="8.8.8.8"):
    """Testa se o DNS (8.8.8.8) está respondendo."""
    response = os.system(f"ping -c 1 {host} > /dev/null 2>&1")
    return response == 0