import socket

def test_dns(host="google.com"):
    """Testa resolução de DNS."""
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False
    except Exception:
        return False
