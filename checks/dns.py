import socket

def test_dns(host="google.com"):
    """Testa resolução de DNS."""
    try:
        socket.gethostbyname(host)
        return {"status": True, "error": None}
    except socket.gaierror:
        return {"status": False, "error": "dns_resolution_failed"}
    except socket.timeout:
        return {"status": False, "error": "timeout"}
    except OSError as e:
        return {"status": False, "error": f"network_error: {str(e)}"}
